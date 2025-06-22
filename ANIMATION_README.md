# Boiling Pool Simulation Animation Guide

This guide explains how to create animated GIFs of your boiling pool simulation showing temperature contours and velocity vectors.

## 📁 Animation Scripts

### Main Scripts:
- **`create_animation.py`** - Full-featured ParaView Python script
- **`simple_animation.py`** - Simplified version for basic setups
- **`create_gif.sh`** - Linux/WSL bash script
- **`create_gif.bat`** - Windows batch script

## 🚀 Quick Start

### Option 1: Windows (Recommended)
```cmd
# Run the Windows batch script
create_gif.bat
```

### Option 2: WSL/Linux
```bash
# Run the bash script
./create_gif.sh
```

### Option 3: Manual ParaView
```bash
# In WSL Ubuntu
cd /mnt/c/Users/User/Surfing/flows
. /opt/openfoam11/etc/bashrc
pvpython create_animation.py
```

## 📋 Prerequisites

### Required:
1. **Completed OpenFOAM simulation** - Run `./Allrun` first
2. **ParaView** - Already installed with OpenFOAM
3. **Simulation results** - Time directories (0.1, 0.2, etc.)

### Optional (for GIF creation):
- **ImageMagick**: `sudo apt install imagemagick` (in WSL)
- **FFmpeg**: `sudo apt install ffmpeg` (in WSL)
- **Python Pillow**: `pip install Pillow` (in WSL)

## 🎬 What the Animation Shows

The generated GIF will display:

### 🌡️ **Temperature Field**
- **Blue**: Cold water (25°C / 298K)
- **Cyan**: Warming water (~60°C)
- **Yellow**: Hot water (100°C / 373K)
- **Red**: Superheated regions (>100°C)

### 🏹 **Velocity Vectors**
- **Arrows**: Show flow direction and magnitude
- **Colors**: Velocity magnitude (blue=slow, red=fast)
- **Density**: Every 5th-8th grid point (to avoid clutter)

### 💧 **Water Surface** (if enabled)
- **Light blue transparent surface**: Water-air interface
- **Isosurface**: alpha.water = 0.5

## ⚙️ Customization Options

### Modify Animation Settings

Edit `create_animation.py` to customize:

```python
# Animation duration
animationScene1.NumberOfFrames = 100  # More frames = longer animation

# Vector density
glyph1.Stride = 5  # Lower = more vectors, higher = fewer vectors

# Temperature color range
tLUT.RGBPoints = [298.15, 0.0, 0.0, 1.0,  # Min temp, R, G, B
                  373.15, 1.0, 0.0, 0.0]   # Max temp, R, G, B

# Image resolution
ImageResolution=[1200, 800]  # Width x Height
```

### GIF Settings

Modify GIF creation parameters:

```bash
# ImageMagick
convert -delay 20 -loop 0 animation_frames/*.png output.gif
#        ↑delay   ↑loop forever

# FFmpeg
ffmpeg -framerate 5 -i frames/*.png output.gif
#       ↑frames per second
```

## 🔧 Troubleshooting

### Common Issues:

#### 1. "ParaView not found"
```bash
# In WSL, source OpenFOAM environment
. /opt/openfoam11/etc/bashrc
which pvpython  # Should show path
```

#### 2. "No time directories found"
```bash
# Run simulation first
./Allrun
# Or check if results exist
ls -la [0-9]*
```

#### 3. "Cannot create GIF"
```bash
# Install ImageMagick in WSL
sudo apt update
sudo apt install imagemagick

# Or install FFmpeg
sudo apt install ffmpeg

# Or use online tools with the PNG frames
```

#### 4. "Script fails with errors"
- Check that `case.foam` exists in current directory
- Ensure simulation has completed successfully
- Try the simplified script: `pvpython simple_animation.py`

### Performance Tips:

#### For Large Simulations:
```python
# Reduce frame count
animationScene1.NumberOfFrames = 50

# Lower resolution
ImageResolution=[800, 600]

# Fewer vectors
glyph1.Stride = 10
```

#### For Better Quality:
```python
# More frames
animationScene1.NumberOfFrames = 200

# Higher resolution
ImageResolution=[1600, 1200]

# More vectors
glyph1.Stride = 3
```

## 📊 Expected Output

### File Structure After Running:
```
flows/
├── animation_frames/          # PNG frames
│   ├── frame.0000.png
│   ├── frame.0001.png
│   └── ...
├── boiling_simulation.gif     # Final animated GIF
├── case.foam                  # ParaView case file
└── [simulation results]
```

### Typical File Sizes:
- **PNG frames**: 100-500 KB each
- **Final GIF**: 5-50 MB (depends on frames/resolution)
- **Animation duration**: 5-20 seconds

## 🎯 Advanced Usage

### Custom Views:
```python
# Top view
renderView1.CameraPosition = [0.0, 0.0, 0.3]
renderView1.CameraFocalPoint = [0.0, 0.0, 0.05]
renderView1.CameraViewUp = [0.0, 1.0, 0.0]

# Side view
renderView1.CameraPosition = [0.2, 0.0, 0.05]
renderView1.CameraFocalPoint = [0.0, 0.0, 0.05]
renderView1.CameraViewUp = [0.0, 0.0, 1.0]
```

### Multiple Variables:
```python
# Add pressure contours
pressure_contour = Contour(Input=case_foam)
pressure_contour.ContourBy = ['POINTS', 'p_rgh']
pressure_contour.Isosurfaces = [101325, 102000, 103000]
```

### Export Individual Frames:
```python
# Save specific timestep
animationScene1.AnimationTime = 5.0  # 5 seconds
SaveScreenshot('timestep_5s.png', renderView1)
```

## 🆘 Getting Help

If you encounter issues:

1. **Check the terminal output** for specific error messages
2. **Verify simulation completed** - look for time directories
3. **Try the simple script** first: `simple_animation.py`
4. **Check ParaView installation**: `pvpython --version`
5. **Use manual ParaView** - open `case.foam` in ParaView GUI

## 📚 Additional Resources

- [ParaView Documentation](https://www.paraview.org/documentation/)
- [OpenFOAM User Guide](https://openfoam.org/guide/)
- [ParaView Python Scripting](https://kitware.github.io/paraview-docs/latest/python/)

The animation will help you visualize the complex physics of boiling, including bubble formation, natural convection, and heat transfer patterns!
