#!/usr/bin/env python3
"""
Simple Boiling Interface GIF Generator
Creates a focused animation showing the water-vapor interface evolution
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

def read_openfoam_scalar_field(filepath, expected_cells=64000):
    """Read OpenFOAM scalar field data"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Find the data section
        lines = content.split('\n')
        data_values = []
        in_data_section = False
        
        for line in lines:
            line = line.strip()
            if 'internalField' in line and 'nonuniform' in line:
                in_data_section = True
                continue
            elif in_data_section:
                if line == ')' or line == ');':
                    break
                elif line and not line.startswith('(') and line.isdigit() == False:
                    try:
                        value = float(line)
                        data_values.append(value)
                    except ValueError:
                        if line.isdigit():
                            continue  # Skip the count line
        
        # Ensure we have the right number of values
        if len(data_values) != expected_cells:
            print(f"Warning: Expected {expected_cells}, got {len(data_values)} values")
            if len(data_values) < expected_cells:
                data_values.extend([0.0] * (expected_cells - len(data_values)))
            else:
                data_values = data_values[:expected_cells]
        
        return np.array(data_values)
    
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return np.zeros(expected_cells)

def create_boiling_frame(time_dir, nx=40, ny=40, nz=40):
    """Create a single frame showing the boiling interface"""
    
    # Read alpha.water field
    alpha_file = os.path.join(time_dir, 'alpha.water')
    temp_file = os.path.join(time_dir, 'T')
    
    if not os.path.exists(alpha_file):
        print(f"Missing alpha.water in {time_dir}")
        return None
    
    # Read the fields
    alpha_data = read_openfoam_scalar_field(alpha_file)
    alpha_3d = alpha_data.reshape((nz, ny, nx))
    
    temp_data = None
    if os.path.exists(temp_file):
        temp_data = read_openfoam_scalar_field(temp_file)
        temp_3d = temp_data.reshape((nz, ny, nx))
    
    # Find the most interesting slice (with interface activity)
    best_slice = nz // 4  # Start with lower quarter
    max_interface = 0
    
    for k in range(nz):
        slice_2d = alpha_3d[k, :, :]
        interface_cells = np.sum((slice_2d > 0.1) & (slice_2d < 0.9))
        if interface_cells > max_interface:
            max_interface = interface_cells
            best_slice = k
    
    # Extract the slice
    alpha_slice = alpha_3d[best_slice, :, :]
    
    # Create coordinate arrays (in cm)
    x = np.linspace(-5, 5, nx)
    y = np.linspace(-5, 5, ny)
    X, Y = np.meshgrid(x, y)
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left plot: Interface with temperature if available
    if temp_data is not None:
        temp_slice = temp_3d[best_slice, :, :]
        # Temperature background
        temp_plot = ax1.contourf(X, Y, temp_slice, levels=15, cmap='hot', alpha=0.8)
        plt.colorbar(temp_plot, ax=ax1, label='Temperature (K)')
    
    # Interface contours
    levels = [0.1, 0.5, 0.9]
    colors = ['cyan', 'blue', 'navy']
    contours = ax1.contour(X, Y, alpha_slice, levels=levels, colors=colors, linewidths=2)
    ax1.clabel(contours, inline=True, fontsize=10)
    
    # Water region overlay
    water_mask = alpha_slice > 0.5
    ax1.contourf(X, Y, water_mask.astype(float), levels=[0.5, 1.5], 
                colors=['lightblue'], alpha=0.4)
    
    time_val = float(os.path.basename(time_dir))
    z_height = best_slice * 10.0 / nz  # Height in cm
    
    ax1.set_title(f'Boiling Interface + Temperature\nTime: {time_val:.3f}s, Height: {z_height:.1f}cm')
    ax1.set_xlabel('X Position (cm)')
    ax1.set_ylabel('Y Position (cm)')
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    
    # Right plot: Pure interface
    interface_plot = ax2.contourf(X, Y, alpha_slice, levels=20, cmap='RdYlBu_r', vmin=0, vmax=1)
    ax2.contour(X, Y, alpha_slice, levels=[0.5], colors=['black'], linewidths=3)
    plt.colorbar(interface_plot, ax=ax2, label='Water Volume Fraction')
    
    ax2.set_title(f'Water Volume Fraction\nTime: {time_val:.3f}s')
    ax2.set_xlabel('X Position (cm)')
    ax2.set_ylabel('Y Position (cm)')
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def create_boiling_gif(case_dir='.', output_file='boiling_interface.gif', fps=6):
    """Create GIF animation of boiling interface evolution"""
    
    print("🔥 Creating Boiling Interface Animation")
    print("=" * 40)
    
    # Find all time directories
    time_dirs = []
    for item in os.listdir(case_dir):
        try:
            time_val = float(item)
            time_path = os.path.join(case_dir, item)
            if os.path.isdir(time_path) and os.path.exists(os.path.join(time_path, 'alpha.water')):
                time_dirs.append((time_val, time_path))
        except ValueError:
            continue
    
    time_dirs.sort()
    print(f"Found {len(time_dirs)} time steps")
    
    if len(time_dirs) < 2:
        print("❌ Need at least 2 time steps!")
        return
    
    # Create frames (skip some for smoother animation)
    skip = max(1, len(time_dirs) // 30)  # Limit to ~30 frames
    selected_dirs = time_dirs[::skip]
    
    print(f"Creating {len(selected_dirs)} frames...")
    
    frame_files = []
    for i, (time_val, time_dir) in enumerate(selected_dirs):
        print(f"Frame {i+1}/{len(selected_dirs)}: t={time_val:.3f}s", end='\r')
        
        try:
            fig = create_boiling_frame(time_dir)
            if fig is not None:
                frame_file = f'frame_{i:04d}.png'
                fig.savefig(frame_file, dpi=100, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
                frame_files.append(frame_file)
                plt.close(fig)
        except Exception as e:
            print(f"\nError creating frame {i}: {e}")
            continue
    
    print(f"\n📽️  Assembling GIF...")
    
    # Create GIF
    if frame_files:
        images = []
        for frame_file in frame_files:
            if os.path.exists(frame_file):
                img = Image.open(frame_file)
                images.append(img)
        
        if images:
            duration = int(1000 / fps)
            images[0].save(output_file, save_all=True, append_images=images[1:],
                         duration=duration, loop=0, optimize=True)
            
            print(f"✅ Animation saved: {output_file}")
            print(f"📊 Stats: {len(images)} frames, {len(images)/fps:.1f}s duration")
            
            # Clean up
            for frame_file in frame_files:
                if os.path.exists(frame_file):
                    os.remove(frame_file)
        else:
            print("❌ No valid images created!")
    else:
        print("❌ No frames created!")

if __name__ == "__main__":
    create_boiling_gif(output_file='simple_boiling_animation.gif', fps=8)
    print("\n🎉 Done! Check the GIF file for the boiling animation.")
