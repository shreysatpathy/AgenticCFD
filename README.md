# 🔥 Thermal Boiling Simulation - OpenFOAM CFD Analysis

## 🎯 Project Value & Significance

This comprehensive thermal boiling simulation represents a sophisticated computational fluid dynamics (CFD) analysis of two-phase flow with phase change phenomena, utilizing OpenFOAM's compressibleVoF solver to model the complex physics of water-to-vapor transition under controlled heating conditions. The simulation captures critical thermal engineering processes including interface dynamics, bubble formation, heat transfer mechanisms, and vapor generation within a 10cm³ heated pool domain, providing valuable insights for applications ranging from nuclear reactor safety analysis and industrial heat exchanger design to microfluidics and thermal management systems. By employing a high-resolution 40×40×40 computational grid with parallel processing capabilities, the simulation delivers detailed temporal and spatial resolution of the boiling interface evolution, temperature field distribution, and phase fraction dynamics over a 1-second timeframe, generating both quantitative data for engineering analysis and high-quality 2D/3D visualizations that reveal the fundamental physics of thermal phase change processes. The complete workflow includes automated simulation execution, real-time monitoring, comprehensive post-processing analysis, and advanced visualization tools that produce professional-grade animations and static images, making this simulation framework invaluable for research, education, and industrial applications requiring detailed understanding of thermal boiling phenomena and two-phase flow behavior.

## 📋 Case Specifications

This OpenFOAM case simulates the thermal two-phase flow of a boiling pool of water with the following specifications:

## Case Parameters
- **Domain geometry**: 10cm × 10cm × 10cm cubic heated pool
- **Grid resolution**: 40 × 40 × 40 cells (64,000 total)
- **Initial temperature**: 25°C (298.15 K)
- **Heat source**: 50,000 K/m thermal gradient from bottom wall
- **Pool configuration**: 5cm water height, 5cm vapor space above
- **Solver**: compressibleVoF with thermal phase change
- **Simulation time**: 0.0s to 1.0s with adaptive time stepping
- **Parallel processing**: 8-core decomposition for enhanced performance

## Physical Models
- **Two-phase flow**: Water (liquid) and air/steam (gas)
- **Phase change**: Lee model for evaporation/condensation
- **Turbulence**: k-ε RANS model for both phases
- **Heat transfer**: Full energy equation with conduction and convection
- **Surface tension**: 0.0728 N/m (water-air interface)

## 📁 Project Organization
```
flows/
├── 📂 run_scripts/              # Simulation execution scripts
│   ├── run_thermal_boiling.sh   # Main simulation runner
│   ├── run_parallel_boiling.sh  # Parallel execution
│   ├── analyze_thermal_results.sh # Post-processing analysis
│   └── monitor_simulation.sh    # Real-time monitoring
├── 📂 visualization_scripts/    # Analysis and visualization tools
│   ├── create_boiling_animation.py # 2D interface animations
│   ├── ultimate_3d_boiling_viz.py # 3D temperature-colored visualizations
│   └── visualization_summary.py # Comprehensive analysis overview
├── 📂 visualization_output/     # Generated visualizations (excluded from git)
│   ├── thermal_boiling_evolution.gif # 2D interface evolution
│   ├── 3d_boiling_rotation.gif  # 3D rotating views
│   └── *.png                    # High-quality static images
├── 📂 0/                        # Initial conditions
│   ├── alpha.water              # Water volume fraction
│   ├── U                        # Velocity field
│   ├── p_rgh                    # Pressure field
│   └── T                        # Temperature field
├── 📂 constant/                 # Material properties and mesh
│   ├── transportProperties      # Phase properties
│   ├── thermophysicalProperties # Thermal properties
│   └── phaseChangeProperties    # Phase change modeling
├── 📂 system/                   # Solver configuration
│   ├── controlDict             # Time control and field averaging
│   ├── fvSchemes               # Numerical schemes
│   ├── fvSolution              # Linear solvers and PIMPLE settings
│   ├── blockMeshDict           # 40×40×40 mesh generation
│   ├── setFieldsDict           # Initial water level setup
│   └── decomposeParDict        # Parallel decomposition
├── 📂 [0.01-1.0]/              # Time directories (simulation results)
├── 📂 processor*/              # Parallel decomposition data
└── 📂 postProcessing/          # OpenFOAM analysis output
```

## 🚀 Running the Simulation

### Prerequisites
- OpenFOAM 9 or later with properly sourced environment
- Python 3.x with matplotlib, numpy, PIL for visualizations
- WSL/Linux environment for script execution
- Minimum 8GB RAM for parallel processing

### Quick Start
```bash
# Navigate to run scripts directory
cd run_scripts/

# Execute main thermal boiling simulation
./run_thermal_boiling.sh

# Monitor simulation progress (in separate terminal)
./monitor_simulation.sh

# Analyze results after completion
./analyze_thermal_results.sh
```

### Advanced Execution Options
```bash
# Parallel execution (recommended)
./run_parallel_boiling.sh

# Complete workflow with analysis
./run_complete_thermal_simulation.sh

# Manual step-by-step execution
blockMesh                    # Generate 40×40×40 mesh
setFields                    # Initialize water level
decomposePar                 # Decompose for parallel
mpirun -np 8 compressibleVoF -parallel  # Run solver
reconstructPar               # Reconstruct results
```

## 🎨 Visualization & Analysis

### Automated Visualization Generation
```bash
# Navigate to visualization scripts
cd visualization_scripts/

# Generate comprehensive 2D animations
python3 create_boiling_animation.py

# Create 3D temperature-colored visualizations
python3 ultimate_3d_boiling_viz.py

# Generate analysis summary
python3 visualization_summary.py
```

### Generated Visualizations
- **2D Interface Evolution**: `thermal_boiling_evolution.gif` - Interface + temperature overlay
- **3D Rotating Views**: `3d_boiling_rotation.gif` - 360° temperature-colored visualization
- **3D Time Evolution**: `3d_boiling_time_evolution.gif` - Temporal boiling dynamics
- **High-Quality Snapshots**: Static PNG images for publications

### ParaView Analysis
```bash
# Traditional OpenFOAM visualization
paraview case.foam
```

### Key Variables to Analyze
- **alpha.water**: Water volume fraction (0=vapor, 1=water)
- **alphaMean.water**: Time-averaged water fraction (statistical interface)
- **T**: Temperature field (thermal distribution and gradients)
- **U**: Velocity vectors (convection and bubble dynamics)
- **p_rgh**: Pressure field (hydrostatic and dynamic effects)

### Advanced Visualization Features
1. **Temperature-colored interface**: Hot colormap showing thermal gradients
2. **3D domain boundaries**: Transparent cube wireframe for spatial context
3. **Phase identification**: Blue (water), red (vapor), hot colors (interface)
4. **Time-averaged analysis**: Statistical behavior using alphaMean fields
5. **Multi-scale visualization**: From microscopic bubbles to macroscopic flow patterns

## Expected Physics

The simulation should capture:
1. **Initial heating**: Bottom surface heats the water
2. **Natural convection**: Hot water rises, cold water sinks
3. **Nucleate boiling**: Vapor bubbles form at heated surface
4. **Bubble dynamics**: Bubbles grow, detach, and rise
5. **Phase change**: Evaporation at hot surfaces, condensation in cooler regions
6. **Heat transfer**: Conduction in liquid, convection by fluid motion

## Troubleshooting

### Common Issues
1. **Convergence problems**: Reduce time step in controlDict
2. **Mesh quality**: Check blockMesh output for warnings
3. **Phase change instability**: Adjust Lee model coefficients
4. **Memory issues**: Reduce mesh resolution in blockMeshDict

### Performance Tips
- Start with coarser mesh for testing
- Use parallel processing: `mpirun -np 4 compressibleInterFoam -parallel`
- Monitor residuals in log files

## Customization

### Modifying Heat Input
Edit `0/T` boundary condition for bottom patch:
```cpp
bottom
{
    type            fixedGradient;
    gradient        uniform 60000;  // Adjust this value
}
```

### Changing Pool Geometry
Modify `system/blockMeshDict` vertices and blocks.

### Material Properties
Edit files in `constant/` directory for different fluids or conditions.

## References
- OpenFOAM User Guide: https://openfoam.org/guide/
- compressibleInterFoam solver documentation
- Two-phase flow modeling in OpenFOAM
