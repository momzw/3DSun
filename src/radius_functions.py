import numpy as np


__all__ = [
    'tapered_ends_radius',
    'bulging_radius',
    'multi_bulge_radius',
    'wavy_radius',
    'magnetic_flux_radius',
    'kink_instability_radius',
    'turbulent_radius',
    'composite_radius'
]


def tapered_ends_radius(t, taper_factor=0.5, taper_exp=2.0):
    """
    Creates a tube that is thinner at the endpoints and thicker in the middle.

    Args:
        t: Parameter from 0 to 1 along the curve
        taper_factor: How thin the ends should be (0.5 = 50% of max thickness)
        taper_exp: Controls how quickly the taper occurs (higher = more abrupt)

    Returns:
        float: Radius multiplier (1.0 at the middle, smaller at the ends)
    """
    # Create a parabolic profile: 1.0 at t=0.5, reducing to taper_factor at t=0,1
    return taper_factor + (1.0 - taper_factor) * (1.0 - (2 * t - 1.0) ** taper_exp)


def bulging_radius(t, bulge_factor=1.5, bulge_width=0.3):
    """
    Creates a tube with a bulge in the middle section.

    Args:
        t: Parameter from 0 to 1 along the curve
        bulge_factor: How thick the bulge should be (1.5 = 50% thicker than normal)
        bulge_width: How much of the curve length the bulge covers

    Returns:
        float: Radius multiplier
    """
    # Create a gaussian-like bulge centered at t=0.5
    distance_from_center = (t - 0.5) ** 2
    bulge = bulge_factor * np.exp(-distance_from_center / (2 * bulge_width ** 2))

    # Ensure the base radius is 1.0, with the bulge on top
    return 1.0 + (bulge - 1.0) * (bulge > 1.0)


def multi_bulge_radius(t, n_bulges=3, bulge_factor=1.3):
    """
    Creates a tube with multiple bulged sections along its length.

    Args:
        t: Parameter from 0 to 1 along the curve
        n_bulges: Number of bulges to create
        bulge_factor: How thick each bulge should be

    Returns:
        float: Radius multiplier
    """
    # Create multiple sine-wave bulges
    bulges = 1.0 + (bulge_factor - 1.0) * 0.5 * (1.0 + np.cos(n_bulges * 2 * np.pi * t))
    return bulges


def wavy_radius(t, wavelength=8, amplitude=0.3):
    """
    Creates a tube with a wavy radius that oscillates along the curve.

    Args:
        t: Parameter from 0 to 1 along the curve
        wavelength: Number of complete oscillations along the curve
        amplitude: Magnitude of the oscillation (0.3 = ±30% variation)

    Returns:
        float: Radius multiplier
    """
    # Create a sine wave variation around 1.0
    return 1.0 + amplitude * np.sin(wavelength * 2 * np.pi * t)


def magnetic_flux_radius(t, expansion_factor=3.0, corona_start=0.2):
    """
    Models a solar magnetic flux tube that expands from the photosphere into the corona.

    Args:
        t: Parameter from 0 to 1 along the curve
        expansion_factor: How much the tube expands in the corona
        corona_start: Where along the parameter the corona begins

    Returns:
        float: Radius multiplier
    """
    # Calculate height-dependent expansion like in solar physics models
    # Footpoints at the surface (t=0,1) are thin, expanding in the corona

    # Distance from either footpoint (0 at footpoints, 0.5 at middle)
    height = min(t, 1 - t) / 0.5

    # Sigmoid transition from thin to expanded
    if height < corona_start:
        # Linear increase in the chromosphere
        return 1.0 + (expansion_factor - 1.0) * (height / corona_start)
    else:
        # Full expansion in the corona with slight additional increase
        return expansion_factor + 0.5 * (expansion_factor - 1.0) * (height - corona_start) / (1.0 - corona_start)


def kink_instability_radius(t, kink_center=0.5, kink_width=0.1, kink_factor=1.7):
    """
    Models a magnetic flux tube with a kink instability bulge.

    Args:
        t: Parameter from 0 to 1 along the curve
        kink_center: Location of the kink along the curve
        kink_width: Width of the kink region
        kink_factor: How much the tube expands at the kink

    Returns:
        float: Radius multiplier
    """
    # Localized expansion at the kink instability site
    dist_from_kink = abs(t - kink_center)

    # Gaussian profile for the kink
    kink_profile = np.exp(-(dist_from_kink ** 2) / (2 * kink_width ** 2))

    # Combine base tube (1.0) with the kink expansion
    return 1.0 + (kink_factor - 1.0) * kink_profile


def turbulent_radius(t, seed=42, n_points=10, amplitude=0.2):
    """
    Creates a tube with random radius variations, good for turbulent structures.

    Args:
        t: Parameter from 0 to 1 along the curve
        seed: Random seed for reproducibility
        n_points: Number of control points for the random variation
        amplitude: Maximum magnitude of random variations

    Returns:
        float: Radius multiplier
    """
    # Set the random seed for reproducibility
    np.random.seed(seed)

    # Create random control points
    control_points = np.linspace(0, 1, n_points)
    random_values = 1.0 + amplitude * (2 * np.random.random(n_points) - 1)

    # Interpolate to get a smooth curve
    from scipy.interpolate import interp1d
    interp_func = interp1d(control_points, random_values, kind='cubic', bounds_error=False,
                           fill_value=(random_values[0], random_values[-1]))

    return interp_func(t)


def composite_radius(t, radius_funcs=None, combination_method='multiply', weights=None, **kwargs):
    """
    Combines multiple radius functions for complex tube shapes.

    Args:
        t: Parameter from 0 to 1 along the curve
        radius_funcs: List of radius functions to combine
        combination_method: How to combine the functions ('multiply', 'max', 'add', or 'weighted')
        weights: List of weights for each function (used with 'weighted' method)
        **kwargs: Parameters to pass to the component functions

    Returns:
        float: Combined radius multiplier
    """
    if radius_funcs is None:
        # Default behavior - use standard set of radius functions
        results = [
            tapered_ends_radius(t, **kwargs.get('tapered', {})),
            wavy_radius(t, **kwargs.get('wavy', {})),
            bulging_radius(t, **kwargs.get('bulging', {}))
        ]
    else:
        # Apply each function with its specific parameters from kwargs
        results = []
        for i, func in enumerate(radius_funcs):
            # Get function name to look up parameters
            func_name = func.__name__ if hasattr(func, '__name__') else f'func{i}'
            # Get parameters for this function, or empty dict if none provided
            func_kwargs = kwargs.get(func_name, {})
            # Call the function and save result
            results.append(func(t, **func_kwargs))

    # Apply the selected combination method
    if combination_method == 'multiply':
        # Multiply all effects together
        result = 1.0
        for r in results:
            result *= r
        return result

    elif combination_method == 'max':
        # Take the maximum effect at each point
        return max(results)

    elif combination_method == 'add':
        # Add all effects and normalize
        # First, assume average base value is 1.0 and adjust
        adjusted_sum = sum(results) - (len(results) - 1.0)
        # Ensure we don't go below 0
        return max(0.1, adjusted_sum)

    elif combination_method == 'weighted':
        # Apply weights to each effect
        if weights is None:
            # Default to equal weights
            weights = [1.0 / len(results)] * len(results)
        elif len(weights) != len(results):
            # Mismatch of weights and functions
            raise ValueError(
                f"Number of weights ({len(weights)}) must match number of radius functions ({len(results)})")

        # Calculate weighted sum
        weighted_sum = sum(w * r for w, r in zip(weights, results))
        return weighted_sum

    else:
        raise ValueError(f"Unknown combination method: {combination_method}")
