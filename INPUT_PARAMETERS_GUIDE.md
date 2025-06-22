# OpenFOAM Boiling Pool - Input Parameters Guide

This guide shows you exactly where to modify input variables and initial conditions for your boiling pool simulation.

## 🎯 **Quick Reference Table**

| Parameter | File | Line | Current Value | Description |
|-----------|------|------|---------------|-------------|
| Initial Temperature | `0/T` | 20 | 298.15 K | Starting water temperature |
| Heat Flux | `0/T` | 29 | 60000 | Bottom heating intensity |
| Water Level | `system/setFieldsDict` | 28 | 0.05 m | Initial water height |
| Pool Radius | `system/setFieldsDict` | 29 | 0.05 m | Pool radius |
| Simulation Time | `system/controlDict` | 26 | 10 s | Total simulation duration |
| Time Step | `system/controlDict` | 28 | 0.001 s | Calculation time step |
| Output Frequency | `system/controlDict` | 32 | 0.1 s | How often to save results |

## 🌡️ **Temperature Settings**

### **Initial Water Temperature** (`0/T`)
```cpp
// Line 20
internalField   uniform 298.15;  // 25°C in Kelvin

// Common values:
// 273.15  = 0°C   (ice cold)
// 283.15  = 10°C  (cold)
// 293.15  = 20°C  (room temperature)
// 298.15  = 25°C  (current setting)
// 313.15  = 40°C  (warm)
// 353.15  = 80°C  (hot start)
```

### **Heat Input** (`0/T`)
```cpp
// Line 29 - Bottom boundary condition
gradient        uniform 60000;  // Heat flux [K/m]

// Heat intensity guide:
// 10000   = Gentle heating
// 30000   = Moderate heating
// 60000   = Current setting (strong)
// 100000  = Intense heating
// 200000  = Extreme heating
```

### **Boiling Point** (`constant/phaseChangeProperties`)
```cpp
// Line 26
saturationTemperature   373.15;  // 100°C at 1 atm

// For different pressures:
// 363.15  = 90°C  (reduced pressure)
// 373.15  = 100°C (standard pressure)
// 383.15  = 110°C (elevated pressure)
```

## 🏊 **Pool Geometry**

### **Water Level** (`system/setFieldsDict`)
```cpp
// Line 28
p2 (0 0 0.05);  // Water height = 5cm

// Examples:
// p2 (0 0 0.03);  // 3cm deep (shallow)
// p2 (0 0 0.05);  // 5cm deep (current)
// p2 (0 0 0.08);  // 8cm deep (deeper)
// p2 (0 0 0.10);  // 10cm deep (full height)
```

### **Pool Radius** (`system/setFieldsDict`)
```cpp
// Line 29
radius 0.05;    // 5cm radius

// Examples:
// radius 0.03;    // 3cm radius (small)
// radius 0.05;    // 5cm radius (current)
// radius 0.08;    // 8cm radius (large)
```

### **Total Domain Size** (`system/blockMeshDict`)
```cpp
// Lines 25-34 - Vertices define the computational domain
// Current: 10cm × 10cm × 10cm box
// Bottom: (-0.05, -0.05, 0) to (0.05, 0.05, 0)
// Top:    (-0.05, -0.05, 0.1) to (0.05, 0.05, 0.1)

// To change domain size, modify all coordinates proportionally
```

## ⏱️ **Time Settings**

### **Simulation Duration** (`system/controlDict`)
```cpp
// Line 26
endTime         10;     // 10 seconds total

// Typical values:
// 5      = Quick test (5 seconds)
// 10     = Current setting
// 20     = Longer simulation
// 60     = Full minute simulation
```

### **Time Step** (`system/controlDict`)
```cpp
// Line 28
deltaT          0.001;  // 1 millisecond

// Stability guide:
// 0.0001  = Very stable (slow)
// 0.001   = Current setting
// 0.01    = Faster (less stable)
```

### **Output Frequency** (`system/controlDict`)
```cpp
// Line 32
writeInterval   0.1;    // Save every 0.1 seconds

// Storage vs detail trade-off:
// 0.01   = Very detailed (large files)
// 0.1    = Current setting (good balance)
// 0.5    = Less detail (smaller files)
```

## 🧪 **Material Properties**

### **Water Properties** (`constant/thermophysicalProperties.water`)
```cpp
// Density
rho             998.2;     // kg/m³

// Heat capacity
Cp              4182;      // J/(kg·K)

// Viscosity
mu              1.002e-3;  // Pa·s
```

### **Phase Change** (`constant/phaseChangeProperties`)
```cpp
// Evaporation/condensation rates
condensationCoeff   0.1;   // Higher = faster condensation
evaporationCoeff    0.1;   // Higher = faster boiling

// Latent heat
latentHeat         2.26e6; // J/kg (energy for phase change)
```

## 🔧 **Common Modifications**

### **Scenario 1: Gentle Heating**
```bash
# Modify 0/T
gradient uniform 20000;     # Reduce heat flux
internalField uniform 293.15; # Start at 20°C
```

### **Scenario 2: Rapid Boiling**
```bash
# Modify 0/T
gradient uniform 150000;    # Increase heat flux
internalField uniform 363.15; # Start at 90°C (near boiling)
```

### **Scenario 3: Large Pool**
```bash
# Modify system/setFieldsDict
p2 (0 0 0.08);             # 8cm water depth
radius 0.08;               # 8cm radius

# Also update blockMeshDict vertices accordingly
```

### **Scenario 4: Long Simulation**
```bash
# Modify system/controlDict
endTime 30;                # 30 seconds
writeInterval 0.5;         # Save every 0.5s (less storage)
```

## 🚨 **Important Notes**

### **After Changing Parameters:**
1. **Clean the case**: `./Allclean`
2. **Regenerate mesh**: `blockMesh`
3. **Reset initial conditions**: `setFields`
4. **Run simulation**: `compressibleInterFoam`

### **Units in OpenFOAM:**
- **Length**: meters (m)
- **Time**: seconds (s)
- **Temperature**: Kelvin (K)
- **Pressure**: Pascal (Pa)
- **Velocity**: m/s
- **Heat flux**: K/m (temperature gradient)

### **Stability Guidelines:**
- **Smaller time steps** = more stable but slower
- **Lower heat flux** = more stable
- **Finer mesh** = more accurate but slower
- **Start with conservative settings** and increase gradually

### **Mesh Considerations:**
If you change pool dimensions significantly, you may need to:
1. **Update blockMeshDict** vertices
2. **Adjust mesh resolution** (40 40 40) in blocks
3. **Regenerate mesh** with `blockMesh`

## 🎯 **Quick Start Examples**

### **Test Run (Fast)**
```bash
# In system/controlDict
endTime 2;
writeInterval 0.2;
```

### **Production Run (Detailed)**
```bash
# In system/controlDict
endTime 20;
writeInterval 0.05;
deltaT 0.0005;
```

Remember: Always run `./Allclean && ./Allrun` after making changes to ensure all modifications take effect!
