"""Print hydro/wet delay profiles at the cube centre for several files.

Usage: python profile.py FILE [FILE ...]
"""
import sys

import numpy as np
import xarray as xr

HEIGHTS = [0, 500, 1000, 3000, 10000, 30000]

for f in sys.argv[1:]:
    ds = xr.open_dataset(f)
    iy, ix = ds.sizes['y'] // 2, ds.sizes['x'] // 2
    print(f'== {f}  (centre pixel y={iy}, x={ix})')
    for h in HEIGHTS:
        iz = int(np.abs(ds.z.values - h).argmin())
        hy, we = ds.hydro.values[iz, iy, ix], ds.wet.values[iz, iy, ix]
        print(f'  z={ds.z.values[iz]:9.1f} m  hydro={hy:12.5g}  wet={we:12.5g}')
    for v in ('hydro', 'wet'):
        a = ds[v].values
        print(f'  {v}: finite={np.isfinite(a).mean():.3f} min={np.nanmin(a):.4g} max={np.nanmax(a):.4g}')
