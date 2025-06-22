#!/bin/bash

# Script to properly set up and run rapid boiling simulation
# This script handles the alpha.water field correctly

echo "=== Rapid Boiling Simulation Setup ==="
echo ""

# Source OpenFOAM environment
echo "Sourcing OpenFOAM environment..."
source /opt/openfoam11/etc/bashrc

# Clean previous results
echo "Cleaning previous simulation results..."
./Allclean

# Generate mesh
echo "Generating mesh..."
blockMesh
if [ $? -ne 0 ]; then
    echo "Error: Mesh generation failed!"
    exit 1
fi

echo "Mesh generated successfully with $(grep -o 'cells:.*' log.blockMesh | tail -1) cells"

# Set initial water level using setFields
echo "Setting initial water level..."
setFields
if [ $? -ne 0 ]; then
    echo "Error: setFields failed!"
    exit 1
fi

# Check if alpha.water was corrupted by setFields and fix it
echo "Checking alpha.water field..."
line_count=$(wc -l < 0/alpha.water)
if [ $line_count -gt 100 ]; then
    echo "Warning: alpha.water field was corrupted by setFields (${line_count} lines)"
    echo "Fixing alpha.water field..."
    
    # Backup the field data
    cp 0/alpha.water 0/alpha.water.backup
    
    # Extract the internal field data (between the parentheses)
    echo "Extracting field data..."
    
    # Create a new alpha.water file with proper boundary conditions
    cat > 0/alpha.water << 'EOF'
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  11
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      alpha.water;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 0 0 0 0];

EOF

    # Extract and add the internal field from backup
    echo "internalField   nonuniform List<scalar>" >> 0/alpha.water
    
    # Get the number and data from backup file
    sed -n '21,/^);$/p' 0/alpha.water.backup >> 0/alpha.water
    
    # Add boundary conditions
    cat >> 0/alpha.water << 'EOF'

boundaryField
{
    bottom
    {
        type            zeroGradient;
    }
    
    walls
    {
        type            constantAlphaContactAngle;
        theta0          90;
        limit           gradient;
        value           uniform 0;
    }
    
    top
    {
        type            inletOutlet;
        inletValue      uniform 0;
        value           uniform 0;
    }
}

// ************************************************************************* //
EOF

    echo "alpha.water field fixed successfully"
else
    echo "alpha.water field is OK (${line_count} lines)"
fi

# Verify all fields are ready
echo ""
echo "Verifying initial conditions..."
for field in T U p_rgh alpha.water k epsilon; do
    if [ -f "0/$field" ]; then
        lines=$(wc -l < "0/$field")
        echo "  $field: $lines lines - OK"
    else
        echo "  $field: MISSING!"
        exit 1
    fi
done

echo ""
echo "=== Simulation Parameters ==="
echo "Initial temperature: 90°C (363.15 K)"
echo "Heat flux: 150,000 K/m"
echo "End time: 5 seconds"
echo "Time step: 0.01 seconds (adaptive)"
echo "Output frequency: Every 0.05 seconds"
echo ""

# Run the simulation
echo "Starting rapid boiling simulation..."
echo "This will take several minutes..."
echo ""

# Run with time monitoring
start_time=$(date +%s)
compressibleInterFoam | tee simulation.log

# Check if simulation completed successfully
if [ $? -eq 0 ]; then
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    echo ""
    echo "=== Simulation Completed Successfully! ==="
    echo "Duration: $duration seconds"
    
    # Count timesteps
    timestep_count=$(ls -1 [0-9]* 2>/dev/null | wc -l)
    echo "Number of output timesteps: $timestep_count"
    
    # Count actual computational timesteps from log
    if [ -f simulation.log ]; then
        actual_timesteps=$(grep -c "^Time = " simulation.log)
        echo "Actual computational timesteps: $actual_timesteps"
        
        # Show final time
        final_time=$(grep "^Time = " simulation.log | tail -1 | awk '{print $3}')
        echo "Final simulation time: $final_time seconds"
    fi
    
    echo ""
    echo "Results available in time directories:"
    ls -1 [0-9]* | head -10
    if [ $timestep_count -gt 10 ]; then
        echo "... and $((timestep_count - 10)) more"
    fi
    
    echo ""
    echo "=== Next Steps ==="
    echo "1. Visualize in ParaView: paraview case.foam"
    echo "2. Create animation: ./create_gif.sh"
    echo "3. Check simulation.log for detailed information"
    
else
    echo ""
    echo "❌ Simulation failed! Check the log for errors."
    echo "Check simulation.log for detailed error information"
    exit 1
fi
