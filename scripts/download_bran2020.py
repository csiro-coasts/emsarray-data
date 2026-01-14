#!/usr/bin/env python3

import pathlib

from emsarray_data.pack import copy_variables, pack_variables
from emsarray_data.utils import report, run

url = "https://thredds.nci.org.au/thredds/dodsC/gb6/BRAN/BRAN2020/daily/ocean_temp_2021_12.nc"
out = pathlib.Path("./bran2020.nc")

out_temp = out.with_name(out.stem + ".temp" + out.suffix)

if out.exists():
    out.unlink()
if out_temp.exists():
    out_temp.unlink()

run(
    'ncks',
    '-d', 'Time,0,19',
    '-d', 'xt_ocean,1400,1499',
    '-d', 'yt_ocean,280,379',
    '-d', 'st_ocean,0,29',
    url, out_temp)
copy_variables(out_temp, out, ['Time', 'xt_ocean', 'yt_ocean', 'st_ocean', 'temp'])
run(
    'ncatted',
    '-a', 'standard_name,Time,c,c,time',
    '-a', 'bounds,Time,d,,',
    '-a', 'standard_name,xt_ocean,c,c,latitude',
    '-a', 'standard_name,yt_ocean,c,c,longitude',
    out,
)

out_temp.unlink()

report(out)
