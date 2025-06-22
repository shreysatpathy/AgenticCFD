#!/bin/bash

# =============================================================================
# 🔬 THERMAL SIMULATION ANALYSIS SCRIPT 🔬
# =============================================================================
# 
# This script analyzes the results of the thermal boiling simulation:
# - Temperature field statistics
# - Heat transfer analysis
# - Phase distribution monitoring
# - Convergence analysis
# - Performance metrics
#
# Author: Augment Agent
# Date: 2025-06-21
# =============================================================================

set -e

echo "🔬🔬🔬 THERMAL SIMULATION ANALYSIS 🔬🔬🔬"
echo "========================================="

# =============================================================================
# STEP 1: Check simulation status
# =============================================================================
echo ""
echo "📊 SIMULATION STATUS CHECK"
echo "=========================="

if [ ! -f "thermal_simulation.log" ]; then
    echo "❌ No simulation log found. Run the simulation first!"
    exit 1
fi

# Check if simulation completed
if grep -q "End" thermal_simulation.log; then
    echo "✅ Simulation completed successfully"
    COMPLETION_STATUS="COMPLETED"
elif grep -q "FOAM FATAL" thermal_simulation.log; then
    echo "❌ Simulation failed with fatal error"
    COMPLETION_STATUS="FAILED"
else
    echo "⚠️  Simulation status unclear"
    COMPLETION_STATUS="UNKNOWN"
fi

# =============================================================================
# STEP 2: Temperature analysis
# =============================================================================
echo ""
echo "🌡️  TEMPERATURE ANALYSIS"
echo "========================"

# Count temperature solutions
TEMP_SOLUTIONS=$(grep -c "Solving for T" thermal_simulation.log || echo "0")
echo "Temperature solutions: $TEMP_SOLUTIONS"

if [ $TEMP_SOLUTIONS -gt 0 ]; then
    echo "✅ Temperature transport was active"
    
    # Get temperature residuals
    echo ""
    echo "Temperature convergence history:"
    grep "Solving for T" thermal_simulation.log | head -10 | while read line; do
        if [[ "$line" =~ Initial\ residual\ =\ ([0-9.e-]+).*Final\ residual\ =\ ([0-9.e-]+) ]]; then
            INITIAL=${BASH_REMATCH[1]}
            FINAL=${BASH_REMATCH[2]}
            echo "  Initial: $INITIAL → Final: $FINAL"
        fi
    done
else
    echo "❌ No temperature solutions found"
fi

# =============================================================================
# STEP 3: Time progression analysis
# =============================================================================
echo ""
echo "⏱️  TIME PROGRESSION ANALYSIS"
echo "============================="

# Extract time steps
TIMESTEPS=$(grep "Time = " thermal_simulation.log | wc -l || echo "0")
echo "Total timesteps: $TIMESTEPS"

if [ $TIMESTEPS -gt 0 ]; then
    echo ""
    echo "Time progression:"
    grep "Time = " thermal_simulation.log | head -10 | while read line; do
        if [[ "$line" =~ Time\ =\ ([0-9.e-]+)s ]]; then
            TIME=${BASH_REMATCH[1]}
            echo "  Time: ${TIME}s"
        fi
    done
    
    # Get final time
    FINAL_TIME=$(grep "Time = " thermal_simulation.log | tail -1 | grep -o '[0-9.e-]*s' | sed 's/s//')
    echo ""
    echo "Final simulation time: ${FINAL_TIME}s"
fi

# =============================================================================
# STEP 4: Convergence analysis
# =============================================================================
echo ""
echo "📈 CONVERGENCE ANALYSIS"
echo "======================="

# Check PIMPLE convergence
PIMPLE_CONVERGED=$(grep -c "PIMPLE: Converged" thermal_simulation.log || echo "0")
PIMPLE_NOT_CONVERGED=$(grep -c "PIMPLE: Not converged" thermal_simulation.log || echo "0")

echo "PIMPLE convergence:"
echo "  Converged steps: $PIMPLE_CONVERGED"
echo "  Non-converged steps: $PIMPLE_NOT_CONVERGED"

if [ $PIMPLE_CONVERGED -gt 0 ]; then
    echo "✅ Some timesteps achieved convergence"
else
    echo "⚠️  No timesteps achieved full convergence"
fi

# =============================================================================
# STEP 5: Phase analysis
# =============================================================================
echo ""
echo "🌊 PHASE ANALYSIS"
echo "================="

# Check phase volume fractions
PHASE_LINES=$(grep "Phase-1 volume fraction" thermal_simulation.log | wc -l || echo "0")
echo "Phase fraction updates: $PHASE_LINES"

if [ $PHASE_LINES -gt 0 ]; then
    echo ""
    echo "Phase volume fraction history:"
    grep "Phase-1 volume fraction" thermal_simulation.log | head -5 | while read line; do
        if [[ "$line" =~ Phase-1\ volume\ fraction\ =\ ([0-9.]+) ]]; then
            FRACTION=${BASH_REMATCH[1]}
            echo "  Water fraction: $FRACTION"
        fi
    done
fi

# =============================================================================
# STEP 6: Performance analysis
# =============================================================================
echo ""
echo "⚡ PERFORMANCE ANALYSIS"
echo "======================"

# Check execution time
if grep -q "ExecutionTime" thermal_simulation.log; then
    echo "Execution time progression:"
    grep "ExecutionTime" thermal_simulation.log | tail -5 | while read line; do
        if [[ "$line" =~ ExecutionTime\ =\ ([0-9.]+)\ s ]]; then
            EXEC_TIME=${BASH_REMATCH[1]}
            echo "  Execution time: ${EXEC_TIME}s"
        fi
    done
fi

# Check Courant numbers
MAX_COURANT=$(grep "Courant Number" thermal_simulation.log | grep -o "max: [0-9.e-]*" | tail -1 | cut -d' ' -f2 || echo "N/A")
echo "Maximum Courant number: $MAX_COURANT"

# =============================================================================
# STEP 7: Error analysis
# =============================================================================
echo ""
echo "🚨 ERROR ANALYSIS"
echo "================="

# Count different types of issues
FATAL_ERRORS=$(grep -c "FOAM FATAL" thermal_simulation.log || echo "0")
WARNINGS=$(grep -c "WARNING" thermal_simulation.log || echo "0")
BOUNDING=$(grep -c "bounding" thermal_simulation.log || echo "0")

echo "Fatal errors: $FATAL_ERRORS"
echo "Warnings: $WARNINGS"
echo "Bounding operations: $BOUNDING"

if [ $FATAL_ERRORS -gt 0 ]; then
    echo ""
    echo "❌ Fatal errors found:"
    grep "FOAM FATAL" thermal_simulation.log | head -3
fi

if [ $BOUNDING -gt 0 ]; then
    echo ""
    echo "⚠️  Bounding operations (field limiting):"
    grep "bounding" thermal_simulation.log | tail -3
fi

# =============================================================================
# STEP 8: Results summary
# =============================================================================
echo ""
echo "📋 RESULTS SUMMARY"
echo "=================="

# Check for result directories
RESULT_DIRS=$(ls -1d [0-9]* 2>/dev/null | wc -l || echo "0")
echo "Result directories: $RESULT_DIRS"

if [ $RESULT_DIRS -gt 0 ]; then
    echo "Available timesteps:"
    ls -1d [0-9]* 2>/dev/null | sort -n | head -10
    
    # Check field files in latest timestep
    LATEST_TIME=$(ls -1d [0-9]* 2>/dev/null | sort -n | tail -1)
    if [ -n "$LATEST_TIME" ]; then
        echo ""
        echo "Fields in latest timestep ($LATEST_TIME):"
        ls -1 "$LATEST_TIME"/ 2>/dev/null | sed 's/^/  /'
    fi
fi

# =============================================================================
# STEP 9: Recommendations
# =============================================================================
echo ""
echo "💡 RECOMMENDATIONS"
echo "=================="

if [ "$COMPLETION_STATUS" = "COMPLETED" ]; then
    echo "✅ Simulation completed successfully!"
    echo "   → Ready for visualization and post-processing"
    echo "   → Run 'paraFoam' to visualize results"
elif [ "$COMPLETION_STATUS" = "FAILED" ]; then
    echo "❌ Simulation failed. Consider:"
    echo "   → Check boundary conditions"
    echo "   → Reduce time step"
    echo "   → Adjust solver settings"
    echo "   → Review thermal properties"
else
    echo "⚠️  Simulation status unclear. Check log file manually."
fi

if [ $TEMP_SOLUTIONS -gt 0 ]; then
    echo "✅ Temperature transport was active - thermal physics working!"
else
    echo "❌ No temperature solutions - check thermal setup"
fi

if [ $TIMESTEPS -gt 5 ]; then
    echo "✅ Multiple timesteps completed - good progress"
elif [ $TIMESTEPS -gt 0 ]; then
    echo "⚠️  Few timesteps completed - may need longer runtime"
else
    echo "❌ No timesteps completed - check setup"
fi

echo ""
echo "🔬 Analysis complete! Check thermal_simulation.log for detailed output."
echo "📊 For visualization: touch case.foam && paraFoam"
