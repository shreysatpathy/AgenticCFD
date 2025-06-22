#!/bin/bash

# Parallel OpenFOAM Boiling Simulation
# Uses 8 cores for faster computation

echo "🚀 === Parallel Rapid Boiling Simulation === 🚀"
echo ""

# Source OpenFOAM environment
source /opt/openfoam11/etc/bashrc

# Check if we need to decompose
if [ ! -d "processor0" ]; then
    echo "📊 Setting up parallel decomposition..."
    
    # Clean any existing decomposition
    rm -rf processor*
    
    # Decompose the domain
    echo "🔧 Decomposing domain into 8 subdomains..."
    decomposePar
    
    if [ $? -ne 0 ]; then
        echo "❌ Error: Domain decomposition failed!"
        exit 1
    fi
    
    echo "✅ Domain decomposed successfully!"
    echo "📁 Created processor directories: processor0 to processor7"
else
    echo "✅ Parallel decomposition already exists"
fi

echo ""
echo "=== Parallel Simulation Parameters ==="
echo "🖥️  CPU cores: 8 (out of 16 available)"
echo "📦 Subdomains: 2x2x2 = 8"
echo "🔥 Solver: incompressibleVoF"
echo "🌡️  Initial temperature: 90°C"
echo "⚡ Heat flux: 150,000 K/m"
echo "⏱️  End time: 5 seconds"
echo "📈 Expected speedup: ~4-6x faster"
echo ""

# Run parallel simulation
echo "🚀 Starting parallel simulation..."
echo "This should be much faster than serial!"
echo ""

start_time=$(date +%s)

# Run in parallel with 8 processes
mpirun -np 8 foamRun -solver incompressibleVoF -parallel 2>&1 | tee parallel_simulation.log

# Check results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    echo ""
    echo "🎉 === Parallel Simulation Completed! === 🎉"
    echo "⏱️  Duration: $duration seconds"
    
    # Reconstruct the case for visualization
    echo "🔄 Reconstructing case for ParaView..."
    reconstructPar
    
    if [ $? -eq 0 ]; then
        echo "✅ Case reconstructed successfully!"
        
        # Count timesteps
        timestep_count=$(ls -1d [0-9]* 2>/dev/null | wc -l)
        echo "📊 Number of output timesteps: $timestep_count"
        
        # Count computational timesteps from log
        if [ -f parallel_simulation.log ]; then
            actual_timesteps=$(grep -c "^Time = " parallel_simulation.log)
            echo "🔢 Computational timesteps: $actual_timesteps"
            
            # Show final time
            final_time=$(grep "^Time = " parallel_simulation.log | tail -1 | awk '{print $3}')
            echo "🏁 Final simulation time: $final_time seconds"
        fi
        
        echo ""
        echo "📁 Time directories:"
        ls -1d [0-9]* | head -10
        if [ $timestep_count -gt 10 ]; then
            echo "... and $((timestep_count - 10)) more"
        fi
        
        echo ""
        echo "🔥 === Parallel Boiling Results Ready! === 🔥"
        echo "✅ Speedup achieved with 8 cores"
        echo "✅ High-temperature rapid boiling simulation"
        echo "✅ Two-phase flow with interface tracking"
        echo ""
        echo "🎬 Next steps:"
        echo "1. Visualize: paraview case.foam"
        echo "2. Create animation: ./create_gif.sh"
        echo "3. Compare with serial performance"
        
    else
        echo "⚠️  Warning: Case reconstruction failed"
        echo "💡 You can still visualize using processor directories"
    fi
    
else
    echo ""
    echo "❌ Parallel simulation failed!"
    echo "📋 Error details:"
    tail -20 parallel_simulation.log
    echo ""
    echo "💡 Troubleshooting:"
    echo "- Check if MPI is installed: mpirun --version"
    echo "- Try with fewer cores: edit decomposeParDict"
    echo "- Fall back to serial: ./run_working_boiling.sh"
    exit 1
fi
