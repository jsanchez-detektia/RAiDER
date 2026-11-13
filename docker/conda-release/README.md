# RAiDER conda-release image

Builds RAiDER from a pinned **conda-forge release** instead of this repository's
source (for that, use the `Dockerfile` at the repository root). Use it to re-run
a configuration with the exact RAiDER version that produced existing outputs.

## Build

```bash
docker build --build-arg RAIDER_VERSION=0.4.2 -t raider:0.4.2 docker/conda-release
docker build --build-arg RAIDER_VERSION=0.4.5 -t raider:0.4.5 docker/conda-release
```

`RAIDER_VERSION` is any `raider` version on conda-forge; `PYTHON_VERSION`
(default `3.9`) must be one that version was built for
(`conda search -c conda-forge raider`).

Today's conda-forge no longer resolves a working environment for these old
releases on its own, so the image pins:

| Pin | Why |
|---|---|
| `libgdal-netcdf`, `libgdal-hdf5` | GDAL >= 3.9 on conda-forge ships the netCDF/HDF5 drivers as separate plugins. Without them RAiDER fails reading `netcdf:...weather_files/*.nc` |
| `findlibs<0.1` | `findlibs` >= 0.1 uses Python 3.10 syntax and breaks the eccodes import on Python 3.9 (fatal in 0.4.5) |
| `numpy<2` | These releases predate numpy 2 |

## Run

The image runs as `mambauser` (home `/home/mambauser`), conda prefix
`/opt/conda`, working directory `/work`, entrypoint `raider.py`:

```bash
docker run --rm -u $(id -u):$(id -g) \
  -v ~/.cdsapirc:/home/mambauser/.cdsapirc:ro \
  -v /path/to/data:/home/mambauser/data:ro \
  -v $PWD:/work \
  raider:0.4.2 my_config.yaml
```

- Paths inside the yaml (DEM, orbit files, ...) must be container paths.
- Outputs and `weather_files/` are written to `/work`. If the raw weather
  model files are already in `./weather_files/`, RAiDER reuses them and no
  download (and no CDS login) is needed.

### ERA5 download credentials

ERA5 is downloaded from the Copernicus Climate Data Store
(dataset `reanalysis-era5-complete`) via `cdsapi`:

1. Create an account at <https://cds.climate.copernicus.eu>.
2. Accept the ERA5 licence on the dataset's *Download* tab.
3. Write `~/.cdsapirc` (new CDS format; the old `/api/v2` + `UID:key`
   format stopped working in 2024):

   ```
   url: https://cds.climate.copernicus.eu/api
   key: <your-personal-access-token>
   ```

## Checking outputs

`compare.py` and `profile.py` are copied to `/opt/raider-tools/`:

```bash
# per-file diff of x/y/z grids and hydro/wet cubes, matched by filename
docker run --rm --entrypoint /usr/local/bin/_entrypoint.sh -v $PWD:/work raider:0.4.2 \
  python -I /opt/raider-tools/compare.py original_dir new_dir 'ERA5_*_ztd.nc'

# hydro/wet profile at the cube centre (sanity check of magnitudes)
docker run --rm --entrypoint /usr/local/bin/_entrypoint.sh -v $PWD:/work raider:0.4.2 \
  python -I /opt/raider-tools/profile.py ERA5_tropo_20191207T181700_ztd.nc
```

Expected zenith delays near sea level are roughly 2.3 m hydrostatic and
0.05-0.3 m wet.

## Validation

- **0.4.2**: re-ran 270 ERA5 zenith-delay cubes (bounding box, output
  `EPSG:32630`) from cached weather files; identical grids and NaN masks,
  max difference 0.7 µm against outputs produced in 2024.
- **0.4.5**: with a bounding box and `output_projection: EPSG:32630`, both
  2024 outputs and re-runs contain non-physical values (zeros at the centre
  pixel, wet delays of -5000 m, overflow to ~1e29 / inf). Do not use 0.4.5
  with this configuration.
