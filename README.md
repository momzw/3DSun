# 3DSun - 3D Solar Mesh Generator

A Python package for generating and visualizing 3D meshes of solar features, including the solar surface, magnetic loops, and other solar phenomena.

## Features

- Convert spherical coordinates (longitude, latitude, distance) to 3D Cartesian coordinates
- Generate triangular meshes using Delaunay triangulation
- Create parametric tubes for modeling solar loops, prominences, and other structures
- Apply various radius functions to model physical phenomena like magnetic flux expansion, kink instability, and turbulence
- Combine multiple meshes to create complex solar models
- Visualize the resulting 3D meshes with Plotly (interactive) or Matplotlib
- Export meshes to STL format for 3D printing or further processing

## Requirements

- Python 3.6+
- NumPy
- Plotly
- SciPy
- Matplotlib
- Astropy (for FITS file handling)

## Installation

1. Clone this repository:
```
git clone https://github.com/momzw/3DSun.git
cd 3DSun
```

2. Install the required dependencies:
```
pip install -e .
```

## Usage

### Basic Usage

Run the example script:

```
python examples/example_usage.py
```

This will generate sample 3D meshes and display them in your browser using Plotly.

### Creating a Simple Spherical Mesh

```python
import numpy as np
from src import spherical_mesh, visualize_mesh

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

# Generate mesh
vertices, triangles = spherical_mesh(points)

# Visualize
visualize_mesh(vertices, triangles, "Bumpy Sphere Example", renderer='browser')
```

### Creating Parametric Tubes (Solar Loops)

```python
from src import custom_curve_tube_mesh, loop_with_twist

# Create a loop with twist
vertices_loop, triangles_loop = custom_curve_tube_mesh(
    sun_position=(90, -45),  # Position on the sun (longitude, latitude)
    orientation=(0, 0),      # Orientation angles
    base_radius=0.15,        # Base tube thickness
    curve_func=loop_with_twist,
    curve_params={'height': 0.4, 'width': 4, 'twist': 2},
    radius_func=lambda t: 0.15  # Constant radius
)

# Visualize
visualize_mesh(vertices_loop, triangles_loop, "Solar Loop Example", renderer='browser')
```

### Creating Complex Solar Models

See `examples/sun_model.py` for a comprehensive example that:
- Loads real solar data from FITS files
- Creates a base solar surface mesh
- Adds multiple solar features (loops, prominences)
- Combines all meshes into a single model
- Exports the result to STL format

## Function Reference

### Core Functions

#### `spherical_to_cartesian(lon, lat, distance)`

Converts spherical coordinates to Cartesian coordinates.

- `lon`: Longitude in degrees (-180 to 180)
- `lat`: Latitude in degrees (-90 to 90)
- `distance`: Distance from center
- Returns: Tuple of (x, y, z) coordinates

#### `spherical_mesh(points)`

Generates a 3D mesh from an array of points in spherical coordinates.

- `points`: Array of points where each point is [longitude, latitude, distance]
- Returns: Tuple of (vertices, triangles) where vertices are the 3D points and triangles define the mesh faces

#### `visualize_mesh(vertices, triangles, title="3D Mesh", renderer="browser")`

Visualizes the 3D mesh using Plotly.

- `vertices`: Array of 3D points
- `triangles`: Array of triangle indices
- `title`: Plot title (optional)
- `renderer`: Plotly renderer to use (default: "browser")

#### `combine_meshes(base_vertices, base_triangles, additional_meshes)`

Combines multiple meshes into a single mesh.

- `base_vertices`: Vertices of the base mesh
- `base_triangles`: Triangles of the base mesh
- `additional_meshes`: List of (vertices, triangles) tuples to add to the base mesh
- Returns: Tuple of (vertices, triangles) for the combined mesh

### Parametric Tube Functions

#### `create_parametric_tube(curve_func, radius_func, **kwargs)`

Creates a tube mesh along a parametric curve with varying radius.

- `curve_func`: Function that generates points along a curve
- `radius_func`: Function that determines the tube radius at each point
- `**kwargs`: Additional parameters for the curve and radius functions
- Returns: Tuple of (vertices, triangles) for the tube mesh

#### `custom_curve_tube_mesh(sun_position, orientation, base_radius, curve_func, curve_params, radius_func)`

Creates a tube mesh positioned on the solar surface.

- `sun_position`: (longitude, latitude) position on the sun
- `orientation`: (tilt_angle, rotation_angle) for orienting the tube
- `base_radius`: Base radius of the tube
- `curve_func`: Function defining the curve shape (e.g., loop_with_twist, spiral_curve)
- `curve_params`: Parameters for the curve function
- `radius_func`: Function determining how the tube radius varies along its length
- Returns: Tuple of (vertices, triangles) for the tube mesh

### Export Functions

#### `export_mesh(vertices, triangles, filename, format="stl")`

Exports a mesh to a file.

- `vertices`: Array of 3D points
- `triangles`: Array of triangle indices
- `filename`: Output filename (without extension)
- `format`: Output format (currently only "stl" is supported)

### Radius Functions

The package includes several radius functions for modeling different physical phenomena:

- `magnetic_flux_radius(t, expansion_factor, corona_start)`: Models magnetic flux tube expansion
- `wavy_radius(t, wavelength, amplitude)`: Creates wave-like variations in tube radius
- `kink_instability_radius(t, kink_center, kink_width, kink_factor)`: Models kink instability
- `turbulent_radius(t, amplitude, seed)`: Adds random turbulent variations to tube radius
- `composite_radius(t, radius_funcs, combination_method, **kwargs)`: Combines multiple radius functions

## License

MIT
