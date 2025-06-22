#!/usr/bin/env python3
"""
Ultimate 3D Boiling Visualization
Creates stunning 3D visualizations with temperature-colored interface and transparent cube
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import os
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

def read_field_robust(filepath, expected_cells=64000):
    """Robust OpenFOAM field reader"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract numeric values
        lines = content.split('\n')
        values = []
        in_data = False
        
        for line in lines:
            line = line.strip()
            if 'internalField' in line and 'nonuniform' in line:
                in_data = True
                continue
            elif in_data and (line == ')' or line == ');'):
                break
            elif in_data and line:
                try:
                    if not line.startswith('(') and not line.isdigit():
                        val = float(line)
                        values.append(val)
                except ValueError:
                    continue
        
        # Pad or truncate to expected size
        if len(values) < expected_cells:
            values.extend([values[-1] if values else 0.0] * (expected_cells - len(values)))
        elif len(values) > expected_cells:
            values = values[:expected_cells]
            
        return np.array(values)
    
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return np.zeros(expected_cells)

def create_ultimate_3d_viz(time_val, case_dir='.', nx=40, ny=40, nz=40):
    """Create ultimate 3D visualization"""
    
    # Read data
    time_dir = str(time_val)
    alpha_file = os.path.join(case_dir, time_dir, 'alpha.water')
    temp_file = os.path.join(case_dir, time_dir, 'T')
    
    alpha_data = read_field_robust(alpha_file)
    temp_data = read_field_robust(temp_file)
    
    # Reshape to 3D
    alpha_3d = alpha_data.reshape((nz, ny, nx))
    temp_3d = temp_data.reshape((nz, ny, nx))
    
    # Create coordinates (in cm)
    x = np.linspace(-5, 5, nx)
    y = np.linspace(-5, 5, ny)
    z = np.linspace(0, 10, nz)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    
    # Create figure
    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    # Draw transparent cube wireframe
    cube_x = [-5, 5, 5, -5, -5, 5, 5, -5]
    cube_y = [-5, -5, 5, 5, -5, -5, 5, 5]
    cube_z = [0, 0, 0, 0, 10, 10, 10, 10]
    
    # Cube edges
    edges = [
        [0,1], [1,2], [2,3], [3,0],  # bottom
        [4,5], [5,6], [6,7], [7,4],  # top
        [0,4], [1,5], [2,6], [3,7]   # vertical
    ]
    
    for edge in edges:
        points = np.array([cube_x, cube_y, cube_z])
        ax.plot3D(*points[:, edge], 'k-', alpha=0.4, linewidth=2)
    
    # Sample data for visualization (every 2nd point for performance)
    step = 2
    x_sub = x[::step]
    y_sub = y[::step]
    z_sub = z[::step]
    alpha_sub = alpha_3d[::step, ::step, ::step]
    temp_sub = temp_3d[::step, ::step, ::step]
    X_sub, Y_sub, Z_sub = np.meshgrid(x_sub, y_sub, z_sub, indexing='ij')
    
    # Temperature range for coloring
    temp_min, temp_max = temp_sub.min(), temp_sub.max()
    temp_range = temp_max - temp_min
    
    # 1. Water phase (alpha > 0.8) - Blue with temperature variation
    water_mask = alpha_sub > 0.8
    if np.any(water_mask):
        x_water = X_sub[water_mask]
        y_water = Y_sub[water_mask]
        z_water = Z_sub[water_mask]
        temp_water = temp_sub[water_mask]
        
        # Normalize temperature for coloring
        temp_norm = (temp_water - temp_min) / (temp_range + 1e-10)
        colors_water = plt.cm.Blues(0.3 + 0.7 * temp_norm)
        
        ax.scatter(x_water, y_water, z_water, c=colors_water, s=15, alpha=0.6)
    
    # 2. Interface region (0.2 < alpha < 0.8) - Temperature colored
    interface_mask = (alpha_sub > 0.2) & (alpha_sub < 0.8)
    if np.any(interface_mask):
        x_interface = X_sub[interface_mask]
        y_interface = Y_sub[interface_mask]
        z_interface = Z_sub[interface_mask]
        temp_interface = temp_sub[interface_mask]
        
        # Use hot colormap for interface
        scatter = ax.scatter(x_interface, y_interface, z_interface, 
                           c=temp_interface, cmap='hot', s=25, alpha=0.9)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax, shrink=0.6, aspect=30, pad=0.1)
        cbar.set_label('Temperature (K)', fontsize=14, fontweight='bold')
    
    # 3. Vapor phase (alpha < 0.2) - Red with temperature variation
    vapor_mask = alpha_sub < 0.2
    if np.any(vapor_mask):
        x_vapor = X_sub[vapor_mask]
        y_vapor = Y_sub[vapor_mask]
        z_vapor = Z_sub[vapor_mask]
        temp_vapor = temp_sub[vapor_mask]
        
        # Normalize temperature for coloring
        temp_norm = (temp_vapor - temp_min) / (temp_range + 1e-10)
        colors_vapor = plt.cm.Reds(0.3 + 0.7 * temp_norm)
        
        ax.scatter(x_vapor, y_vapor, z_vapor, c=colors_vapor, s=8, alpha=0.5)
    
    # Add heated bottom surface indicator (simple plane)
    xx, yy = np.meshgrid([-5, 5], [-5, 5])
    zz = np.zeros_like(xx)
    ax.plot_surface(xx, yy, zz, color='red', alpha=0.2)
    
    # Styling
    ax.set_xlabel('X Position (cm)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Y Position (cm)', fontsize=14, fontweight='bold')
    ax.set_zlabel('Z Position (cm)', fontsize=14, fontweight='bold')
    
    title = f'🔥 3D Thermal Boiling Simulation 🔥\n'
    title += f'Time: {time_val:.3f}s | Temperature-Colored Interface'
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # Set viewing angle
    ax.view_init(elev=25, azim=45)
    
    # Set aspect ratio
    ax.set_box_aspect([1, 1, 2])
    
    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', 
                  markersize=10, alpha=0.7, label='💧 Water (α > 0.8)'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', 
                  markersize=10, alpha=0.9, label='🌡️ Interface (0.2 < α < 0.8)'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                  markersize=10, alpha=0.7, label='💨 Vapor (α < 0.2)'),
        plt.Line2D([0], [0], color='red', linewidth=3, alpha=0.5, 
                  label='🔥 Heated Bottom')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))
    
    return fig

def create_ultimate_3d_gif(case_dir='.', output_file='ultimate_3d_boiling.gif'):
    """Create ultimate 3D GIF animation"""
    
    print("🌟 Creating Ultimate 3D Boiling Animation")
    print("=" * 50)
    
    # Find time directories
    time_dirs = []
    for item in os.listdir(case_dir):
        try:
            time_val = float(item)
            time_path = os.path.join(case_dir, item)
            if (os.path.isdir(time_path) and 
                os.path.exists(os.path.join(time_path, 'alpha.water'))):
                time_dirs.append(time_val)
        except ValueError:
            continue
    
    time_dirs.sort()
    print(f"Found {len(time_dirs)} time steps")
    
    # Select frames (limit to ~25 frames for reasonable file size)
    skip = max(1, len(time_dirs) // 25)
    selected_times = time_dirs[::skip]
    
    print(f"Creating {len(selected_times)} frames...")
    
    frame_files = []
    for i, time_val in enumerate(selected_times):
        print(f"Frame {i+1}/{len(selected_times)}: t={time_val:.3f}s", end='\r')
        
        try:
            fig = create_ultimate_3d_viz(time_val, case_dir)
            frame_file = f'ultimate_frame_{i:03d}.png'
            plt.savefig(frame_file, dpi=120, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            frame_files.append(frame_file)
            plt.close(fig)
        except Exception as e:
            print(f"\nError creating frame {i}: {e}")
            continue
    
    print(f"\n🎬 Assembling ultimate GIF...")
    
    # Create GIF
    if frame_files:
        images = []
        for frame_file in frame_files:
            if os.path.exists(frame_file):
                img = Image.open(frame_file)
                images.append(img)
        
        if images:
            images[0].save(output_file, save_all=True, append_images=images[1:],
                         duration=250, loop=0, optimize=True)
            
            print(f"✅ Ultimate 3D GIF saved: {output_file}")
            print(f"📊 Stats: {len(images)} frames, {len(images)*0.25:.1f}s duration")
            
            # Clean up
            for frame_file in frame_files:
                if os.path.exists(frame_file):
                    os.remove(frame_file)
        else:
            print("❌ No valid images created!")
    else:
        print("❌ No frames created!")

if __name__ == "__main__":
    create_ultimate_3d_gif()
    print("\n🎉 Ultimate 3D visualization complete!")
    print("🔍 Features:")
    print("   - 💧 Blue points: Water phase")
    print("   - 🌡️ Hot colors: Interface (temperature-colored)")
    print("   - 💨 Red points: Vapor phase")
    print("   - 🔥 Red surface: Heated bottom")
    print("   - ⬛ Black wireframe: Domain boundaries")
