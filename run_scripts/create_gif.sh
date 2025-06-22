#!/bin/bash

# Script to create animated GIF of boiling pool simulation
# Shows temperature contours and velocity vectors

echo "=== Boiling Pool Simulation GIF Creator ==="
echo ""

# Check if OpenFOAM environment is sourced
if ! command -v pvpython &> /dev/null; then
    echo "Sourcing OpenFOAM environment..."
    source /opt/openfoam11/etc/bashrc
fi

# Check if case.foam exists
if [ ! -f "case.foam" ]; then
    echo "Error: case.foam file not found!"
    echo "Make sure you're in the OpenFOAM case directory."
    exit 1
fi

# Check if simulation results exist
if [ ! -d "0.1" ] && [ ! -d "1" ]; then
    echo "Warning: No time directories found. Make sure the simulation has been run."
    echo "Run the simulation first with: ./Allrun"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Creating animation frames with ParaView..."

# Run the ParaView Python script
if command -v pvpython &> /dev/null; then
    pvpython create_animation.py
else
    echo "Error: pvpython not found!"
    echo "Trying alternative method with paraview..."
    if command -v paraview &> /dev/null; then
        paraview --script=create_animation.py
    else
        echo "Error: ParaView not found in PATH!"
        echo "Make sure ParaView is properly installed."
        exit 1
    fi
fi

# Check if frames were created
if [ ! -d "animation_frames" ]; then
    echo "Error: Animation frames were not created!"
    exit 1
fi

frame_count=$(ls animation_frames/*.png 2>/dev/null | wc -l)
if [ $frame_count -eq 0 ]; then
    echo "Error: No PNG frames found!"
    exit 1
fi

echo "Found $frame_count animation frames."

# Try different methods to create GIF
echo "Creating animated GIF..."

# Method 1: Try ImageMagick
if command -v convert &> /dev/null; then
    echo "Using ImageMagick to create GIF..."
    convert -delay 20 -loop 0 animation_frames/*.png boiling_simulation.gif
    if [ $? -eq 0 ]; then
        echo "✓ GIF created successfully with ImageMagick: boiling_simulation.gif"
        echo "File size: $(du -h boiling_simulation.gif | cut -f1)"
        exit 0
    fi
fi

# Method 2: Try ffmpeg
if command -v ffmpeg &> /dev/null; then
    echo "Using ffmpeg to create GIF..."
    
    # Create palette for better quality
    ffmpeg -y -framerate 5 -pattern_type glob -i 'animation_frames/*.png' \
           -vf "fps=5,scale=800:-1:flags=lanczos,palettegen" palette.png
    
    # Create GIF with palette
    ffmpeg -y -framerate 5 -pattern_type glob -i 'animation_frames/*.png' \
           -i palette.png -filter_complex "fps=5,scale=800:-1:flags=lanczos[x];[x][1:v]paletteuse" \
           boiling_simulation.gif
    
    if [ $? -eq 0 ]; then
        echo "✓ GIF created successfully with ffmpeg: boiling_simulation.gif"
        echo "File size: $(du -h boiling_simulation.gif | cut -f1)"
        rm -f palette.png
        exit 0
    fi
fi

# Method 3: Python with Pillow (if available)
echo "Trying Python with Pillow..."
python3 -c "
import os
import glob
from PIL import Image

try:
    frame_files = sorted(glob.glob('animation_frames/*.png'))
    if not frame_files:
        print('No frames found!')
        exit(1)
    
    images = [Image.open(f) for f in frame_files]
    images[0].save('boiling_simulation.gif',
                   save_all=True,
                   append_images=images[1:],
                   duration=200,
                   loop=0)
    print('✓ GIF created successfully with Python/Pillow: boiling_simulation.gif')
except ImportError:
    print('Pillow not available')
    exit(1)
except Exception as e:
    print(f'Error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "File size: $(du -h boiling_simulation.gif | cut -f1)"
    exit 0
fi

# If all methods failed
echo ""
echo "❌ Could not create GIF automatically."
echo ""
echo "Manual options:"
echo "1. Install ImageMagick: sudo apt install imagemagick"
echo "   Then run: convert -delay 20 -loop 0 animation_frames/*.png boiling_simulation.gif"
echo ""
echo "2. Install ffmpeg: sudo apt install ffmpeg"
echo "   Then run the ffmpeg commands shown above"
echo ""
echo "3. Install Python Pillow: pip install Pillow"
echo "   Then run the Python script again"
echo ""
echo "Animation frames are saved in: animation_frames/"
echo "You can view them individually or use any tool to create the GIF."

exit 1
