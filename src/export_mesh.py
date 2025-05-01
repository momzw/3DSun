# Function to export the mesh to various 3D formats
def export_mesh(vertices, triangles, filename, export_format='obj'):
    """
    Export a mesh to a 3D file format that Blender can import.

    Args:
        vertices (numpy.ndarray): Vertex coordinates array (n_vertices, 3)
        triangles (numpy.ndarray): Triangle indices array (n_triangles, 3)
        filename (str): Output filename (without extension)
        export_format (str): Export format - 'obj', 'stl', or 'ply'

    Returns:
        str: Path to the exported file
    """
    # Make sure the filename has the correct extension
    if not filename.endswith('.' + export_format.lower()):
        filename = filename + '.' + export_format.lower()

    if export_format.lower() == 'obj':
        # Export as OBJ
        with open(filename, 'w') as f:
            # Write vertices
            for v in vertices:
                f.write(f"v {v[0]} {v[1]} {v[2]}\n")

            # Write faces (OBJ uses 1-based indexing)
            for face in triangles:
                f.write(f"f {face[0] + 1} {face[1] + 1} {face[2] + 1}\n")

    elif export_format.lower() == 'stl':
        # For STL we'll use numpy-stl
        try:
            from stl import mesh as stl_mesh
            import numpy as np

            # Create the mesh
            your_mesh = stl_mesh.Mesh(np.zeros(len(triangles), dtype=stl_mesh.Mesh.dtype))

            # Set the vertices of each triangle
            for i, face in enumerate(triangles):
                for j in range(3):
                    your_mesh.vectors[i][j] = vertices[face[j]]

            # Write the mesh to file
            your_mesh.save(filename)

        except ImportError:
            print("To export STL files, install numpy-stl: pip install numpy-stl")
            return None

    elif export_format.lower() == 'ply':
        # For PLY we'll use trimesh
        try:
            import trimesh

            # Create a trimesh mesh
            mesh = trimesh.Trimesh(vertices=vertices, faces=triangles)

            # Export to PLY
            mesh.export(filename)

        except ImportError:
            print("To export PLY files, install trimesh: pip install trimesh")
            return None

    else:
        raise ValueError(f"Unsupported export format: {export_format}")

    print(f"Mesh exported to {filename}")
    return filename


# Example usage to export your spherical harmonics mesh:
# export_mesh(vertices_example, triangles_example, "spherical_harmonics_mesh", "obj")