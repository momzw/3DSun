#!/usr/bin/env python3
"""
Example usage of the 3D mesh generator with custom data.
"""

import numpy as np
from src.generate_3d_mesh import spherical_mesh, visualize_mesh


def main():
    """
    Demonstrates how to use the 3D mesh generator with custom data.
    """
    # Example 1: Create a simple sphere with varying distances
    print("Example 1: Simple sphere with varying distances")
    
    # Create a grid of longitude and latitude points
    lon_steps, lat_steps = 15, 10
    longitudes = np.linspace(-180, 180, lon_steps)
    latitudes = np.linspace(-90, 90, lat_steps)
    
    # Create a meshgrid for all combinations
    lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)
    
    # Flatten the grids
    lons = lon_grid.flatten()
    lats = lat_grid.flatten()
    
    # Create distances with a simple pattern (a bumpy sphere)
    base_radius = 10
    distances = base_radius + np.sin(np.radians(lons)) * np.cos(np.radians(lats)) * 2
    
    # Combine into points array
    points = np.column_stack((lons, lats, distances))
    
    print(f"Generated {len(points)} points")
    
    # Generate mesh
    vertices, triangles = spherical_mesh(points)
    
    print(f"Mesh created with {len(vertices)} vertices and {len(triangles)} triangles")
    
    # Visualize
    visualize_mesh(vertices, triangles, "Bumpy Sphere Example", renderer='browser')

    # ==================================
    # Example 2: Manual point definition
    print("\nExample 2: Manually defined points")
    
    # Define specific points
    manual_points = [
        [0, 0, 10],       # Point at equator, prime meridian
        [90, 0, 12],      # Point at equator, 90° east
        [180, 0, 11],     # Point at equator, 180°
        [270, 0, 9],      # Point at equator, 90° west
        [0, 90, 10.5],    # North pole
        [0, -90, 9.5],    # South pole
        [45, 45, 11],     # Northeast quadrant
        [135, 45, 10.8],  # Southeast quadrant
        [225, 45, 9.7],   # Southwest quadrant
        [315, 45, 10.2],  # Northwest quadrant
        [45, -45, 10.3],  # Northeast quadrant, southern hemisphere
        [135, -45, 9.9],  # Southeast quadrant, southern hemisphere
        [225, -45, 10.7], # Southwest quadrant, southern hemisphere
        [315, -45, 11.1]  # Northwest quadrant, southern hemisphere
    ]
    
    # Generate mesh from manual points
    vertices, triangles = spherical_mesh(manual_points)
    
    print(f"Mesh created with {len(vertices)} vertices and {len(triangles)} triangles")
    
    # Visualize
    visualize_mesh(vertices, triangles, "Manual Points Example", renderer='browser')

if __name__ == "__main__":
    main()