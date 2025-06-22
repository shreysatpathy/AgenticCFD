# Simple ParaView script to visualize boiling interface
# Run this in ParaView's Python shell

import paraview.simple as pvs

print("🌊 Simple Interface Visualization")

# Load the case (make sure ParaView is in the right directory)
print("📂 Loading case...")
case = pvs.OpenFOAMReader(FileName='case.foam')

# Update to see what's available
case.UpdatePipeline()

print("✅ Case loaded successfully!")
print(f"Timesteps: {len(case.TimestepValues)}")

# Show the case first
view = pvs.GetActiveViewOrCreate('RenderView')
caseDisplay = pvs.Show(case, view)

# Color by alpha.water if available
try:
    pvs.ColorBy(caseDisplay, ('CELLS', 'alpha.water'))
    print("✅ Colored by alpha.water (cells)")
except:
    try:
        pvs.ColorBy(caseDisplay, ('POINTS', 'alpha.water'))
        print("✅ Colored by alpha.water (points)")
    except:
        print("⚠️  Could not color by alpha.water, using default")

# Reset camera for good view
view.ResetCamera()

# Create contour for interface
print("🔍 Creating interface contour...")
try:
    contour = pvs.Contour(Input=case)
    contour.ContourBy = ['CELLS', 'alpha.water']
    contour.Isosurfaces = [0.5]
    
    # Show the contour
    contourDisplay = pvs.Show(contour, view)
    contourDisplay.Representation = 'Surface'
    
    # Color the contour
    pvs.ColorBy(contourDisplay, ('POINTS', 'alpha.water'))
    
    print("✅ Interface contour created!")
    
except Exception as e:
    print(f"⚠️  Contour failed: {e}")
    print("💡 Try manually: Filters → Contour → alpha.water = 0.5")

# Render the view
pvs.Render()

print("🎉 Visualization complete!")
print("💡 Use the time controls to animate through timesteps")
print("💡 Try changing the contour value if no interface is visible")
