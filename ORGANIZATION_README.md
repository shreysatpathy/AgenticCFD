# 🔥 Thermal Boiling Simulation - Project Organization

## 📁 Directory Structure

```
flows/
├── 📂 run_scripts/              # All simulation execution scripts
├── 📂 visualization_scripts/    # All visualization and analysis scripts  
├── 📂 visualization_output/     # Generated images, GIFs, and plots
├── 📂 system/                   # OpenFOAM system configuration
├── 📂 constant/                 # Physical properties and mesh
├── 📂 0/, 0.01/, 0.02/, ...    # Time directories with simulation results
├── 📂 processor*/               # Parallel decomposition data
├── 📂 postProcessing/           # OpenFOAM post-processing output
└── 📂 results_backup/           # Backup of previous simulation results
```

## 🚀 Run Scripts (`run_scripts/`)

### **Main Simulation Scripts:**
- `run_thermal_boiling.sh` - Primary thermal boiling simulation
- `run_parallel_boiling.sh` - Parallel execution version
- `run_complete_thermal_simulation.sh` - Complete workflow
- `setup_rapid_boiling.sh` - Quick setup for boiling simulation

### **Analysis & Monitoring:**
- `analyze_thermal_results.sh` - Post-simulation analysis
- `monitor_simulation.sh` - Real-time simulation monitoring
- `test_improved_solver.sh` - Solver testing and validation

### **Utility Scripts:**
- `restart_faster_simulation.sh` - Restart with optimized settings
- `create_gif.sh` / `create_gif.bat` - Basic GIF creation utilities

### **Legacy Scripts:**
- `run_simple_boiling.sh` - Basic boiling setup
- `run_corrected_boiling.sh` - Corrected version
- `run_final_boiling.sh` - Final optimized version
- `run_working_boiling.sh` - Working baseline version

## 🎨 Visualization Scripts (`visualization_scripts/`)

### **2D Visualizations:**
- `create_boiling_animation.py` - Advanced 2D interface animation
- `simple_boiling_gif.py` - Simple 2D GIF generator
- `create_animation.py` - General animation utilities
- `simple_animation.py` - Basic animation framework

### **3D Visualizations:**
- `create_3d_boiling_visualization.py` - Full 3D visualization suite
- `ultimate_3d_boiling_viz.py` - Ultimate 3D visualization with temperature coloring
- `simple_interface.py` - Simple 3D interface visualization

### **Analysis & Summary:**
- `visualization_summary.py` - Comprehensive visualization overview
- `visualize_interface.py` - Interface-specific analysis

## 🖼️ Visualization Output (`visualization_output/`)

### **2D Animations:**
- `thermal_boiling_evolution.gif` (3.6MB) - Complete 2D evolution with temperature
- `simple_boiling_animation.gif` (2.7MB) - Simplified 2D animation

### **3D Visualizations:**
- `3d_boiling_rotation.gif` (1.9MB) - 360° rotating 3D view
- `3d_boiling_time_evolution.gif` (1.8MB) - 3D time evolution
- `3d_boiling_t0.500s.png` (597KB) - High-quality 3D snapshot
- `test_3d_ultimate.png` (1.2MB) - Ultimate 3D visualization

### **Summary:**
- `visualization_montage.png` - Side-by-side comparison of key visualizations

## 🔧 Usage Instructions

### **Running Simulations:**
```bash
cd run_scripts/
./run_thermal_boiling.sh          # Main simulation
./monitor_simulation.sh           # Monitor progress
./analyze_thermal_results.sh      # Analyze results
```

### **Creating Visualizations:**
```bash
cd visualization_scripts/
python3 create_boiling_animation.py           # 2D animations
python3 ultimate_3d_boiling_viz.py           # 3D visualizations
python3 visualization_summary.py             # Summary overview
```

### **Viewing Results:**
```bash
cd visualization_output/
# Open any .gif or .png file in your preferred viewer
```

## 📊 File Statistics

| Directory | Files | Total Size | Description |
|-----------|-------|------------|-------------|
| `run_scripts/` | 15 scripts | ~50KB | Simulation execution |
| `visualization_scripts/` | 9 scripts | ~150KB | Visualization generation |
| `visualization_output/` | 7 files | ~11.8MB | Generated visualizations |

## 🎯 Key Features

### **Simulation Capabilities:**
- ✅ Thermal two-phase flow with phase change
- ✅ Parallel processing (8 cores)
- ✅ Stable numerical schemes
- ✅ Real-time monitoring
- ✅ Automatic result analysis

### **Visualization Features:**
- ✅ 2D interface evolution animations
- ✅ 3D temperature-colored visualizations
- ✅ Rotating 3D views
- ✅ Time evolution animations
- ✅ High-quality static images
- ✅ Comprehensive analysis tools

## 🔬 Technical Details

- **Domain**: 10cm × 10cm × 10cm heated pool
- **Grid**: 40 × 40 × 40 cells (64,000 total)
- **Solver**: compressibleVoF (OpenFOAM)
- **Physics**: Thermal boiling with phase change
- **Time Range**: 0.0s to 1.0s simulation time
- **Heat Source**: Bottom wall heating (50,000 K/m)

## 🚀 Next Steps

1. **Run Analysis**: Execute scripts in `run_scripts/` for simulation
2. **Generate Visuals**: Use scripts in `visualization_scripts/` for analysis
3. **Review Results**: Check outputs in `visualization_output/`
4. **Modify Parameters**: Edit configuration files for different scenarios
5. **Advanced Analysis**: Use ParaView for detailed 3D analysis

## 📝 Notes

- All scripts are executable and well-documented
- Visualization outputs are optimized for quality and file size
- Scripts handle error checking and provide progress feedback
- Organization supports easy navigation and maintenance

---
**Generated**: Thermal Boiling Simulation Project
**Last Updated**: Current organization with all files properly categorized
