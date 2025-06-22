# ParaView Python script to visualize boiling interface
# Run this in ParaView's Python shell or as a macro

import paraview.simple as pvs

print("🌊 Starting interface visualization...")

try:
    # Clear any existing data safely
    sources = pvs.GetSources()
    if sources:
        for source in sources.values():
            pvs.Delete(source)

    # Load the case
    print("📂 Loading OpenFOAM case...")
    case = pvs.OpenFOAMReader(FileName='case.foam')
    case.MeshRegions = ['internalMesh']
    # Don't force specific arrays, let it auto-detect
    case.UpdatePipeline()

    print(f"✅ Loaded {len(case.TimestepValues)} timesteps")
    print(f"📊 Available cell arrays: {case.CellArrays}")
    print(f"📊 Available point arrays: {case.PointArrays}")

    # Check if alpha.water exists
    if 'alpha.water' not in case.CellArrays:
        print("⚠️  alpha.water not found in cell arrays, checking point arrays...")
        if 'alpha.water' not in case.PointArrays:
            print("❌ alpha.water field not found!")
            print("Available fields:", case.CellArrays + case.PointArrays)
            raise Exception("alpha.water field not available")

    # Create interface contour
    print("🔍 Creating interface contour at alpha.water = 0.5...")
    contour = pvs.Contour(Input=case)

    # Use CELLS if available, otherwise POINTS
    if 'alpha.water' in case.CellArrays:
        contour.ContourBy = ['CELLS', 'alpha.water']
    else:
        contour.ContourBy = ['POINTS', 'alpha.water']

    contour.Isosurfaces = [0.5]  # Interface at alpha.water = 0.5
    contour.UpdatePipeline()

    # Color by alpha.water
    pvs.ColorBy(contour, ('POINTS', 'alpha.water'))

    # Set up the view
    view = pvs.GetActiveViewOrCreate('RenderView')
    view.ResetCamera()

    # Create a nice color map for the interface
    colorMap = pvs.GetColorTransferFunction('alpha.water')
    colorMap.RGBPoints = [0.0, 0.2, 0.2, 1.0,  # Blue for air
                          0.5, 0.0, 1.0, 0.0,  # Green for interface
                          1.0, 1.0, 0.2, 0.0]  # Red for water

    # Show the interface
    contourDisplay = pvs.Show(contour, view)
    contourDisplay.Representation = 'Surface'

    # Also show the original data as wireframe for context
    caseDisplay = pvs.Show(case, view)
    caseDisplay.Representation = 'Wireframe'
    caseDisplay.Opacity = 0.1

    # Set camera for good view
    view.CameraPosition = [0.2, 0.2, 0.3]
    view.CameraFocalPoint = [0.0, 0.0, 0.05]
    view.CameraViewUp = [0.0, 0.0, 1.0]
    view.ResetCamera()

    pvs.Render()

    print("🎉 Interface visualization created successfully!")
    print("💡 Tips:")
    print("  - Use the time controls to animate through timesteps")
    print("  - Green surface shows the water-air interface")
    print("  - Try Filters → Glyph to add velocity vectors")
    print("  - Use Filters → Slice to see internal temperature")

except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 Make sure ParaView is open and case.foam exists")
