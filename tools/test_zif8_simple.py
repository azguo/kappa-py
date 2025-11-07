#!/usr/bin/env python3
"""
Simple test: Compute CID from ZIF-8 LAMMPS data file.
"""

import sys
sys.path.insert(0, 'src')

import numpy as np
from pathlib import Path
from kappa import read_lammps_data, filter_by_atom_type, bin_particles_3d, compute_normalized_cid

def test_zif8(data_file):
    """Test CID computation on ZIF-8 structure."""

    print(f"Reading: {data_file}")
    print("="*60)

    # Read structure
    data = read_lammps_data(data_file)

    print(f"\nStructure info:")
    print(f"  Total atoms: {data['natoms']}")
    print(f"  Atom types: {data['ntypes']}")
    print(f"  Box: {data['box']['Lx']:.3f} x {data['box']['Ly']:.3f} x {data['box']['Lz']:.3f} Å")

    # Count atoms by type
    coords = data['coords']
    type_names = {
        1: 'Zn', 2: 'N', 3: 'C', 4: 'C', 5: 'C',
        6: 'H', 7: 'H', 8: 'H', 9: 'H', 10: 'Ar'
    }

    print(f"\nAtom counts:")
    for atype in range(1, data['ntypes'] + 1):
        count = int(np.sum(coords[:, 0] == atype))
        name = type_names.get(atype, f'Type{atype}')
        print(f"  {name:3s}: {count:5d}")

    # Binning parameters
    box_size = data['box']['Lx']  # Assuming cubic
    nbins = 32

    print(f"\nBinning parameters:")
    print(f"  Box size: {box_size:.3f} Å")
    print(f"  Number of bins: {nbins}³ = {nbins**3} bins")
    print(f"  Bin width: {box_size/nbins:.3f} Å")

    # Test 1: All atoms
    print(f"\n{'='*60}")
    print("Test 1: All atoms")
    print("="*60)

    binned_str = bin_particles_3d(coords, nbins=nbins, box_size=box_size)
    print(f"Binned string length: {len(binned_str)}")
    print(f"First 100 chars: {binned_str[:100]}...")

    binned_bytes = binned_str.encode('utf-8')
    result = compute_normalized_cid(binned_bytes, n_shuffles=5)

    print(f"\nCID results (all atoms):")
    print(f"  CID (original):      {result['cid']:.4f}")
    print(f"  CID (shuffled):      {result['cid_shuffled']:.4f} ± {result['cid_shuffled_std']:.4f}")
    print(f"  CID (normalized):    {result['cid_normalized']:.4f}")
    print(f"  Compression gain:    {result['compression_gain']:.4f} ({result['compression_gain']*100:.1f}%)")

    # Test 2: Zn only (metal nodes)
    print(f"\n{'='*60}")
    print("Test 2: Zn sublattice only")
    print("="*60)

    zn_coords = filter_by_atom_type(data, [1])
    print(f"Zn atoms: {len(zn_coords)}")

    binned_str = bin_particles_3d(zn_coords, nbins=nbins, box_size=box_size)
    binned_bytes = binned_str.encode('utf-8')
    result_zn = compute_normalized_cid(binned_bytes, n_shuffles=5)

    print(f"\nCID results (Zn only):")
    print(f"  CID (original):      {result_zn['cid']:.4f}")
    print(f"  CID (shuffled):      {result_zn['cid_shuffled']:.4f} ± {result_zn['cid_shuffled_std']:.4f}")
    print(f"  CID (normalized):    {result_zn['cid_normalized']:.4f}")
    print(f"  Compression gain:    {result_zn['compression_gain']:.4f} ({result_zn['compression_gain']*100:.1f}%)")

    # Test 3: Framework (no H or guests)
    print(f"\n{'='*60}")
    print("Test 3: Framework (Zn + N + C, no H or Ar)")
    print("="*60)

    framework_coords = filter_by_atom_type(data, [1, 2, 3, 4, 5])
    print(f"Framework atoms: {len(framework_coords)}")

    binned_str = bin_particles_3d(framework_coords, nbins=nbins, box_size=box_size)
    binned_bytes = binned_str.encode('utf-8')
    result_fw = compute_normalized_cid(binned_bytes, n_shuffles=5)

    print(f"\nCID results (framework):")
    print(f"  CID (original):      {result_fw['cid']:.4f}")
    print(f"  CID (shuffled):      {result_fw['cid_shuffled']:.4f} ± {result_fw['cid_shuffled_std']:.4f}")
    print(f"  CID (normalized):    {result_fw['cid_normalized']:.4f}")
    print(f"  Compression gain:    {result_fw['compression_gain']:.4f} ({result_fw['compression_gain']*100:.1f}%)")

    # Test 4: Guests only (if present)
    ar_coords = filter_by_atom_type(data, [10])
    if len(ar_coords) > 0:
        print(f"\n{'='*60}")
        print("Test 4: Argon guests only")
        print("="*60)
        print(f"Ar atoms: {len(ar_coords)}")

        binned_str = bin_particles_3d(ar_coords, nbins=nbins, box_size=box_size)
        binned_bytes = binned_str.encode('utf-8')
        result_ar = compute_normalized_cid(binned_bytes, n_shuffles=5)

        print(f"\nCID results (Ar guests):")
        print(f"  CID (original):      {result_ar['cid']:.4f}")
        print(f"  CID (shuffled):      {result_ar['cid_shuffled']:.4f} ± {result_ar['cid_shuffled_std']:.4f}")
        print(f"  CID (normalized):    {result_ar['cid_normalized']:.4f}")
        print(f"  Compression gain:    {result_ar['compression_gain']:.4f} ({result_ar['compression_gain']*100:.1f}%)")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print("="*60)
    print(f"{'Subset':<20} {'CID_norm':<12} {'Interpretation'}")
    print("-"*60)
    print(f"{'All atoms':<20} {result['cid_normalized']:<12.4f} ", end="")
    print("Highly ordered" if result['cid_normalized'] < 0.7 else "Moderately ordered")

    print(f"{'Zn sublattice':<20} {result_zn['cid_normalized']:<12.4f} ", end="")
    print("Highly ordered" if result_zn['cid_normalized'] < 0.7 else "Moderately ordered")

    print(f"{'Framework':<20} {result_fw['cid_normalized']:<12.4f} ", end="")
    print("Highly ordered" if result_fw['cid_normalized'] < 0.7 else "Moderately ordered")

    if len(ar_coords) > 0:
        print(f"{'Ar guests':<20} {result_ar['cid_normalized']:<12.4f} ", end="")
        print("Highly ordered" if result_ar['cid_normalized'] < 0.7 else "Disordered")

    print("\n" + "="*60)
    print("Test complete!")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Test CID on ZIF-8 structure')
    parser.add_argument('data_file', type=Path, help='LAMMPS data file')

    args = parser.parse_args()

    test_zif8(args.data_file)
