#!/usr/bin/env python3

import pathlib

import emsarray  # noqa
import numpy as np
import xarray as xr

url = "https://thredds.nci.org.au/thredds/dodsC/gb6/BRAN/BRAN2020/daily/ocean_temp_2021_12.nc"
out = pathlib.Path("./bran2020.nc")

dataset = xr.open_dataset(url)

# Drop some variables
dataset = dataset.drop_vars([
    'Time_bounds', 'st_edges_ocean',
    'average_T1', 'average_T2', 'average_DT',
])

# Fix attribute names for ease of access
dataset['Time'].attrs['standard_name'] = 'time'
del dataset['Time'].attrs['bounds']
dataset['yt_ocean'].attrs['standard_name'] = 'latitude'
dataset['xt_ocean'].attrs['standard_name'] = 'longitude'

# Slice to a smaller spatial and temporal extent
dataset = dataset.isel(
    xt_ocean=np.s_[1400:1500],
    yt_ocean=np.s_[280:380],
    st_ocean=np.s_[0:30],
    Time=np.s_[0:20],
)

if out.exists():
    out.unlink()

# Set up maximum compression for each variable
for data_array in (dataset[name] for name in dataset.variables.keys()):
    data_array.encoding.update({'zlib': True, 'complevel': 9, 'shuffle': True})
dataset.ems.to_netcdf(out)

print(f"{out.name}: {out.stat().st_size / (1024 ** 2):3.2f}MB")
