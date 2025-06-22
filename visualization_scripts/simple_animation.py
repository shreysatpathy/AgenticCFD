#!/usr/bin/env python3
"""
Simplified ParaView Python script for creating boiling pool animation
This version focuses on essential visualization elements
"""

import os
import sys

def create_simple_animation():
    """Create a simple animation with temperature and velocity"""
    
    try:
        from paraview.simple import *
    except ImportError:
        print("Error: ParaView Python modules not found.")
        print("Run with: pvpython simple_animation.py")
        return False
    
    print("Creating simple boiling pool animation...")
    
    # Disable automatic camera reset
    paraview.simple._DisableFirstRenderCameraReset()
    
    # Load OpenFOAM case
    print("Loading case...")
    reader = OpenFOAMReader(FileName='case.foam')
    reader.MeshRegions = ['internalMesh']
    reader.CellArrays = ['T', 'U', 'alpha.water']
    
    # Get animation scene and update with data timesteps
    scene = GetAnimationScene()
    scene.UpdateAnimationUsingDataTimeSteps()
    
    # Create render view
    view = CreateView('RenderView')
    view.ViewSize = [1000, 800]
    view.Background = [0.2, 0.2, 0.2]  # Dark gray background
    
    # Show the data
    display = Show(reader, view)
    
    # Color by temperature
    ColorBy(display, ('POINTS', 'T'))
    
    # Set up temperature color map
    temp_lut = GetColorTransferFunction('T')
    temp_lut.RGBPoints = [
        298.15, 0.0, 0.0, 1.0,  # Blue for 25°C
        335.0, 0.0, 1.0, 1.0,   # Cyan
        373.15, 1.0, 1.0, 0.0,  # Yellow for 100°C
        400.0, 1.0, 0.0, 0.0    # Red for >100°C
    ]
    
    # Show color bar
    color_bar = GetScalarBar(temp_lut, view)
    color_bar.Title = 'Temperature [K]'
    color_bar.Position = [0.85, 0.2]
    color_bar.ScalarBarLength = 0.6
    display.SetScalarBarVisibility(view, True)
    
    # Create velocity vectors (simplified)
    print("Adding velocity vectors...")
    glyph = Glyph(Input=reader, GlyphType='Arrow')
    glyph.OrientationArray = ['POINTS', 'U']
    glyph.ScaleArray = ['POINTS', 'U']
    glyph.ScaleFactor = 0.005
    glyph.GlyphMode = 'Every Nth Point'
    glyph.Stride = 8  # Every 8th point
    
    # Show velocity vectors
    glyph_display = Show(glyph, view)
    glyph_display.Representation = 'Surface'
    
    # Color vectors by velocity magnitude
    ColorBy(glyph_display, ('POINTS', 'U', 'Magnitude'))
    
    # Set camera position
    view.CameraPosition = [0.1, 0.1, 0.2]
    view.CameraFocalPoint = [0.0, 0.0, 0.05]
    view.CameraViewUp = [0.0, 0.0, 1.0]
    view.ResetCamera()
    
    # Create output directory
    output_dir = 'simple_frames'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get number of timesteps
    timesteps = scene.TimeKeeper.TimestepValues
    num_frames = len(timesteps) if timesteps else 50
    
    print(f"Creating {num_frames} frames...")
    
    # Save frames
    for i in range(num_frames):
        scene.AnimationTime = timesteps[i] if timesteps else i * 0.1
        Render()
        SaveScreenshot(f'{output_dir}/frame_{i:04d}.png', view, 
                      ImageResolution=[1000, 800])
        
        if i % 10 == 0:
            print(f"  Saved frame {i+1}/{num_frames}")
    
    print(f"Animation frames saved to: {output_dir}/")
    return output_dir

def create_gif_simple(frame_dir):
    """Simple GIF creation using available tools"""
    
    import subprocess
    import glob
    
    frames = sorted(glob.glob(os.path.join(frame_dir, '*.png')))
    if not frames:
        print("No frames found!")
        return False
    
    print(f"Found {len(frames)} frames")
    
    # Try ImageMagick
    try:
        cmd = ['convert', '-delay', '20', '-loop', '0'] + frames + ['simple_boiling.gif']
        subprocess.run(cmd, check=True)
        print("✓ GIF created with ImageMagick: simple_boiling.gif")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try ffmpeg
    try:
        # Create palette
        subprocess.run([
            'ffmpeg', '-y', '-framerate', '5', '-pattern_type', 'glob',
            '-i', f'{frame_dir}/*.png', '-vf', 'palettegen', 'palette.png'
        ], check=True)
        
        # Create GIF
        subprocess.run([
            'ffmpeg', '-y', '-framerate', '5', '-pattern_type', 'glob',
            '-i', f'{frame_dir}/*.png', '-i', 'palette.png',
            '-lavfi', 'paletteuse', 'simple_boiling.gif'
        ], check=True)
        
        os.remove('palette.png')
        print("✓ GIF created with ffmpeg: simple_boiling.gif")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    print("Could not create GIF automatically.")
    print("Install ImageMagick or ffmpeg, or use online tools.")
    return False

if __name__ == "__main__":
    if not os.path.exists('case.foam'):
        print("Error: case.foam not found!")
        print("Run this script from your OpenFOAM case directory.")
        sys.exit(1)
    
    try:
        frame_dir = create_simple_animation()
        if frame_dir:
            create_gif_simple(frame_dir)
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure ParaView is properly installed.")
        sys.exit(1)
