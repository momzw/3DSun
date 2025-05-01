from astropy.io import fits
import plotly.colors as pc
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from src.generate_3d_mesh import spherical_mesh, visualize_mesh, combine_meshes
from src.export_mesh import export_mesh             # Associated code might be commented out
from src.parametric_tube import spiral_curve, loop_with_twist, custom_curve_tube_mesh
from src.radius_functions import *


FILENAME = '../data/sunerf_map.fits'
CMAP = plt.get_cmap('sdoaia304')
colorscale = pc.make_colorscale([matplotlib.colors.rgb2hex(CMAP(i)) for i in np.linspace(0, 1, 10)])


if __name__ == '__main__':
    with fits.open(FILENAME) as hdul:
        hdul.info()
        data = np.flip(hdul[0].data, axis=0)

    longitudes = np.linspace(-180, 180, data.shape[1], endpoint=False)
    latitudes = np.linspace(-90, 90, data.shape[0], endpoint=False)

    # Create a meshgrid for all combinations
    lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)

    # Flatten the grid
    lons = lon_grid.flatten()
    lats = lat_grid.flatten()

    # Create distances based on (normalized) data
    base_radius = 10
    data_normalized = (data - np.min(data)) / (np.max(data) - np.min(data))
    distances = base_radius + data_normalized

    # Combine into points array
    points = np.column_stack((lons, lats, distances.flatten()))

    # Generate mesh
    vertices_sphere, triangles_sphere = spherical_mesh(points)
    print(f"Spherical mesh created with {len(vertices_sphere)} vertices and {len(triangles_sphere)} triangles")

    vertices_composite, triangles_composite = custom_curve_tube_mesh(
        sun_position=(10, -60),
        orientation=(0, 0),  # Position
        base_radius=0.3,  # Base thickness
        curve_func=loop_with_twist,  # Curve shape
        curve_params={'height': 2.2, 'width': 8, 'twist': 1.1},
        radius_func=lambda t: composite_radius(
            t,
            radius_funcs=[magnetic_flux_radius, wavy_radius, turbulent_radius],
            combination_method='add',
            # Parameters for each function
            magnetic_flux_radius={'expansion_factor': 2.5, 'corona_start': .5},
            wavy_radius={'wavelength': 10, 'amplitude': 0.2},
            kink_instability_radius={'kink_center': 0.7, 'kink_factor': 2},
            turbulent_radius={'amplitude': 0.3, 'seed': 123}
        )
    )
    print(f"Composite mesh created with {len(vertices_composite)} vertices and {len(triangles_composite)} triangles")

    vertices_loop, triangles_loop = custom_curve_tube_mesh(
        sun_position=(90, -45),
        orientation=(0, 0),  # Tuple (tilt_angle, rotation_angle, roll_angle)
        base_radius=0.15,  # Thicker tube
        curve_func=loop_with_twist,
        curve_params={'height': .4, 'width': 4, 'twist': 2},
        radius_func=lambda t: kink_instability_radius(t, kink_center=.5, kink_width=.1, kink_factor=2.0)
    )
    print(f"Loop mesh created with {len(vertices_loop)} vertices and {len(triangles_loop)} triangles")

    vertices_loop2, triangles_loop2 = custom_curve_tube_mesh(
        sun_position=(120, 45),
        orientation=(0, 0),  # Tuple (tilt_angle, rotation_angle, roll_angle)
        base_radius=0.15,  # Thicker tube
        curve_func=loop_with_twist,
        curve_params={'height': 1, 'width': 6, 'twist': 1.1},
        radius_func=lambda t: kink_instability_radius(t, kink_center=.5, kink_width=.1, kink_factor=1.0)
    )
    print(f"Loop mesh created with {len(vertices_loop2)} vertices and {len(triangles_loop2)} triangles")

    vertices_magflux, triangles_magflux = custom_curve_tube_mesh(
        sun_position=(240, -70),
        orientation=(90, 0),  # Tuple (tilt_angle, rotation_angle, roll_angle)
        base_radius=0.05,  # Thicker tube
        curve_func=spiral_curve,
        curve_params={'height': 4.0, 'radius': .2, 'turns': 2, 'taper': 1.1},
        radius_func=lambda t: magnetic_flux_radius(t, expansion_factor=4.0, corona_start=0.2)
    )
    print(f"Magnetic flux mesh created with {len(vertices_magflux)} vertices and {len(triangles_magflux)} triangles")

    vertices_magflux2, triangles_magflux2 = custom_curve_tube_mesh(
        sun_position=(250, -70),
        orientation=(90, 0),  # Tuple (tilt_angle, rotation_angle, roll_angle)
        base_radius=0.05,  # Thicker tube
        curve_func=spiral_curve,
        curve_params={'height': 4.0, 'radius': .2, 'turns': 2, 'taper': 1.1},
        radius_func=lambda t: magnetic_flux_radius(t, expansion_factor=4.0, corona_start=0.2)
    )
    print(f"Magnetic flux mesh created with {len(vertices_magflux)} vertices and {len(triangles_magflux)} triangles")

    vertices_magflux3, triangles_magflux3 = custom_curve_tube_mesh(
        sun_position=(235, -75),
        orientation=(90, 0),  # Tuple (tilt_angle, rotation_angle, roll_angle)
        base_radius=0.05,  # Thicker tube
        curve_func=spiral_curve,
        curve_params={'height': 4.0, 'radius': .2, 'turns': 2, 'taper': 1.1},
        radius_func=lambda t: magnetic_flux_radius(t, expansion_factor=4.0, corona_start=0.2)
    )
    print(f"Magnetic flux mesh created with {len(vertices_magflux)} vertices and {len(triangles_magflux)} triangles")

    vertices_total, triangles_total = combine_meshes(
        vertices_sphere, triangles_sphere,
        [
            (vertices_loop, triangles_loop),
            (vertices_loop2, triangles_loop2),
            (vertices_composite, triangles_composite),
            (vertices_magflux, triangles_magflux),
            (vertices_magflux2, triangles_magflux2),
            (vertices_magflux3, triangles_magflux3)
        ],
    )
    print(f"Total mesh created with {len(vertices_total)} vertices and {len(triangles_total)} triangles")

    export_mesh(vertices_total, triangles_total, "output/sun_3d", "stl")