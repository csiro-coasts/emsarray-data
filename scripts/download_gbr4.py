#!/usr/bin/env python3

import pathlib

import numpy as np

import emsarray
from emsarray.utils import extract_vars

url = "https://thredds.nci.org.au/thredds/dodsC/fx3/gbr4_v2/gbr4_simple_2022-05-12.nc"
out = pathlib.Path("./gbr4.nc")

dataset = emsarray.open_dataset(url)

# Pick only a few variables
dataset = extract_vars(dataset, [
    'zc', 'longitude', 'latitude', 'time',
    'botz', 'eta', 'salt', 'temp',
])

# One timestep
dataset = dataset.isel(time=np.s_[0:1])

# Cast all float64 variables to float32. We don't need the precision in an
# example, and float32's are half the file size.
dataset.update({
    name: data_array.astype(np.single, casting='same_kind')
    for name, data_array in ((name, dataset[name]) for name in dataset.variables.keys())
    if data_array.dtype == np.float64
})


if out.exists():
    out.unlink()

# Set up maximum compression for each variable
for data_array in (dataset[name] for name in dataset.variables.keys()):
    data_array.encoding.update({'zlib': True, 'complevel': 9, 'shuffle': True})
dataset.ems.to_netcdf(out)

print(f"{out.name}: {out.stat().st_size / (1024 ** 2):3.2f}MB")
