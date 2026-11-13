# RAiDER from a pinned conda-forge release (not from this repository's source).
# Use it to re-run or reproduce outputs made with an older RAiDER version.
#
#   docker build --build-arg RAIDER_VERSION=0.4.2 -t raider:0.4.2 docker/conda-release
#   docker build --build-arg RAIDER_VERSION=0.4.5 -t raider:0.4.5 docker/conda-release
#
# See README.md in this directory for run instructions.
FROM mambaorg/micromamba:1.5.8

LABEL org.opencontainers.image.title="RAiDER (conda-forge release)"
LABEL org.opencontainers.image.description="Raytracing Atmospheric Delay Estimation for RADAR, pinned conda-forge release"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.source="https://github.com/dbekaert/RAiDER"

ARG RAIDER_VERSION=0.4.2
ARG PYTHON_VERSION=3.9

# numpy<2: these RAiDER releases predate numpy 2
# findlibs<0.1: newer findlibs uses py3.10 syntax and breaks eccodes import on py3.9
# libgdal-netcdf/hdf5: conda-forge GDAL >=3.9 ships these drivers as plugins,
# and RAiDER reads weather models through GDAL's netcdf: driver
RUN micromamba install -y -n base -c conda-forge \
        python=${PYTHON_VERSION} \
        raider=${RAIDER_VERSION} \
        "numpy<2" \
        "findlibs<0.1" \
        cdsapi \
        libgdal-netcdf \
        libgdal-hdf5 \
    && micromamba clean --all --yes

ARG MAMBA_DOCKERFILE_ACTIVATE=1
RUN python -c "import RAiDER, xarray, cdsapi; print('RAiDER', RAiDER.__version__)" \
    && gdalinfo --formats | grep netCDF > /dev/null

COPY --chown=$MAMBA_USER:$MAMBA_USER compare.py profile.py /opt/raider-tools/

WORKDIR /work
ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "raider.py"]
