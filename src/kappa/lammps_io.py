"""
Read LAMMPS data files and extract coordinates.
"""

import numpy as np
from pathlib import Path


def read_lammps_data(filepath):
    """
    Read LAMMPS data file and extract atom coordinates.

    Parameters
    ----------
    filepath : str or Path
        Path to LAMMPS data file

    Returns
    -------
    dict with keys:
        'coords': np.ndarray (N, 4) - [type, x, y, z]
        'box': dict - box dimensions
        'natoms': int
        'types': dict - atom type info if available
    """
    filepath = Path(filepath)

    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Parse header
    natoms = 0
    ntypes = 0
    box = {}

    for i, line in enumerate(lines):
        if 'atoms' in line:
            natoms = int(line.split()[0])
        elif 'atom types' in line:
            ntypes = int(line.split()[0])
        elif 'xlo xhi' in line:
            vals = line.split()
            box['xlo'] = float(vals[0])
            box['xhi'] = float(vals[1])
        elif 'ylo yhi' in line:
            vals = line.split()
            box['ylo'] = float(vals[0])
            box['yhi'] = float(vals[1])
        elif 'zlo zhi' in line:
            vals = line.split()
            box['zlo'] = float(vals[0])
            box['zhi'] = float(vals[1])
        elif 'Atoms' in line:
            atoms_start = i + 2  # Skip "Atoms" and blank line
            break

    # Calculate box size
    box['Lx'] = box['xhi'] - box['xlo']
    box['Ly'] = box['yhi'] - box['ylo']
    box['Lz'] = box['zhi'] - box['zlo']

    # Read atom coordinates
    coords = []
    for i in range(atoms_start, len(lines)):
        line = lines[i].strip()

        # Stop at next section
        if not line or line.startswith('Velocities') or line.startswith('Bonds'):
            break

        parts = line.split()
        if len(parts) >= 5:  # atom_id mol_id type x y z ...
            atom_type = int(parts[2])
            x = float(parts[4])
            y = float(parts[5])
            z = float(parts[6])
            coords.append([atom_type, x, y, z])

    coords = np.array(coords)

    return {
        'coords': coords,
        'box': box,
        'natoms': natoms,
        'ntypes': ntypes
    }


def filter_by_atom_type(data, atom_types):
    """
    Filter coordinates to only include specific atom types.

    Parameters
    ----------
    data : dict
        Output from read_lammps_data
    atom_types : list of int
        Atom types to keep (e.g., [1, 2] for Zn and N)

    Returns
    -------
    np.ndarray
        Filtered coordinates
    """
    coords = data['coords']
    mask = np.isin(coords[:, 0], atom_types)
    return coords[mask]
