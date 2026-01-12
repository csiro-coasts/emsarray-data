#!/usr/bin/env python3

import pathlib

import numpy as np
import xarray as xr

import emsarray  # noqa

url = "http://data-cbr.csiro.au/opendap/OA_SLE_processed/ARENA_tide/COMPAS_out66_AUSTEn.nc"
out = pathlib.Path("./austen.nc")

dataset = xr.open_dataset(url, mask_and_scale=False)

# The model takes a while to converge, so skip a few days of data.
offset = 5 * 24
records = 24
dataset = dataset.isel(record=np.s_[offset:offset + records])


def asfloat(data_array: xr.DataArray) -> xr.DataArray:
    """
    Construct a new dataset by casting the existing dataset to smaller data
    types. We do not need 64 bits of accuracy for this example! This will save
    considerably on filesize
    """
    return data_array.astype(np.single, casting='same_kind')


dataset = xr.Dataset(
    data_vars={
        # Mesh variables
        'Mesh2': dataset['Mesh2'],
        'Mesh2_face_nodes': dataset['Mesh2_face_nodes'],
        'Mesh2_node_x': asfloat(dataset['Mesh2_node_x']),
        'Mesh2_node_y': asfloat(dataset['Mesh2_node_y']),

        # Data variables
        'Mesh2_depth': asfloat(dataset['Mesh2_depth']),
        'eta': asfloat(dataset['eta']),

        # Time coordinate
        't': dataset['t'],
    },
    attrs=dataset.attrs,
)
# This connectivity array has a string-typed start_index.
# This goes against the spec, and raises a warning in emsarray.
# Let's fix it here so our example datasets are well formed.
face_nodes = dataset['Mesh2_face_nodes']
face_nodes.attrs['start_index'] = np.int32(face_nodes.attrs['start_index'])

if out.exists():
    out.unlink()

# Set up maximum compression for each variable
for data_array in (dataset[name] for name in dataset.variables.keys()):
    data_array.encoding.update({'zlib': True, 'complevel': 9, 'shuffle': True})
dataset.ems.to_netcdf(out)
print(f"{out.name}: {out.stat().st_size / (1024 ** 2):3.2f}MB")
