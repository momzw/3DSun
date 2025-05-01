"""
3D Mesh Generator from Longitude, Latitude, and Distance Points

This script takes an array of points consisting of longitude, latitude, and distance from center,
and generates a 3D mesh representation.

Dependencies:
- numpy
- plotly
"""

import numpy as np
import plotly.graph_objects as go
from scipy.spatial import Delaunay


def spherical_to_cartesian(lon, lat, distance):
    """
    Convert spherical coordinates (longitude, latitude, distance) to Cartesian coordinates (x, y, z).

    Args:
        lon (float or array): Longitude in degrees
        lat (float or array): Latitude in degrees
        distance (float or array): Distance from center

    Returns:
        tuple: (x, y, z) coordinates
    """
    # Convert degrees to radians
    lon_rad = np.radians(lon)
    lat_rad = np.radians(lat)

    # Convert to Cartesian coordinates
    x = distance * np.cos(lat_rad) * np.cos(lon_rad)
    y = distance * np.cos(lat_rad) * np.sin(lon_rad)
    z = distance * np.sin(lat_rad)

    return x, y, z


def spherical_mesh(points):
    """
    Generate a 3D mesh from an array of points.

    Args:
        points (array-like): Array of points where each point is [longitude, latitude, distance]

    Returns:
        tuple: (vertices, triangles) where vertices are the 3D points and triangles define the mesh faces
    """
    # Convert points to numpy array if not already
    points_array = np.array(points)

    # Extract components
    longitudes = points_array[:, 0]
    latitudes = points_array[:, 1]
    distances = points_array[:, 2]

    # Convert to Cartesian coordinates
    x, y, z = spherical_to_cartesian(longitudes, latitudes, distances)

    # Combine into vertices array
    vertices = np.column_stack((x, y, z))

    # Create triangulation (mesh) using Delaunay
    tri = Delaunay(np.column_stack((longitudes, latitudes)))

    return vertices, tri.simplices


def toroidal_mesh(
        lon0_deg, lat0_deg,
        R_sun=10.0,  # Solar surface "radius"
        loop_major=2.0,  # Major radius (distance from center to tube center)
        loop_minor=0.3,  # Minor radius (tube thickness)
        n_major=40,  # Resolution around major circle
        n_minor=15  # Resolution around minor circle
):
    """
    Create a torus mesh with proper face indices.

    Args:
        lon0_deg, lat0_deg: Position on sun surface (degrees)
        R_sun: Radius of sun
        loop_major: Major radius of torus
        loop_minor: Minor radius of torus
        n_major: Resolution around major circle
        n_minor: Resolution around minor circle

    Returns:
        tuple: (vertices, triangles) where vertices are 3D points and triangles define the mesh faces
    """
    # Parameter arrays (angles)
    u = np.linspace(0, 2 * np.pi, n_major, endpoint=False)  # Major circle
    v = np.linspace(0, 2 * np.pi, n_minor, endpoint=False)  # Minor circle

    # Create vertices
    vertices = []

    # Create 2D grid of vertices
    for i, u_val in enumerate(u):
        for j, v_val in enumerate(v):
            # Torus parametric equation
            x_local = (loop_major + loop_minor * np.cos(v_val)) * np.cos(u_val)
            y_local = (loop_major + loop_minor * np.cos(v_val)) * np.sin(u_val)
            z_local = loop_minor * np.sin(v_val)

            # Shift to position at height R_sun
            z_local += R_sun

            # Add to vertices list
            vertices.append([x_local, y_local, z_local])

    vertices = np.array(vertices)

    # Apply rotation to position on sun
    lon0 = np.radians(lon0_deg)
    lat0 = np.radians(lat0_deg)

    # Rotation for latitude (about y)
    Ry = np.array([
        [np.cos(lat0), 0, np.sin(lat0)],
        [0, 1, 0],
        [-np.sin(lat0), 0, np.cos(lat0)]
    ])
    # Rotation for longitude (about z)
    Rz = np.array([
        [np.cos(lon0), -np.sin(lon0), 0],
        [np.sin(lon0), np.cos(lon0), 0],
        [0, 0, 1]
    ])

    # Total rotation
    R = Rz @ Ry
    vertices = vertices @ R.T

    # Create triangles (faces)
    triangles = []

    # Loop through the grid
    for i in range(n_major):
        for j in range(n_minor):
            # Calculate indices for the 4 corners of a grid cell
            # with appropriate wrapping for the torus topology
            i_next = (i + 1) % n_major  # Wrap around major circle
            j_next = (j + 1) % n_minor  # Wrap around minor circle

            # Indices of the 4 corners
            v00 = i * n_minor + j  # Current vertex
            v01 = i * n_minor + j_next  # Next in minor direction
            v10 = i_next * n_minor + j  # Next in major direction
            v11 = i_next * n_minor + j_next  # Diagonal

            # Add two triangles to create a quad face
            triangles.append([v00, v01, v11])
            triangles.append([v00, v11, v10])

    triangles = np.array(triangles)

    return vertices, triangles


def stretched_toroidal_mesh(
        lon0_deg, lat0_deg,
        R_sun=10.0,  # Solar surface "radius"
        loop_major=2.0,  # Base major radius
        loop_minor=0.3,  # Minor radius (tube thickness)
        n_major=40,  # Resolution around major circle
        n_minor=15,  # Resolution around minor circle
        stretch_factor=1.5,  # How much to stretch in one direction
        stretch_axis='x',  # Which axis to stretch along ('x', 'y', or 'z')
        asymmetry=0.0  # Asymmetry factor (0.0 = symmetric, >0 = asymmetric)
):
    """
    Create a stretched torus mesh with proper face indices.

    Args:
        lon0_deg, lat0_deg: Position on sun surface (degrees)
        R_sun: Radius of sun
        loop_major: Base major radius of torus
        loop_minor: Minor radius of torus (tube thickness)
        n_major: Resolution around major circle
        n_minor: Resolution around minor circle
        stretch_factor: How much to stretch along the specified axis
        stretch_axis: Which axis to stretch ('x', 'y', or 'z')
        asymmetry: Makes the stretching asymmetric when > 0

    Returns:
        tuple: (vertices, triangles) where vertices are 3D points and triangles define the mesh faces
    """
    # Parameter arrays (angles)
    u = np.linspace(0, 2 * np.pi, n_major, endpoint=False)  # Major circle
    v = np.linspace(0, 2 * np.pi, n_minor, endpoint=False)  # Minor circle

    # Create vertices
    vertices = []

    # Create 2D grid of vertices
    for i, u_val in enumerate(u):
        for j, v_val in enumerate(v):
            # Standard torus parameterization
            x_local = (loop_major + loop_minor * np.cos(v_val)) * np.cos(u_val)
            y_local = (loop_major + loop_minor * np.cos(v_val)) * np.sin(u_val)
            z_local = loop_minor * np.sin(v_val)

            # Apply stretching based on the parameter u
            # Calculate the stretch modifier (varies from 1.0 to stretch_factor)
            stretch = 1.0
            if stretch_axis == 'x':
                # Stretching along x-axis
                # The cos function gives maximum stretch at u=0,2π and minimum at u=π
                stretch_modifier = 1.0 + (stretch_factor - 1.0) * (
                            0.5 + 0.5 * np.cos(u_val + asymmetry * np.sin(u_val)))
                x_local *= stretch_modifier
            elif stretch_axis == 'y':
                # Stretching along y-axis
                stretch_modifier = 1.0 + (stretch_factor - 1.0) * (
                            0.5 + 0.5 * np.cos(u_val - np.pi / 2 + asymmetry * np.sin(u_val)))
                y_local *= stretch_modifier
            elif stretch_axis == 'z':
                # Stretching the height
                z_factor = 1.0 + (stretch_factor - 1.0) * (0.5 + 0.5 * np.cos(u_val + asymmetry * np.sin(u_val)))
                z_local *= z_factor

            # Adjust height on sun's surface
            z_local += R_sun

            # Add to vertices list
            vertices.append([x_local, y_local, z_local])

    vertices = np.array(vertices)

    # Apply rotation to position on sun
    lon0 = np.radians(lon0_deg)
    lat0 = np.radians(lat0_deg)

    # Rotation for latitude (about y)
    Ry = np.array([
        [np.cos(lat0), 0, np.sin(lat0)],
        [0, 1, 0],
        [-np.sin(lat0), 0, np.cos(lat0)]
    ])
    # Rotation for longitude (about z)
    Rz = np.array([
        [np.cos(lon0), -np.sin(lon0), 0],
        [np.sin(lon0), np.cos(lon0), 0],
        [0, 0, 1]
    ])

    # Total rotation
    R = Rz @ Ry
    vertices = vertices @ R.T

    # Create triangles (faces)
    triangles = []

    # Loop through the grid
    for i in range(n_major):
        for j in range(n_minor):
            # Calculate indices for the 4 corners of a grid cell
            # with appropriate wrapping for the torus topology
            i_next = (i + 1) % n_major  # Wrap around major circle
            j_next = (j + 1) % n_minor  # Wrap around minor circle

            # Indices of the 4 corners
            v00 = i * n_minor + j  # Current vertex
            v01 = i * n_minor + j_next  # Next in minor direction
            v10 = i_next * n_minor + j  # Next in major direction
            v11 = i_next * n_minor + j_next  # Diagonal

            # Add two triangles to create a quad face
            triangles.append([v00, v01, v11])
            triangles.append([v00, v11, v10])

    triangles = np.array(triangles)

    return vertices, triangles


def combine_meshes(sphere_vertices, sphere_triangles, tube_meshes):
    """
    Combine a spherical mesh with multiple tube structures (like solar prominences).

    Args:
        sphere_vertices: Vertices of the spherical mesh
        sphere_triangles: Triangle indices of the spherical mesh
        tube_meshes: List of tuples, each containing (vertices, triangles) for a tube
        show_anchors: Whether to show anchor points for debugging

    Returns:
        tuple: (combined_vertices, combined_triangles)
    """

    # Start with the sphere vertices and triangles
    combined_vertices = sphere_vertices.copy()
    combined_triangles = sphere_triangles.copy()

    # For each tube mesh
    for i, (tube_vertices, tube_triangles) in enumerate(tube_meshes):
        # Get the current vertex count to offset triangle indices
        vertex_offset = len(combined_vertices)

        # Add the tube vertices to the combined vertices
        combined_vertices = np.vstack([combined_vertices, tube_vertices])

        # Add the tube triangles with adjusted indices
        adjusted_triangles = tube_triangles + vertex_offset
        combined_triangles = np.vstack([combined_triangles, adjusted_triangles])

    return combined_vertices, combined_triangles


def visualize_mesh(vertices, triangles, title="3D Mesh", renderer='notebook_connected',
                   edges=True, scatters=True,
                   return_fig=False):
    """
    Visualize the 3D mesh.

    Args:
        vertices (array-like): Array of 3D points
        triangles (array-like): Array of triangle indices
        title (str, optional): Plot title
        renderer (str, optional): Plot renderer
        return_fig (bool, optional): Whether to return the figure object
    """
    data = []
    # Create a mesh3d trace for the triangular mesh
    mesh = go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=triangles[:, 0],
        j=triangles[:, 1],
        k=triangles[:, 2],
        opacity=1.0,
        colorscale='Viridis'
    )
    data.append(mesh)

    if scatters:
        # Create a scatter3d trace for the vertices
        scatter = go.Scatter3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            mode='markers',
            marker=dict(
                size=5,
                color='red',
                opacity=0.5
            )
        )
        data.append(scatter)

    if edges:
        # Create edges for the mesh
        # Initialize lists to collect edge coordinates
        x_edges, y_edges, z_edges = [], [], []

        # For each triangle, add ittributeError: Can't get attribute 'CoxNetEstimator' on <module '__main__'ts edges to the list
        for triangle in triangles:
            # Get vertex indices for this triangle
            i, j, k = triangle

            # Add coordinates for first edge (i to j)
            x_edges.extend([vertices[i, 0], vertices[j, 0], None])
            y_edges.extend([vertices[i, 1], vertices[j, 1], None])
            z_edges.extend([vertices[i, 2], vertices[j, 2], None])

            # Add coordinates for second edge (j to k)
            x_edges.extend([vertices[j, 0], vertices[k, 0], None])
            y_edges.extend([vertices[j, 1], vertices[k, 1], None])
            z_edges.extend([vertices[j, 2], vertices[k, 2], None])

            # Add coordinates for third edge (k to i)
            x_edges.extend([vertices[k, 0], vertices[i, 0], None])
            y_edges.extend([vertices[k, 1], vertices[i, 1], None])
            z_edges.extend([vertices[k, 2], vertices[i, 2], None])

        # Create a scatter3d trace for the edges
        edges = go.Scatter3d(
            x=x_edges,
            y=y_edges,
            z=z_edges,
            mode='lines',
            line=dict(
                color='white',
                width=2
            )
        )
        data.append(edges)

    # Create the figure and add the traces
    fig = go.Figure(data=data)

    # Update the layout
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z'
        ),
        width=800,
        height=800
    )

    if return_fig:
        # Return figure object
        return fig
    else:
        # Show the figure
        fig.show(renderer=renderer)
        return None


def main():
    """Example usage of the mesh generation functionality."""
    # Example data: [longitude, latitude, distance]
    # Generate some sample points (a distorted sphere)
    n_points = 100
    longitudes = np.random.uniform(-180, 180, n_points)
    latitudes = np.random.uniform(-90, 90, n_points)

    # Base distance with some variation
    base_distance = 10
    variation = 2
    distances = base_distance + np.random.uniform(-variation, variation, n_points)

    # Combine into points array
    points = np.column_stack((longitudes, latitudes, distances))

    print(f"Generated {n_points} random points")

    # Generate mesh
    vertices, triangles = spherical_mesh(points)

    print(f"Mesh created with {len(vertices)} vertices and {len(triangles)} triangles")

    # Visualize
    visualize_mesh(vertices, triangles, "Sample 3D Mesh", renderer='browser', edges=True, scatters=True)

if __name__ == "__main__":
    main()
