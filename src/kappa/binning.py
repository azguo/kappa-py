"""
Spatial binning of particle coordinates using Hilbert curve.
Based on bin_finalconfig.py
"""

import numpy as np
from hilbertcurve.hilbertcurve import HilbertCurve


def bin_particles_3d(particles, nbins=32, box_size=75):
    """
    Bin particle coordinates into 3D grid using Hilbert curve ordering.

    Parameters
    ----------
    particles : np.ndarray
        Nx4 array: [type, x, y, z]
    nbins : int
        Number of bins per dimension (should be power of 2)
    box_size : float
        Size of simulation box

    Returns
    -------
    str
        Binned configuration as string of digits
    """
    # # Shift particles to ensure all coordinates are positive
    # coords = particles[:, 1:4] +
    coords = particles[:, 1:4]

    # Create 3D histogram
    histo, _ = np.histogramdd(
        coords,
        bins=(nbins, nbins, nbins),
        range=((0, box_size), (0, box_size), (0, box_size))
    )

    # Set up Hilbert curve for space-filling ordering
    p = int(np.log2(nbins**2) / 2)
    N = 3
    hilbert_curve = HilbertCurve(p, N)

    # Get Hilbert curve indices
    indexes = np.zeros((nbins**N, N), dtype=int)
    for i in range(nbins**N):
        coords = hilbert_curve.point_from_distance(i)
        indexes[i, :] = coords

    # Flatten using Hilbert curve ordering
    flattened = [int(histo[x, y, z]) for x, y, z in indexes]
    binned = ''.join([str(i) for i in flattened])

    return binned


def load_xyz_snapshot(filepath):
    """
    Load a snapshot file in xyz format.

    Expected format:
    # type x y z
    1 10.5 20.3 15.2
    ...

    Parameters
    ----------
    filepath : str or Path
        Path to .xyz file

    Returns
    -------
    np.ndarray
        Nx4 array of [type, x, y, z]
    """
    return np.loadtxt(filepath)
