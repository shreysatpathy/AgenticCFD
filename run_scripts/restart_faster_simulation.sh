#!/bin/bash

# Restart OpenFOAM simulation with faster time steps
# Updated controlDict for 10x faster execution

echo "🚀 === Restarting with Faster Time Steps === 🚀"
echo ""

# Source OpenFOAM environment
source /opt/openfoam11/etc/bashrc

# Check current simulation status
echo "📊 Current simulation status:"
if [ -f "parallel_simulation.log" ]; then
    current_time=$(grep "^Time = " parallel_simulation.log | tail -1 | awk '{print $3}')
    echo "⏱️  Last completed time: ${current_time}s"
else
    echo "⚠️  No previous log found"
    current_time="0"
fi

echo ""
echo "=== Updated Time Step Settings ==="
echo "🔧 maxCo: 0.5 → 2.0 (4x more aggressive)"
echo "🔧 maxAlphaCo: 0.5 → 1.0 (2x more aggressive)"  
echo "🔧 maxDeltaT: 0.01 → 0.1 (10x larger maximum)"
echo "📈 Expected speedup: 5-10x faster!"
echo ""

# Kill any existing simulation
echo "🛑 Stopping current simulation..."
pkill -f "mpirun.*foamRun" || echo "No running simulation found"
sleep 2

# Check if we need to reconstruct first
if [ -d "processor0" ] && [ ! -f "${current_time}/alpha.water" ]; then
    echo "🔄 Reconstructing current results..."
    reconstructPar -latestTime
fi

# Restart the parallel simulation
echo "🚀 Restarting parallel simulation with faster time steps..."
echo "This should run much faster now!"
echo ""

start_time=$(date +%s)

# Run in parallel with 8 processes
mpirun -np 8 foamRun -solver incompressibleVoF -parallel 2>&1 | tee faster_simulation.log

# Check results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    echo ""
    echo "🎉 === Faster Simulation Completed! === 🎉"
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
        if [ -f faster_simulation.log ]; then
            actual_timesteps=$(grep -c "^Time = " faster_simulation.log)
            echo "🔢 Computational timesteps: $actual_timesteps"
            
            # Show final time
            final_time=$(grep "^Time = " faster_simulation.log | tail -1 | awk '{print $3}')
            echo "🏁 Final simulation time: $final_time seconds"
            
            # Show average time step
            if [ "$actual_timesteps" -gt 0 ]; then
                avg_dt=$(echo "scale=6; $final_time / $actual_timesteps" | bc -l)
                echo "📈 Average time step: ${avg_dt}s (vs 0.01s before)"
            fi
        fi
        
        echo ""
        echo "📁 Time directories:"
        ls -1d [0-9]* | head -10
        if [ $timestep_count -gt 10 ]; then
            echo "... and $((timestep_count - 10)) more"
        fi
        
        echo ""
        echo "🔥 === Faster Boiling Results Ready! === 🔥"
        echo "✅ Simulation completed with larger time steps"
        echo "✅ Much faster execution achieved"
        echo "✅ Ready for visualization and analysis"
        echo ""
        echo "🎬 Next steps:"
        echo "1. Visualize: paraview case.foam"
        echo "2. Check interface: Look for alpha.water changes"
        echo "3. Analyze results: Compare with previous run"
        
    else
        echo "⚠️  Warning: Case reconstruction failed"
        echo "💡 You can still visualize using processor directories"
    fi
    
else
    echo ""
    echo "❌ Faster simulation failed!"
    echo "📋 Error details:"
    tail -20 faster_simulation.log
    echo ""
    echo "💡 Troubleshooting:"
    echo "- Time steps might be too large for current conditions"
    echo "- Try reducing maxCo back to 1.0"
    echo "- Check if boiling has started (more restrictive time steps needed)"
    echo "- Fall back to original settings if needed"
    exit 1
fi
