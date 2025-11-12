#!/usr/bin/env python3
"""
Process polymer melt snapshots and compute normalized CID.

This replaces the old process_snapshots.sh pipeline with a single
Python script that:
1. Reads .xyz snapshots
2. Bins particles spatially
3. Computes normalized CID
4. Saves results to CSV
"""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
import argparse
import pandas as pd
from tqdm import tqdm

from kappa.binning import load_xyz_snapshot, bin_particles_3d
from kappa import compute_normalized_cid


def process_snapshot(xyz_file, nbins=32, box_size=75, n_shuffles=1):
    """
    Process a single snapshot file.

    Returns dict with results.
    """
    # Load particles
    particles = load_xyz_snapshot(xyz_file)

    # Bin particles
    binned_str = bin_particles_3d(particles, nbins=nbins, box_size=box_size)
    binned_bytes = binned_str.encode('utf-8')

    # Compute normalized CID
    result = compute_normalized_cid(binned_bytes, n_shuffles=n_shuffles)

    # Add metadata
    result['snapshot'] = xyz_file.name
    result['nbins'] = nbins
    result['n_particles'] = len(particles)

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Process polymer melt snapshots and compute CID'
    )
    parser.add_argument(
        'snapshot_dir',
        type=Path,
        help='Directory containing snapshot_*.xyz files'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default='cid_results.csv',
        help='Output CSV file (default: cid_results.csv)'
    )
    parser.add_argument(
        '-n', '--nbins',
        type=int,
        default=32,
        help='Number of bins per dimension (default: 32)'
    )
    parser.add_argument(
        '-b', '--box-size',
        type=float,
        default=75.0,
        help='Simulation box size (default: 75.0)'
    )
    parser.add_argument(
        '--n-shuffles',
        type=int,
        default=1,
        help='Number of shuffles for normalization (default: 1)'
    )
    parser.add_argument(
        '--pattern',
        type=str,
        default='snapshot_*.xyz',
        help='Filename pattern (default: snapshot_*.xyz)'
    )

    args = parser.parse_args()

    # Find all snapshot files
    snapshot_files = sorted(args.snapshot_dir.glob(args.pattern))

    if not snapshot_files:
        print(f"No files matching {args.pattern} found in {args.snapshot_dir}")
        return

    print(f"Found {len(snapshot_files)} snapshots")
    print(f"Processing with {args.nbins}³ bins...")

    # Process all snapshots
    results = []
    for xyz_file in tqdm(snapshot_files):
        try:
            result = process_snapshot(
                xyz_file,
                nbins=args.nbins,
                box_size=args.box_size,
                n_shuffles=args.n_shuffles
            )
            results.append(result)
        except Exception as e:
            print(f"Error processing {xyz_file}: {e}")
            continue

    # Convert to DataFrame and save
    df = pd.DataFrame(results)

    # Extract snapshot number for sorting
    df['snapshot_num'] = df['snapshot'].str.extract(r'(\d+)').astype(int)
    df = df.sort_values('snapshot_num')

    # Save to CSV
    df.to_csv(args.output, index=False)

    print(f"\nResults saved to {args.output}")
    print(f"\nSummary statistics:")
    print(df[['cid', 'cid_normalized', 'compression_gain']].describe())


if __name__ == '__main__':
    main()
