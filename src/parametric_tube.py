import numpy as np

def custom_curve_tube_mesh(
        sun_position=(0, 0),  # (longitude, latitude) in degrees
        orientation=(0, 0),  # (tilt_angle, rotation_angle) in degrees
        R_sun=10.0,  # Solar surface "radius"
        base_radius=0.3,  # Base thickness of the tube
        n_curve=40,  # Resolution along curve
        n_circle=15,  # Resolution around tube circumference
        curve_func=None,  # Custom function for curve shape
        curve_params=None,  # Parameters for the custom curve
        radius_func=None  # Function that takes parameter t (0 to 1) and returns radius multiplier
):
    """
    Create a tube mesh around a custom 3D parametric curve.

    Args:
        sun_position:  Tuple (longitude, latitude) in degrees specifying position on sun surface
        orientation:   Tuple (tilt_angle, rotation_angle) in degrees specifying orientation
                       - tilt_angle: tilt from the surface normal (0 = perpendicular to surface)
                       - rotation_angle: rotation around the surface normal

        R_sun:         Radius of sun
        base_radius:   Base radius of the tube
        n_curve:       Resolution along curve
        n_circle:      Resolution around tube circumference
        curve_func:    Function that takes parameter t (0 to 1) and returns (x,y,z)
                       If None, defaults to a simple arch curve
        curve_params:  Dictionary of parameters to pass to curve_func
        radius_func:   Function that takes parameter t (0 to 1) and returns radius multiplier

    Returns:
        tuple: (vertices, triangles) where vertices are 3D points and triangles define the mesh faces
    """
    # Extract position and orientation parameters
    lon0_deg, lat0_deg = sun_position
    tilt_angle, rotation_angle = orientation

    # Convert all angles to radians
    lon0 = np.radians(lon0_deg)
    lat0 = np.radians(lat0_deg)
    tilt = np.radians(tilt_angle - 90)
    rotation = np.radians(rotation_angle)

    # Parameter arrays
    t = np.linspace(0, 1, n_curve)  # Curve parameter
    theta = np.linspace(0, 2 * np.pi, n_circle, endpoint=False)  # Circle parameter

    # Default curve function (simple arch shape)
    if curve_func is None:
        def default_curve(t, height=2.0, width=4.0, asymmetry=0.0):
            """Default curve: a simple asymmetric arch"""
            x = width * (t - 0.5) * (1 + asymmetry * (t - 0.5))
            y = 0
            z = height * np.sin(np.pi * t)
            return x, y, z

        curve_func = default_curve

    if curve_params is None:
        curve_params = {'height': 2.0, 'width': 3.0, 'asymmetry': 0.0}

    # Create vertices
    vertices = []

    # Create local coordinate frames along the curve
    curve_points = []
    tangents = []
    normals = []
    binormals = []

    # Generate the curve points and calculate the Frenet frame
    for i, t_val in enumerate(t):
        # Get point on curve
        x, y, z = curve_func(t_val, **curve_params)
        curve_points.append((x, y, z))

        # Calculate tangent vector (using finite differences or analytical derivative)
        if i == 0:  # Forward difference at start
            t_next = t[i + 1]
            x_next, y_next, z_next = curve_func(t_next, **curve_params)
            tx = x_next - x
            ty = y_next - y
            tz = z_next - z
        elif i == len(t) - 1:  # Backward difference at end
            t_prev = t[i - 1]
            x_prev, y_prev, z_prev = curve_func(t_prev, **curve_params)
            tx = x - x_prev
            ty = y - y_prev
            tz = z - z_prev
        else:  # Central difference elsewhere
            t_next = t[i + 1]
            t_prev = t[i - 1]
            x_next, y_next, z_next = curve_func(t_next, **curve_params)
            x_prev, y_prev, z_prev = curve_func(t_prev, **curve_params)
            tx = 0.5 * (x_next - x_prev)
            ty = 0.5 * (y_next - y_prev)
            tz = 0.5 * (z_next - z_prev)

        # Normalize tangent
        t_norm = np.sqrt(tx ** 2 + ty ** 2 + tz ** 2)
        if t_norm < 1e-10:  # Avoid division by zero
            tx, ty, tz = 1, 0, 0
        else:
            tx, ty, tz = tx / t_norm, ty / t_norm, tz / t_norm

        tangents.append((tx, ty, tz))

        # Calculate normal vector (requires care to avoid parallel vectors)
        # Start with a vector not parallel to tangent
        if abs(tz) < 0.9:  # If tangent is not too close to z-axis
            nx, ny, nz = 0, 0, 1
        else:  # If tangent is close to z-axis, use x-axis
            nx, ny, nz = 1, 0, 0

        # Make it perpendicular to tangent using Gram-Schmidt
        dot = nx * tx + ny * ty + nz * tz
        nx -= dot * tx
        ny -= dot * ty
        nz -= dot * tz

        # Normalize normal
        n_norm = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
        if n_norm < 1e-10:  # Avoid division by zero
            nx, ny, nz = 0, 1, 0
        else:
            nx, ny, nz = nx / n_norm, ny / n_norm, nz / n_norm

        normals.append((nx, ny, nz))

        # Calculate binormal as cross product
        bx = ty * nz - tz * ny
        by = tz * nx - tx * nz
        bz = tx * ny - ty * nx

        binormals.append((bx, by, bz))

    # Default radius function (constant radius)
    if radius_func is None:
        def radius_func(t):
            return 1.0

    # Generate tube vertices around the curve
    for i, (x, y, z) in enumerate(curve_points):
        nx, ny, nz = normals[i]
        bx, by, bz = binormals[i]

        # Variable radius at this point
        current_radius = base_radius * radius_func(t[i])

        for theta_val in theta:
            # Calculate position on circle around curve
            cx = x + current_radius * (nx * np.cos(theta_val) + bx * np.sin(theta_val))
            cy = y + current_radius * (ny * np.cos(theta_val) + by * np.sin(theta_val))
            cz = z + current_radius * (nz * np.cos(theta_val) + bz * np.sin(theta_val))

            # Apply tilt and rotation transformations before positioning on sun
            if tilt != 0 or rotation != 0:
                # Create tilt rotation matrix (tilt around y-axis)
                Rtilt = np.array([
                    [np.cos(tilt), 0, np.sin(tilt)],
                    [0, 1, 0],
                    [-np.sin(tilt), 0, np.cos(tilt)]
                ])

                # Create rotation matrix around z-axis
                Rrot = np.array([
                    [np.cos(rotation), -np.sin(rotation), 0],
                    [np.sin(rotation), np.cos(rotation), 0],
                    [0, 0, 1]
                ])

                # Apply transformations
                R_orientation = Rrot @ Rtilt
                point = np.array([cx, cy, cz])
                cx, cy, cz = R_orientation @ point

            # Shift to position relative to solar surface
            cz += R_sun

            # Add vertex
            vertices.append([cx, cy, cz])

    vertices = np.array(vertices)

    # Apply rotation to position on sun
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

    # Total rotation for positioning on sun
    R = Rz @ Ry
    vertices = vertices @ R.T

    # Create triangles (faces)
    triangles = []

    # Loop through the grid
    for i in range(n_curve - 1):
        for j in range(n_circle):
            # Calculate indices with appropriate wrapping
            j_next = (j + 1) % n_circle  # Wrap around the circle

            # Indices of the 4 corners
            v00 = i * n_circle + j  # Current vertex
            v01 = i * n_circle + j_next  # Next in circle direction
            v10 = (i + 1) * n_circle + j  # Next in curve direction
            v11 = (i + 1) * n_circle + j_next  # Diagonal

            # Add two triangles to create a quad face
            triangles.append([v00, v01, v11])
            triangles.append([v00, v11, v10])

    triangles = np.array(triangles)

    return vertices, triangles



def sigmoid_curve(t, height=2.0, width=3.0, asymmetry=0.0, turns=1.0):
    """
    Creates an S-shaped curve with variable parameters.

    Args:
        t: Parameter from 0 to 1
        height: Maximum height of the curve
        width: Width of the curve
        asymmetry: Controls asymmetry (0 = symmetric)
        turns: Number of turns/waves in the curve

    Returns:
        tuple: (x, y, z) coordinates
    """
    # Create an S-shape using sin function
    x = width * (2 * t - 1) * (1 + asymmetry * (2 * t - 1))

    # Add some curvature in y-direction
    y = width * 0.3 * np.sin(2 * np.pi * t * turns)

    # Height profile with sigmoid-like shape
    z = height * (1.5 * t - 0.5 * t ** 3) * (1 - 0.7 * t * np.sin(np.pi * t))

    return x, y, z


def spiral_curve(t, height=2.0, radius=2.0, turns=2.5, taper=0.3):
    """
    Creates a spiral curve rising from the surface.

    Args:
        t: Parameter from 0 to 1
        height: Maximum height of the curve
        radius: Radius of the spiral
        turns: Number of turns in the spiral
        taper: How much the radius decreases as height increases

    Returns:
        tuple: (x, y, z) coordinates
    """
    # Calculate the spiral coordinates
    angle = 2 * np.pi * turns * t
    r = radius * (1 - taper * t)

    x = r * np.cos(angle)
    y = r * np.sin(angle)
    z = height * t

    return x, y, z


def loop_with_twist(t, height=2.0, width=3.0, twist=1.5):
    """
    Creates a loop with a twist in the middle.

    Args:
        t: Parameter from 0 to 1
        height: Height of the loop
        width: Width of the loop
        twist: Amount of twisting

    Returns:
        tuple: (x, y, z) coordinates
    """
    # Map t to angle (0 to pi)
    angle = np.pi * t

    # Base loop shape
    x = width * np.sin(angle)
    z = height * np.sin(angle)

    # Add twist in the y direction
    y = width * 0.3 * np.sin(2 * np.pi * twist * t)

    return x, y, z