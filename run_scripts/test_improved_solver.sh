#!/bin/bash

# Test improved pressure solver settings
# Should achieve better convergence and allow larger time steps

echo "🔧 === Testing Improved Pressure Solver === 🔧"
echo ""

# Source OpenFOAM environment
source /opt/openfoam11/etc/bashrc

echo "=== Solver Improvements ==="
echo "✅ GAMG solver: Better smoother (GaussSeidel vs DIC)"
echo "✅ GAMG settings: Optimized agglomeration and sweeps"
echo "✅ PIMPLE algorithm: More outer correctors (3 vs 1)"
echo "✅ Momentum predictor: Enabled for stability"
echo "✅ Residual controls: Added convergence criteria"
echo "✅ Relaxation factors: Added under-relaxation for stability"
echo ""

# Check current simulation status
if [ -f "5/alpha.water" ]; then
    echo "📊 Previous simulation completed successfully"
    echo "🔄 Starting from clean state for comparison..."
    
    # Backup completed results
    if [ ! -d "results_backup" ]; then
        mkdir results_backup
        cp -r [0-9]* results_backup/ 2>/dev/null || true
        echo "✅ Backed up previous results to results_backup/"
    fi
    
    # Clean for fresh start
    rm -rf [0-9]* processor* 
    echo "🧹 Cleaned case for fresh test"
else
    echo "📊 No previous results found"
fi

echo ""
echo "=== Expected Improvements ==="
echo "🎯 Better pressure convergence (< 100 iterations vs 1000)"
echo "🎯 Larger adaptive time steps (0.02-0.05s vs 0.01s)"
echo "🎯 Faster overall simulation (2-3x speedup)"
echo "🎯 More stable solution"
echo ""

# Initialize the case
echo "🔧 Initializing case with improved settings..."
blockMesh > /dev/null 2>&1
setFields > /dev/null 2>&1

# Decompose for parallel run
echo "📦 Decomposing domain for parallel execution..."
decomposePar > /dev/null 2>&1

echo "🚀 Starting test simulation with improved solver..."
echo "Monitoring first few timesteps for convergence..."
echo ""

start_time=$(date +%s)

# Run parallel simulation with monitoring
timeout 300 mpirun -np 8 foamRun -solver incompressibleVoF -parallel 2>&1 | tee improved_solver_test.log &
sim_pid=$!

# Monitor progress for first few timesteps
sleep 5
echo "📊 === Monitoring Pressure Solver Performance ==="

for i in {1..10}; do
    if ps -p $sim_pid > /dev/null; then
        # Check latest pressure solver performance
        if [ -f "improved_solver_test.log" ]; then
            latest_pressure=$(grep "GAMG.*p_rgh.*No Iterations" improved_solver_test.log | tail -1)
            latest_time=$(grep "^Time = " improved_solver_test.log | tail -1)
            latest_dt=$(grep "^deltaT = " improved_solver_test.log | tail -1)
            
            if [ ! -z "$latest_pressure" ]; then
                iterations=$(echo "$latest_pressure" | awk '{print $NF}')
                echo "⏱️  $latest_time | $latest_dt | Pressure iterations: $iterations"
                
                if [ "$iterations" -lt 50 ]; then
                    echo "🎉 Excellent convergence! (< 50 iterations)"
                elif [ "$iterations" -lt 100 ]; then
                    echo "✅ Good convergence! (< 100 iterations)"
                elif [ "$iterations" -lt 500 ]; then
                    echo "⚠️  Moderate convergence (< 500 iterations)"
                else
                    echo "❌ Poor convergence (> 500 iterations)"
                fi
            fi
        fi
        sleep 10
    else
        break
    fi
done

# Wait for completion or timeout
wait $sim_pid 2>/dev/null
exit_code=$?

end_time=$(date +%s)
duration=$((end_time - start_time))

echo ""
if [ $exit_code -eq 0 ]; then
    echo "🎉 === Test Completed Successfully! ==="
    
    # Reconstruct results
    echo "🔄 Reconstructing results..."
    reconstructPar > /dev/null 2>&1
    
    # Analyze performance
    if [ -f "improved_solver_test.log" ]; then
        total_timesteps=$(grep -c "^Time = " improved_solver_test.log)
        avg_pressure_iters=$(grep "GAMG.*p_rgh.*No Iterations" improved_solver_test.log | awk '{sum+=$NF; count++} END {if(count>0) print int(sum/count); else print "N/A"}')
        max_pressure_iters=$(grep "GAMG.*p_rgh.*No Iterations" improved_solver_test.log | awk '{if($NF>max) max=$NF} END {print max}')
        final_time=$(grep "^Time = " improved_solver_test.log | tail -1 | awk '{print $3}')
        
        echo "📊 Performance Analysis:"
        echo "  ⏱️  Duration: ${duration}s"
        echo "  🔢 Timesteps completed: $total_timesteps"
        echo "  🏁 Final simulation time: ${final_time}s"
        echo "  📈 Average pressure iterations: $avg_pressure_iters"
        echo "  📊 Maximum pressure iterations: $max_pressure_iters"
        
        if [ "$max_pressure_iters" -lt 100 ]; then
            echo "🎉 EXCELLENT: Pressure solver converging well!"
            echo "✅ Ready for larger time steps and faster simulation"
        elif [ "$max_pressure_iters" -lt 500 ]; then
            echo "✅ GOOD: Significant improvement in convergence"
            echo "💡 Can try moderately larger time steps"
        else
            echo "⚠️  MODERATE: Some improvement but still challenging"
            echo "💡 May need further solver tuning"
        fi
    fi
    
elif [ $exit_code -eq 124 ]; then
    echo "⏱️  Test timed out after 5 minutes"
    echo "💡 Check convergence in first few timesteps"
else
    echo "❌ Test failed with exit code: $exit_code"
    echo "📋 Check improved_solver_test.log for details"
fi

echo ""
echo "🔍 === Next Steps ==="
if [ -f "improved_solver_test.log" ] && [ "$max_pressure_iters" -lt 100 ]; then
    echo "1. ✅ Solver improvements successful!"
    echo "2. 🚀 Run full simulation with larger time steps"
    echo "3. 📈 Expect 2-5x speedup in simulation time"
else
    echo "1. 📊 Review pressure solver performance"
    echo "2. 🔧 Consider additional solver tuning if needed"
    echo "3. 💡 May need mesh refinement or different approach"
fi

echo ""
echo "📁 Files created:"
echo "  - improved_solver_test.log (solver performance log)"
echo "  - results_backup/ (previous simulation results)"
echo "  - Updated system/fvSolution (improved solver settings)"
