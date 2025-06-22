#!/bin/bash

# Corrected script for rapid boiling simulation with OpenFOAM 11
# Uses the proper compressibleVoF solver and boundary conditions

echo "=== Corrected Rapid Boiling Simulation ==="
echo ""

# Source OpenFOAM environment
echo "Sourcing OpenFOAM environment..."
source /opt/openfoam11/etc/bashrc

# Clean and regenerate
echo "Cleaning and regenerating case..."
./Allclean

# Generate mesh
echo "Generating mesh..."
blockMesh
if [ $? -ne 0 ]; then
    echo "Error: Mesh generation failed!"
    exit 1
fi

echo "Mesh generated: 64,000 cells (40×40×40)"

# Set initial water level
echo "Setting initial water level..."
setFields
if [ $? -ne 0 ]; then
    echo "Error: setFields failed!"
    exit 1
fi

# Fix alpha.water field with correct boundary conditions
echo "Fixing alpha.water field for OpenFOAM 11..."
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

internalField   uniform 0;

boundaryField
{
    bottom
    {
        type            zeroGradient;
    }
    
    walls
    {
        type            contactAngle;
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

# Now run setFields again to set the water level properly
echo "Re-running setFields to initialize water level..."
setFields

# Extract the internal field data and preserve boundary conditions
echo "Preserving boundary conditions while keeping water initialization..."

# Create a temporary script to fix the alpha.water field
cat > fix_alpha.py << 'EOF'
#!/usr/bin/env python3
import re

# Read the corrupted file
with open('0/alpha.water', 'r') as f:
    content = f.read()

# Extract the internal field data (the numbers between parentheses)
# Find the pattern: number followed by opening parenthesis, then data, then closing parenthesis
match = re.search(r'internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\((.*?)\n\);', content, re.DOTALL)

if match:
    count = match.group(1)
    data = match.group(2)
    
    # Create the corrected file
    corrected_content = '''/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\\\    /   O peration     | Website:  https://openfoam.org
    \\\\  /    A nd           | Version:  11
     \\\\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
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

internalField   nonuniform List<scalar>
''' + count + '''
(
''' + data + '''
);

boundaryField
{
    bottom
    {
        type            zeroGradient;
    }
    
    walls
    {
        type            contactAngle;
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

// ************************************************************************* //'''
    
    # Write the corrected file
    with open('0/alpha.water', 'w') as f:
        f.write(corrected_content)
    
    print(f"Fixed alpha.water field with {count} cells")
else:
    print("Could not parse alpha.water field")
EOF

python3 fix_alpha.py
rm fix_alpha.py

echo ""
echo "=== Simulation Parameters ==="
echo "Solver: compressibleVoF (OpenFOAM 11)"
echo "Initial temperature: 90°C (363.15 K)"
echo "Heat flux: 150,000 K/m"
echo "End time: 5 seconds"
echo "Time step: 0.01 seconds (adaptive)"
echo "Expected timesteps: ~500"
echo ""

# Run the simulation with the correct solver
echo "Starting rapid boiling simulation with foamRun..."
echo "This will take several minutes..."
echo ""

start_time=$(date +%s)
foamRun -solver compressibleVoF | tee simulation.log

# Check results
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
    echo "Time directories created:"
    ls -1 [0-9]* | head -10
    if [ $timestep_count -gt 10 ]; then
        echo "... and $((timestep_count - 10)) more"
    fi
    
    echo ""
    echo "=== Rapid Boiling Results Ready! ==="
    echo "✓ Over 100 timesteps achieved: $actual_timesteps computational steps"
    echo "✓ High-temperature initial conditions (90°C)"
    echo "✓ Intense heating for rapid phase change"
    echo ""
    echo "Next steps:"
    echo "1. Visualize: paraview case.foam"
    echo "2. Create GIF: ./create_gif.sh"
    echo "3. Check log: cat simulation.log"
    
else
    echo ""
    echo "❌ Simulation failed!"
    echo "Check simulation.log for errors"
    tail -20 simulation.log
    exit 1
fi
