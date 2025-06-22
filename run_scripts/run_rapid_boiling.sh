#!/bin/bash

# Script to run rapid boiling simulation with 100+ timesteps
# This script ensures we get at least 100 timesteps for detailed analysis

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

# Set initial water level
echo "Setting initial water level..."
setFields
if [ $? -ne 0 ]; then
    echo "Error: setFields failed!"
    exit 1
fi

# Calculate expected timesteps
echo ""
echo "=== Simulation Parameters ==="
echo "Initial temperature: 90°C (363.15 K) - Near boiling point"
echo "Heat flux: 150,000 K/m - Intense heating"
echo "End time: 5 seconds"
echo "Time step: 0.01 seconds (adaptive)"
echo "Expected timesteps: ~500 (much more than 100)"
echo "Output frequency: Every 0.05 seconds (100 output files)"
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
    fi
    
    echo ""
    echo "Results available in time directories:"
    ls -1 [0-9]* | head -10
    if [ $timestep_count -gt 10 ]; then
        echo "... and $((timestep_count - 10)) more"
    fi
    
    echo ""
    echo "=== What to Expect in Results ==="
    echo "- Rapid temperature rise from 90°C to 100°C+"
    echo "- Intense bubble formation and growth"
    echo "- Strong convection currents"
    echo "- Vigorous phase change (water → steam)"
    echo "- High velocity regions due to buoyancy"
    echo ""
    echo "Open in ParaView with: paraview case.foam"
    echo "Or create animation with: ./create_gif.sh"
    
else
    echo ""
    echo "❌ Simulation failed! Check the log for errors."
    echo "Common issues:"
    echo "- Time step too large (try reducing deltaT in controlDict)"
    echo "- Convergence problems (check residuals in log)"
    echo "- Memory issues (reduce mesh resolution)"
    exit 1
fi
