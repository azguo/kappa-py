"""
LZ77-based compression entropy calculator.
Wrapper around C++ implementation with shuffling normalization.
"""

import subprocess
import tempfile
import os
from pathlib import Path
import numpy as np

# Find the C++ executable
_CPP_DIR = Path(__file__).parent.parent.parent / "cpp" / "lz77"
_LZ_ENTROPY = _CPP_DIR / "lz_entropy"

if not _LZ_ENTROPY.exists():
    raise RuntimeError(
        f"C++ executable not found at {_LZ_ENTROPY}\n"
        f"Please run: cd {_CPP_DIR} && make"
    )


def compute_cid(data, return_stats=False):
    """
    Compute LZ77-based compression entropy (CID).

    Parameters
    ----------
    data : str, bytes, or Path
        Input data. Can be:
        - Path to file
        - String data
        - Bytes data
    return_stats : bool
        If True, return dict with detailed stats instead of just CID

    Returns
    -------
    float or dict
        CID value (bits/char ratio, 0-1), or stats dict if return_stats=True
    """
    # Handle different input types
    if isinstance(data, (str, Path)) and Path(data).exists():
        # It's a file path
        filepath = str(data)
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp_path = None  # Use the actual file
    else:
        # It's data - write to temp file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.dat') as tmp:
            if isinstance(data, str):
                tmp.write(data.encode('utf-8'))
            else:
                tmp.write(data)
            tmp_path = tmp.name
        filepath = tmp_path

    try:
        # Run C++ tool
        result = subprocess.run(
            [str(_LZ_ENTROPY), '-t', filepath],
            capture_output=True,
            text=True,
            check=True
        )

        # Parse tab-delimited output: length\tfactors\tcid
        length, factors, cid = result.stdout.strip().split('\t')

        stats = {
            'length': int(length),
            'factors': int(factors),
            'cid': float(cid)
        }

        return stats if return_stats else stats['cid']

    finally:
        # Clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def compute_normalized_cid(data, n_shuffles=1):
    """
    Compute CID normalized by shuffled baseline.

    This measures spatial structure by comparing actual CID to CID
    of shuffled data (which preserves symbol frequencies but destroys
    spatial correlations).

    Parameters
    ----------
    data : bytes or np.ndarray
        Input data (must be bytes or binary array)
    n_shuffles : int
        Number of shuffles to average over (default: 1)

    Returns
    -------
    dict
        {
            'cid': original CID,
            'cid_shuffled': shuffled CID (mean over n_shuffles),
            'cid_normalized': cid / cid_shuffled,
            'compression_gain': 1 - cid_normalized
        }

    Notes
    -----
    - cid_normalized ≈ 1.0: no spatial structure (gas-like)
    - cid_normalized < 1.0: spatial structure present
    - cid_normalized ≈ 0.5: strong spatial order (crystal-like)
    """
    # Convert to bytes if needed
    if isinstance(data, np.ndarray):
        data_bytes = data.tobytes()
    elif isinstance(data, str):
        data_bytes = data.encode('utf-8')
    else:
        data_bytes = data

    # Compute CID of original
    cid_orig = compute_cid(data_bytes)

    # Compute CID of shuffled versions
    cid_shuffled_list = []
    data_array = np.frombuffer(data_bytes, dtype=np.uint8)

    for _ in range(n_shuffles):
        shuffled = np.random.permutation(data_array)
        cid_shuf = compute_cid(shuffled.tobytes())
        cid_shuffled_list.append(cid_shuf)

    cid_shuffled_mean = np.mean(cid_shuffled_list)

    # Normalize
    if cid_shuffled_mean > 0:
        cid_normalized = cid_orig / cid_shuffled_mean
        compression_gain = 1.0 - cid_normalized
    else:
        cid_normalized = 1.0
        compression_gain = 0.0

    return {
        'cid': cid_orig,
        'cid_shuffled': cid_shuffled_mean,
        'cid_shuffled_std': np.std(cid_shuffled_list) if n_shuffles > 1 else 0.0,
        'cid_normalized': cid_normalized,
        'compression_gain': compression_gain
    }


def batch_process(filepaths, normalized=True, n_shuffles=1, verbose=False):
    """
    Process multiple files in batch.

    Parameters
    ----------
    filepaths : list of Path or str
        List of files to process
    normalized : bool
        If True, compute normalized CID (requires reading files as binary)
    n_shuffles : int
        Number of shuffles per file (if normalized=True)
    verbose : bool
        Print progress

    Returns
    -------
    dict
        Mapping filepath -> results dict
    """
    results = {}

    for i, filepath in enumerate(filepaths):
        if verbose:
            print(f"Processing {i+1}/{len(filepaths)}: {filepath}")

        filepath = Path(filepath)

        if normalized:
            # Read as binary for shuffling
            data = filepath.read_bytes()
            results[str(filepath)] = compute_normalized_cid(data, n_shuffles)
        else:
            # Just compute CID
            cid = compute_cid(filepath)
            results[str(filepath)] = {'cid': cid}

    return results
