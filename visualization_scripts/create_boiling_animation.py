#!/usr/bin/env python3
"""
Advanced Boiling Interface Animation Generator
Creates a high-quality GIF showing the evolution of the water-vapor interface
during the thermal boiling simulation with temperature field overlay.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import os
import glob
import re
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

class BoilingAnimationGenerator:
    def __init__(self, case_dir='.', nx=40, ny=40, nz=40):
        """
        Initialize the animation generator
        
        Args:
            case_dir: OpenFOAM case directory
            nx, ny, nz: Grid dimensions
        """
        self.case_dir = case_dir
        self.nx, self.ny, self.nz = nx, ny, nz
        self.total_cells = nx * ny * nz
        
        # Physical domain (from blockMeshDict)
        self.x_range = (-0.05, 0.05)  # -5cm to +5cm
        self.y_range = (-0.05, 0.05)  # -5cm to +5cm  
        self.z_range = (0.0, 0.1)     # 0 to 10cm height
        
        # Create coordinate arrays
        self.x = np.linspace(self.x_range[0], self.x_range[1], nx)
        self.y = np.linspace(self.y_range[0], self.y_range[1], ny)
        self.z = np.linspace(self.z_range[0], self.z_range[1], nz)
        
        # Find all time directories
        self.time_dirs = self._find_time_directories()
        print(f"Found {len(self.time_dirs)} time steps: {self.time_dirs[:5]}...")
        
    def _find_time_directories(self):
        """Find all time directories with simulation data"""
        time_dirs = []
        for item in os.listdir(self.case_dir):
            try:
                # Check if it's a valid time directory
                time_val = float(item)
                time_path = os.path.join(self.case_dir, item)
                if os.path.isdir(time_path):
                    # Check if it has alpha.water file
                    alpha_file = os.path.join(time_path, 'alpha.water')
                    temp_file = os.path.join(time_path, 'T')
                    if os.path.exists(alpha_file) and os.path.exists(temp_file):
                        time_dirs.append(time_val)
                    else:
                        # Skip directories without required fields
                        print(f"Skipping {item}: missing alpha.water or T field")
            except ValueError:
                continue

        return sorted(time_dirs)
    
    def _read_openfoam_field(self, filepath):
        """Read OpenFOAM field data from file"""
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            # Find the start of data
            data_start = -1
            for i, line in enumerate(lines):
                if 'internalField' in line and 'nonuniform' in line:
                    # Find the number of cells
                    for j in range(i+1, min(i+5, len(lines))):
                        try:
                            num_cells = int(lines[j].strip())
                            if num_cells == self.total_cells:
                                data_start = j + 2  # Skip the opening parenthesis
                                break
                        except ValueError:
                            continue
                    break
            
            if data_start == -1:
                raise ValueError(f"Could not find data start in {filepath}")
            
            # Read the data values
            data = []
            for i in range(data_start, len(lines)):
                line = lines[i].strip()
                if line == ')' or line == ');':
                    break
                if line and not line.startswith('('):
                    try:
                        value = float(line)
                        data.append(value)
                    except ValueError:
                        continue
            
            if len(data) != self.total_cells:
                print(f"Warning: Expected {self.total_cells} cells, got {len(data)} in {filepath}")
                # Pad or truncate as needed
                if len(data) < self.total_cells:
                    data.extend([0.0] * (self.total_cells - len(data)))
                else:
                    data = data[:self.total_cells]
            
            # Reshape to 3D grid (OpenFOAM uses different ordering)
            data_3d = np.array(data).reshape((self.nz, self.ny, self.nx))
            return data_3d
            
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return np.zeros((self.nz, self.ny, self.nx))
    
    def _create_interface_slice(self, alpha_3d, temp_3d, z_slice_idx=None):
        """Create a 2D slice showing interface and temperature"""
        if z_slice_idx is None:
            # Find the slice with most interface activity (alpha between 0.1 and 0.9)
            interface_activity = []
            for k in range(self.nz):
                slice_2d = alpha_3d[k, :, :]
                interface_cells = np.sum((slice_2d > 0.1) & (slice_2d < 0.9))
                interface_activity.append(interface_cells)
            
            if max(interface_activity) > 0:
                z_slice_idx = np.argmax(interface_activity)
            else:
                z_slice_idx = self.nz // 3  # Lower third of domain
        
        alpha_slice = alpha_3d[z_slice_idx, :, :]
        temp_slice = temp_3d[z_slice_idx, :, :]
        
        return alpha_slice, temp_slice, z_slice_idx
    
    def create_animation_frame(self, time_val, ax1, ax2):
        """Create a single animation frame"""
        time_dir = str(time_val)
        
        # Read alpha.water and temperature fields
        alpha_file = os.path.join(self.case_dir, time_dir, 'alpha.water')
        temp_file = os.path.join(self.case_dir, time_dir, 'T')
        
        alpha_3d = self._read_openfoam_field(alpha_file)
        temp_3d = self._read_openfoam_field(temp_file)
        
        # Create 2D slices
        alpha_slice, temp_slice, z_idx = self._create_interface_slice(alpha_3d, temp_3d)
        
        # Clear previous plots
        ax1.clear()
        ax2.clear()
        
        # Create coordinate meshes for plotting
        X, Y = np.meshgrid(self.x * 100, self.y * 100)  # Convert to cm
        
        # Plot 1: Interface evolution with temperature overlay
        # Temperature background
        temp_plot = ax1.contourf(X, Y, temp_slice, levels=20, cmap='hot', alpha=0.7)
        
        # Interface contours
        interface_contours = ax1.contour(X, Y, alpha_slice, levels=[0.1, 0.5, 0.9], 
                                       colors=['cyan', 'blue', 'navy'], linewidths=[1, 2, 1])
        ax1.clabel(interface_contours, inline=True, fontsize=8, fmt='α=%.1f')
        
        # Water region (alpha > 0.5)
        water_mask = alpha_slice > 0.5
        ax1.contourf(X, Y, water_mask.astype(float), levels=[0.5, 1.5], 
                    colors=['lightblue'], alpha=0.3)
        
        ax1.set_title(f'Boiling Interface & Temperature\nTime: {time_val:.3f}s, Height: {self.z[z_idx]*100:.1f}cm')
        ax1.set_xlabel('X Position (cm)')
        ax1.set_ylabel('Y Position (cm)')
        ax1.set_aspect('equal')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Pure interface evolution
        interface_plot = ax2.contourf(X, Y, alpha_slice, levels=20, cmap='RdYlBu_r')
        ax2.contour(X, Y, alpha_slice, levels=[0.5], colors=['black'], linewidths=2)
        
        ax2.set_title(f'Water Volume Fraction (α)\nTime: {time_val:.3f}s')
        ax2.set_xlabel('X Position (cm)')
        ax2.set_ylabel('Y Position (cm)')
        ax2.set_aspect('equal')
        ax2.grid(True, alpha=0.3)
        
        return temp_plot, interface_plot
    
    def generate_gif_animation(self, output_file='boiling_animation.gif', 
                             fps=5, skip_frames=1):
        """Generate the complete GIF animation"""
        print("🎬 Creating boiling interface animation...")
        
        # Select time steps (skip some for faster animation)
        selected_times = self.time_dirs[::skip_frames]
        print(f"Animating {len(selected_times)} frames from t={selected_times[0]:.3f}s to t={selected_times[-1]:.3f}s")
        
        # Set up the figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        fig.suptitle('🔥 Thermal Boiling Simulation - Interface Evolution 🔥', 
                    fontsize=16, fontweight='bold')
        
        # Create frames
        frames = []
        for i, time_val in enumerate(selected_times):
            print(f"Processing frame {i+1}/{len(selected_times)}: t={time_val:.3f}s", end='\r')
            
            try:
                self.create_animation_frame(time_val, ax1, ax2)
                
                # Save frame as image
                frame_file = f'temp_frame_{i:04d}.png'
                plt.savefig(frame_file, dpi=100, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
                frames.append(frame_file)
                
            except Exception as e:
                print(f"\nError processing frame {i}: {e}")
                continue
        
        plt.close(fig)
        
        # Create GIF from frames
        if frames:
            print(f"\n🎞️  Creating GIF with {len(frames)} frames...")
            images = []
            for frame_file in frames:
                if os.path.exists(frame_file):
                    img = Image.open(frame_file)
                    images.append(img)
            
            if images:
                # Save as GIF
                duration = int(1000 / fps)  # milliseconds per frame
                images[0].save(output_file, save_all=True, append_images=images[1:],
                             duration=duration, loop=0, optimize=True)
                
                print(f"✅ Animation saved as: {output_file}")
                print(f"📊 Animation stats:")
                print(f"   - Frames: {len(images)}")
                print(f"   - Duration: {len(images)/fps:.1f} seconds")
                print(f"   - FPS: {fps}")
                
                # Clean up temporary files
                for frame_file in frames:
                    if os.path.exists(frame_file):
                        os.remove(frame_file)
            else:
                print("❌ No valid frames created!")
        else:
            print("❌ No frames to animate!")

def main():
    """Main execution function"""
    print("🌡️  Boiling Interface Animation Generator")
    print("=" * 50)
    
    # Create animation generator
    animator = BoilingAnimationGenerator()
    
    if len(animator.time_dirs) < 2:
        print("❌ Need at least 2 time steps for animation!")
        return
    
    # Generate the animation
    animator.generate_gif_animation(
        output_file='thermal_boiling_evolution.gif',
        fps=8,
        skip_frames=2  # Use every 2nd frame for smoother animation
    )
    
    print("\n🎉 Animation generation complete!")
    print("🔍 The GIF shows:")
    print("   - Left panel: Interface + Temperature field")
    print("   - Right panel: Water volume fraction (α)")
    print("   - Blue regions: Water (α ≈ 1)")
    print("   - Red regions: Vapor (α ≈ 0)")
    print("   - Interface: α ≈ 0.5 (black contour)")

if __name__ == "__main__":
    main()
