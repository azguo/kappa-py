# kappa-py
Data compression for thermodynamic analysis

---

## Setup

```bash
# 1. Build C++ compression backend
cd cpp/lz77
make
cd ../..

# 2. Install Python package
pip install -e .
```

---

## Quick Start

Process a directory of particle snapshots:

```bash
python scripts/process_polymer_snapshots.py /path/to/snapshots/ \
    --box-size 75.0 \
    --output results.csv
```

This reads all `snapshot_*.xyz` files, containing xyz configurations in a cubic box 
(with side ranging from 0 to 75), bins the particles spatially and takes a Hilbert scan
through the discretized data (default 32 bins per side), and computes CID values.
This script takes in all xyz data, does not distinguish atom types. 

---

## Usage

```bash
python scripts/process_polymer_snapshots.py snapshot_dir [OPTIONS]
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `-o, --output` | Output CSV file | `cid_results.csv` |
| `-n, --nbins` | Bins per dimension | `32` |
| `-b, --box-size` | Simulation box size | `75.0` |
| `--n-shuffles` | Number of shuffles | `1` |
| `--pattern` | Filename pattern | `snapshot_*.xyz` |

### Input Format

Snapshots in `.xyz` format:

```
# type x y z
1 10.5 20.3 15.2
1 12.1 18.7 16.4
...
```

---

## Output

CSV file with columns:

- `cid_normalized` - Structural order metric (0.5 = crystal, 1.0 = gas), cid normed by shuffled cid
- `compression_gain` - Amount of spatial structure
- `cid` - Raw compression ratio
- `cid_shuffled` - Shuffled baseline

---

## Dependencies

- Python 3.8+
- numpy, pandas, hilbertcurve, tqdm
- C++ compiler (for LZ77 backend)


