"""Compare reproduced RAiDER delay cubes against the originals.

Usage: python compare.py ORIG_DIR NEW_DIR [GLOB]
"""
import glob
import os
import sys

import numpy as np
import xarray as xr

orig_dir, new_dir = sys.argv[1], sys.argv[2]
pattern = sys.argv[3] if len(sys.argv) > 3 else '*.nc'

for new in sorted(glob.glob(os.path.join(new_dir, pattern))):
    name = os.path.basename(new)
    orig = os.path.join(orig_dir, name)
    if not os.path.exists(orig):
        print(f'{name}: no original')
        continue
    a, b = xr.open_dataset(orig), xr.open_dataset(new)
    print(f'== {name}')
    for c in ('x', 'y', 'z'):
        same = a[c].shape == b[c].shape and np.allclose(a[c], b[c])
        print(f'  {c}: shape {a[c].shape} vs {b[c].shape}, equal={same}')
    for v in ('hydro', 'wet'):
        if a[v].shape != b[v].shape:
            print(f'  {v}: shape mismatch {a[v].shape} vs {b[v].shape}')
            continue
        d = np.abs(a[v].values - b[v].values)
        nan_same = np.array_equal(np.isnan(a[v].values), np.isnan(b[v].values))
        print(f'  {v}: max|diff|={np.nanmax(d):.3e} m, mean|orig|={np.nanmean(np.abs(a[v].values)):.4f} m, '
              f'identical={np.array_equal(a[v].values, b[v].values, equal_nan=True)}, same NaN mask={nan_same}')
