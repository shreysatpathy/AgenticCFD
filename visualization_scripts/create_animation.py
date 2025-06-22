#!/usr/bin/env python3
"""
ParaView Python script to create animated GIF of boiling pool simulation
Shows temperature contours and velocity vectors over time
"""

import os
import sys

# Try to import paraview modules
try:
    from paraview.simple import *
    from paraview import servermanager
except ImportError:
    print("Error: ParaView Python modules not found.")
    print("Make sure you're running this script with ParaView's Python interpreter.")
    print("Usage: pvpython create_animation.py")
    sys.exit(1)

def create_boiling_animation():
    """Create animated GIF of boiling pool simulation"""
    
    # Disable automatic camera reset on 'Show'
    paraview.simple._DisableFirstRenderCameraReset()
    
    # Create a new 'OpenFOAM Reader'
    print("Loading OpenFOAM case...")
    case_foam = OpenFOAMReader(FileName='case.foam')
    case_foam.MeshRegions = ['internalMesh']
    case_foam.CellArrays = ['T', 'U', 'alpha.water', 'p_rgh']
    
    # Get animation scene
    animationScene1 = GetAnimationScene()
    
    # Update animation scene based on data timesteps
    animationScene1.UpdateAnimationUsingDataTimeSteps()
    
    # Get active view
    renderView1 = GetActiveViewOrCreate('RenderView')
    renderView1.ViewSize = [1200, 800]
    renderView1.Background = [1.0, 1.0, 1.0]  # White background
    
    # Show data in view
    case_foamDisplay = Show(case_foam, renderView1, 'UnstructuredGridRepresentation')
    
    # Set representation to surface
    case_foamDisplay.Representation = 'Surface'
    
    # Color by temperature
    ColorBy(case_foamDisplay, ('POINTS', 'T'))
    
    # Get color transfer function for temperature
    tLUT = GetColorTransferFunction('T')
    tLUT.RGBPoints = [298.15, 0.0, 0.0, 1.0,  # Blue for 25°C
                      350.0, 0.0, 1.0, 0.0,   # Green for intermediate
                      373.15, 1.0, 1.0, 0.0,  # Yellow for 100°C
                      400.0, 1.0, 0.0, 0.0]   # Red for >100°C
    tLUT.ColorSpace = 'HSV'
    
    # Show color bar
    tLUTColorBar = GetScalarBar(tLUT, renderView1)
    tLUTColorBar.Title = 'Temperature [K]'
    tLUTColorBar.ComponentTitle = ''
    tLUTColorBar.Position = [0.85, 0.1]
    tLUTColorBar.ScalarBarLength = 0.8
    case_foamDisplay.SetScalarBarVisibility(renderView1, True)
    
    # Create velocity vectors
    print("Creating velocity vectors...")
    glyph1 = Glyph(Input=case_foam, GlyphType='Arrow')
    glyph1.OrientationArray = ['POINTS', 'U']
    glyph1.ScaleArray = ['POINTS', 'U']
    glyph1.ScaleFactor = 0.01
    glyph1.GlyphMode = 'Every Nth Point'
    glyph1.Stride = 5  # Show every 5th point to avoid clutter
    
    # Show velocity vectors
    glyph1Display = Show(glyph1, renderView1, 'GeometryRepresentation')
    glyph1Display.Representation = 'Surface'
    
    # Color vectors by velocity magnitude
    ColorBy(glyph1Display, ('POINTS', 'U', 'Magnitude'))
    
    # Get color transfer function for velocity
    uLUT = GetColorTransferFunction('U')
    uLUT.RGBPoints = [0.0, 0.0, 0.0, 0.0,     # Black for zero velocity
                      0.1, 0.0, 0.0, 1.0,     # Blue for low velocity
                      0.5, 0.0, 1.0, 1.0,     # Cyan for medium velocity
                      1.0, 1.0, 1.0, 0.0,     # Yellow for high velocity
                      2.0, 1.0, 0.0, 0.0]     # Red for very high velocity
    
    # Add water surface (alpha.water = 0.5 isosurface)
    print("Creating water surface...")
    contour1 = Contour(Input=case_foam)
    contour1.ContourBy = ['POINTS', 'alpha.water']
    contour1.Isosurfaces = [0.5]
    
    # Show water surface
    contour1Display = Show(contour1, renderView1, 'GeometryRepresentation')
    contour1Display.Representation = 'Surface'
    contour1Display.ColorArrayName = [None, '']
    contour1Display.DiffuseColor = [0.0, 0.5, 1.0]  # Light blue
    contour1Display.Opacity = 0.3
    
    # Set camera position for good view
    renderView1.CameraPosition = [0.15, 0.15, 0.15]
    renderView1.CameraFocalPoint = [0.0, 0.0, 0.05]
    renderView1.CameraViewUp = [0.0, 0.0, 1.0]
    
    # Reset camera to fit data
    renderView1.ResetCamera()
    
    # Add title
    text1 = Text()
    text1.Text = 'Boiling Pool Simulation: Temperature & Velocity'
    text1Display = Show(text1, renderView1, 'TextSourceRepresentation')
    text1Display.FontSize = 18
    text1Display.Position = [0.1, 0.9]
    
    # Set up animation
    print("Setting up animation...")
    animationScene1.PlayMode = 'Sequence'
    animationScene1.NumberOfFrames = 100  # Adjust based on your timesteps
    
    # Create output directory
    output_dir = 'animation_frames'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save animation frames
    print(f"Saving animation frames to {output_dir}/...")
    SaveAnimation(f'{output_dir}/frame.png', renderView1, 
                  ImageResolution=[1200, 800],
                  FrameWindow=[0, animationScene1.NumberOfFrames-1])
    
    print("Animation frames saved successfully!")
    print(f"Frames saved in: {os.path.abspath(output_dir)}")
    
    return output_dir

def create_gif_from_frames(frame_dir, output_gif='boiling_simulation.gif'):
    """Convert PNG frames to animated GIF"""
    try:
        from PIL import Image
        import glob
        
        print(f"Creating GIF from frames in {frame_dir}...")
        
        # Get all PNG files and sort them
        frame_files = sorted(glob.glob(os.path.join(frame_dir, '*.png')))
        
        if not frame_files:
            print("No PNG frames found!")
            return False
        
        # Load images
        images = []
        for frame_file in frame_files:
            img = Image.open(frame_file)
            images.append(img)
        
        # Save as animated GIF
        images[0].save(output_gif,
                      save_all=True,
                      append_images=images[1:],
                      duration=200,  # 200ms per frame
                      loop=0)
        
        print(f"GIF created successfully: {output_gif}")
        return True
        
    except ImportError:
        print("PIL (Pillow) not available. Install with: pip install Pillow")
        print("Alternatively, use ImageMagick to create GIF:")
        print(f"convert -delay 20 -loop 0 {frame_dir}/*.png {output_gif}")
        return False
    except Exception as e:
        print(f"Error creating GIF: {e}")
        return False

if __name__ == "__main__":
    print("Starting ParaView animation script...")
    print("Make sure your OpenFOAM simulation has completed and results are available.")
    
    try:
        # Create animation frames
        frame_dir = create_boiling_animation()
        
        # Try to create GIF
        if not create_gif_from_frames(frame_dir):
            print("\nManual GIF creation:")
            print("You can create the GIF manually using ImageMagick:")
            print(f"convert -delay 20 -loop 0 {frame_dir}/*.png boiling_simulation.gif")
            print("\nOr using ffmpeg:")
            print(f"ffmpeg -framerate 5 -pattern_type glob -i '{frame_dir}/*.png' -vf palettegen palette.png")
            print(f"ffmpeg -framerate 5 -pattern_type glob -i '{frame_dir}/*.png' -i palette.png -lavfi paletteuse boiling_simulation.gif")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure ParaView is properly installed and the case.foam file exists.")
