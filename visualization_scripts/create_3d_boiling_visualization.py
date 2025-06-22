#!/usr/bin/env python3
"""
3D Boiling Interface Visualization with Temperature Coloring
Creates interactive 3D plots and rotating GIF animations showing the thermal boiling process
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import os
import glob
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

class Boiling3DVisualizer:
    def __init__(self, case_dir='.', nx=40, ny=40, nz=40):
        """Initialize 3D visualization for boiling simulation"""
        self.case_dir = case_dir
        self.nx, self.ny, self.nz = nx, ny, nz
        self.total_cells = nx * ny * nz
        
        # Physical domain (10cm x 10cm x 10cm)
        self.x_range = (-0.05, 0.05)  # -5cm to +5cm
        self.y_range = (-0.05, 0.05)  # -5cm to +5cm  
        self.z_range = (0.0, 0.1)     # 0 to 10cm height
        
        # Create coordinate arrays (in cm for visualization)
        self.x = np.linspace(self.x_range[0], self.x_range[1], nx) * 100
        self.y = np.linspace(self.y_range[0], self.y_range[1], ny) * 100
        self.z = np.linspace(self.z_range[0], self.z_range[1], nz) * 100
        
        # Create 3D coordinate meshes
        self.X, self.Y, self.Z = np.meshgrid(self.x, self.y, self.z, indexing='ij')
        
        # Find time directories
        self.time_dirs = self._find_time_directories()
        print(f"Found {len(self.time_dirs)} time steps for 3D visualization")
        
    def _find_time_directories(self):
        """Find valid time directories"""
        time_dirs = []
        for item in os.listdir(self.case_dir):
            try:
                time_val = float(item)
                time_path = os.path.join(self.case_dir, item)
                if (os.path.isdir(time_path) and 
                    os.path.exists(os.path.join(time_path, 'alpha.water')) and
                    os.path.exists(os.path.join(time_path, 'T'))):
                    time_dirs.append(time_val)
            except ValueError:
                continue
        return sorted(time_dirs)
    
    def _read_openfoam_field(self, filepath):
        """Read OpenFOAM field data"""
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            # Find data section
            data_values = []
            in_data = False
            
            for line in lines:
                line = line.strip()
                if 'internalField' in line and 'nonuniform' in line:
                    in_data = True
                    continue
                elif in_data:
                    if line == ')' or line == ');':
                        break
                    elif line and not line.startswith('('):
                        try:
                            if not line.isdigit():  # Skip count lines
                                value = float(line)
                                data_values.append(value)
                        except ValueError:
                            continue
            
            # Ensure correct size
            if len(data_values) != self.total_cells:
                if len(data_values) < self.total_cells:
                    data_values.extend([0.0] * (self.total_cells - len(data_values)))
                else:
                    data_values = data_values[:self.total_cells]
            
            # Reshape to 3D (k, j, i) ordering for OpenFOAM
            return np.array(data_values).reshape((self.nz, self.ny, self.nx))
            
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return np.zeros((self.nz, self.ny, self.nx))
    
    def _create_cube_wireframe(self, ax):
        """Create transparent cube wireframe"""
        # Define cube vertices (in cm)
        x_min, x_max = self.x[0], self.x[-1]
        y_min, y_max = self.y[0], self.y[-1]
        z_min, z_max = self.z[0], self.z[-1]
        
        # Cube edges
        edges = [
            # Bottom face
            [(x_min, y_min, z_min), (x_max, y_min, z_min)],
            [(x_max, y_min, z_min), (x_max, y_max, z_min)],
            [(x_max, y_max, z_min), (x_min, y_max, z_min)],
            [(x_min, y_max, z_min), (x_min, y_min, z_min)],
            # Top face
            [(x_min, y_min, z_max), (x_max, y_min, z_max)],
            [(x_max, y_min, z_max), (x_max, y_max, z_max)],
            [(x_max, y_max, z_max), (x_min, y_max, z_max)],
            [(x_min, y_max, z_max), (x_min, y_min, z_max)],
            # Vertical edges
            [(x_min, y_min, z_min), (x_min, y_min, z_max)],
            [(x_max, y_min, z_min), (x_max, y_min, z_max)],
            [(x_max, y_max, z_min), (x_max, y_max, z_max)],
            [(x_min, y_max, z_min), (x_min, y_max, z_max)],
        ]
        
        # Draw edges
        for edge in edges:
            xs, ys, zs = zip(*edge)
            ax.plot(xs, ys, zs, 'k-', alpha=0.3, linewidth=1)
    
    def create_3d_frame(self, time_val, view_angle=45):
        """Create a single 3D visualization frame"""
        time_dir = str(time_val)
        
        # Read fields
        alpha_file = os.path.join(self.case_dir, time_dir, 'alpha.water')
        temp_file = os.path.join(self.case_dir, time_dir, 'T')
        
        alpha_3d = self._read_openfoam_field(alpha_file)
        temp_3d = self._read_openfoam_field(temp_file)
        
        # Create figure
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create cube wireframe
        self._create_cube_wireframe(ax)
        
        # Extract interface isosurface (alpha = 0.5)
        interface_level = 0.5
        
        # Create temperature-colored interface visualization
        # Sample points for visualization (reduce for performance)
        step = 2  # Use every 2nd point
        x_sample = self.x[::step]
        y_sample = self.y[::step] 
        z_sample = self.z[::step]
        
        alpha_sample = alpha_3d[::step, ::step, ::step]
        temp_sample = temp_3d[::step, ::step, ::step]
        
        X_sample, Y_sample, Z_sample = np.meshgrid(x_sample, y_sample, z_sample, indexing='ij')
        
        # Find interface points (where alpha is close to 0.5)
        interface_mask = np.abs(alpha_sample - interface_level) < 0.2
        
        if np.any(interface_mask):
            # Extract interface points
            x_interface = X_sample[interface_mask]
            y_interface = Y_sample[interface_mask]
            z_interface = Z_sample[interface_mask]
            temp_interface = temp_sample[interface_mask]
            
            # Create temperature colormap
            scatter = ax.scatter(x_interface, y_interface, z_interface, 
                               c=temp_interface, cmap='hot', s=20, alpha=0.8)
            
            # Add colorbar
            cbar = plt.colorbar(scatter, ax=ax, shrink=0.8, aspect=20)
            cbar.set_label('Temperature (K)', fontsize=12)
        
        # Add water volume visualization (alpha > 0.7)
        water_mask = alpha_sample > 0.7
        if np.any(water_mask):
            x_water = X_sample[water_mask]
            y_water = Y_sample[water_mask]
            z_water = Z_sample[water_mask]
            temp_water = temp_sample[water_mask]
            
            # Water points in blue with temperature variation
            ax.scatter(x_water, y_water, z_water, 
                      c=temp_water, cmap='Blues', s=8, alpha=0.4)
        
        # Add vapor visualization (alpha < 0.3)
        vapor_mask = alpha_sample < 0.3
        if np.any(vapor_mask):
            x_vapor = X_sample[vapor_mask]
            y_vapor = Y_sample[vapor_mask]
            z_vapor = Z_sample[vapor_mask]
            temp_vapor = temp_sample[vapor_mask]
            
            # Vapor points in red with temperature variation
            ax.scatter(x_vapor, y_vapor, z_vapor, 
                      c=temp_vapor, cmap='Reds', s=5, alpha=0.3)
        
        # Set labels and title
        ax.set_xlabel('X Position (cm)', fontsize=12)
        ax.set_ylabel('Y Position (cm)', fontsize=12)
        ax.set_zlabel('Z Position (cm)', fontsize=12)
        ax.set_title(f'3D Boiling Interface - Temperature Colored\nTime: {time_val:.3f}s', 
                    fontsize=14, fontweight='bold')
        
        # Set view angle
        ax.view_init(elev=20, azim=view_angle)
        
        # Set equal aspect ratio
        ax.set_box_aspect([1,1,2])  # Make Z axis twice as tall
        
        return fig
    
    def create_static_3d_plot(self, time_val=None):
        """Create a single static 3D plot"""
        if time_val is None:
            time_val = self.time_dirs[len(self.time_dirs)//2]  # Middle time
        
        print(f"Creating 3D visualization for t={time_val:.3f}s...")
        fig = self.create_3d_frame(time_val)
        
        output_file = f'3d_boiling_t{time_val:.3f}s.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"✅ 3D plot saved: {output_file}")
        plt.show()
        
        return fig
    
    def create_rotating_gif(self, time_val=None, output_file='3d_boiling_rotation.gif'):
        """Create a rotating 3D GIF animation"""
        if time_val is None:
            time_val = self.time_dirs[len(self.time_dirs)//2]  # Middle time
        
        print(f"Creating rotating 3D GIF for t={time_val:.3f}s...")
        
        # Create frames at different viewing angles
        angles = np.linspace(0, 360, 36)  # 36 frames for full rotation
        frame_files = []
        
        for i, angle in enumerate(angles):
            print(f"Rendering frame {i+1}/{len(angles)}: angle={angle:.0f}°", end='\r')
            
            fig = self.create_3d_frame(time_val, view_angle=angle)
            frame_file = f'3d_frame_{i:03d}.png'
            plt.savefig(frame_file, dpi=100, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            frame_files.append(frame_file)
            plt.close(fig)
        
        print(f"\n🎞️  Creating rotating GIF...")
        
        # Create GIF
        images = []
        for frame_file in frame_files:
            if os.path.exists(frame_file):
                img = Image.open(frame_file)
                images.append(img)
        
        if images:
            images[0].save(output_file, save_all=True, append_images=images[1:],
                         duration=100, loop=0, optimize=True)
            
            print(f"✅ Rotating 3D GIF saved: {output_file}")
            
            # Clean up
            for frame_file in frame_files:
                if os.path.exists(frame_file):
                    os.remove(frame_file)
        
        return output_file

    def create_time_evolution_3d_gif(self, output_file='3d_boiling_evolution.gif', skip_frames=3):
        """Create 3D GIF showing time evolution of boiling"""
        print(f"Creating 3D time evolution GIF...")

        # Select time steps
        selected_times = self.time_dirs[::skip_frames]
        print(f"Animating {len(selected_times)} time steps...")

        frame_files = []
        for i, time_val in enumerate(selected_times):
            print(f"Time frame {i+1}/{len(selected_times)}: t={time_val:.3f}s", end='\r')

            # Use a fixed viewing angle for time evolution
            fig = self.create_3d_frame(time_val, view_angle=45)
            frame_file = f'3d_time_frame_{i:03d}.png'
            plt.savefig(frame_file, dpi=100, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            frame_files.append(frame_file)
            plt.close(fig)

        print(f"\n🎞️  Creating time evolution GIF...")

        # Create GIF
        images = []
        for frame_file in frame_files:
            if os.path.exists(frame_file):
                img = Image.open(frame_file)
                images.append(img)

        if images:
            images[0].save(output_file, save_all=True, append_images=images[1:],
                         duration=200, loop=0, optimize=True)

            print(f"✅ 3D Time Evolution GIF saved: {output_file}")

            # Clean up
            for frame_file in frame_files:
                if os.path.exists(frame_file):
                    os.remove(frame_file)

        return output_file

def main():
    """Main execution function"""
    print("🌡️  3D Boiling Interface Visualizer")
    print("=" * 50)
    
    # Create visualizer
    viz = Boiling3DVisualizer()
    
    if len(viz.time_dirs) == 0:
        print("❌ No valid time directories found!")
        return
    
    # Create static 3D plot for middle time
    middle_time = viz.time_dirs[len(viz.time_dirs)//2]
    viz.create_static_3d_plot(middle_time)
    
    # Create rotating GIF
    viz.create_rotating_gif(middle_time, '3d_boiling_rotation.gif')

    # Create time evolution GIF
    viz.create_time_evolution_3d_gif('3d_boiling_time_evolution.gif', skip_frames=3)

    print("\n🎉 3D Visualization complete!")
    print("📊 Generated files:")
    print("   - Static 3D plot: 3d_boiling_t*.png")
    print("   - Rotating GIF: 3d_boiling_rotation.gif")
    print("   - Time Evolution GIF: 3d_boiling_time_evolution.gif")
    print("\n🔍 Visualization features:")
    print("   - 🔴 Red points: Hot vapor (α < 0.3)")
    print("   - 🔵 Blue points: Water (α > 0.7)")
    print("   - 🌈 Interface: Temperature-colored (α ≈ 0.5)")
    print("   - ⬛ Black wireframe: Domain boundaries")

if __name__ == "__main__":
    main()
