#!/usr/bin/env python3
"""
Test the LZ entropy calculator with different patterns.
"""

import sys
sys.path.insert(0, 'src')

from kappa import compute_cid, compute_normalized_cid
import os

def test_pattern(name, data, n_shuffles=5):
    """Test a specific data pattern."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")

    # Basic CID
    cid = compute_cid(data)
    print(f"CID: {cid:.4f}")

    # Normalized CID
    result = compute_normalized_cid(data, n_shuffles=n_shuffles)
    print(f"\nNormalized results:")
    print(f"  CID (original):      {result['cid']:.4f}")
    print(f"  CID (shuffled):      {result['cid_shuffled']:.4f} ± {result['cid_shuffled_std']:.4f}")
    print(f"  CID (normalized):    {result['cid_normalized']:.4f}")
    print(f"  Compression gain:    {result['compression_gain']:.4f} ({result['compression_gain']*100:.1f}%)")

    return result

if __name__ == '__main__':
    print("LZ Entropy Calculator Tests")
    print("="*60)

    # Test 1: Repeated pattern
    test_pattern("Repeated pattern (ABCABC...)", b"ABCABCABCABC")

    # Test 2: Highly ordered (all same)
    test_pattern("Highly ordered (AAA...)", b"A" * 100)

    # Test 3: Random data
    test_pattern("Random data", os.urandom(100))

    # Test 4: More complex pattern
    test_pattern("Complex pattern", b"AABBCCAABBCCAABBCC" * 5)

    print("\n" + "="*60)
    print("tests done\n")
