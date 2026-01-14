#!/usr/bin/env python3

import pathlib

from emsarray_data.pack import cast_variable, copy_variables, pack_variables
from emsarray_data.utils import report, run

url = "https://thredds.nci.org.au/thredds/dodsC/fx3/gbr4_v2/gbr4_simple_2022-05-12.nc"
out = pathlib.Path("./kgari.nc")

out_temp = out.with_name(out.stem + ".temp" + out.suffix)

if out.exists():
    out.unlink()
if out_temp.exists():
    out_temp.unlink()

run(
    'ncks',
    '-d', 'time,0,23',
    '-d', 'i,-130,-61',
    '-d', 'j,70,119',
    url, out_temp)

copy_variables(out_temp, out, ['zc', 'time'])
cast_variable(out_temp, out, 'latitude', 'NC_FLOAT')
cast_variable(out_temp, out, 'longitude', 'NC_FLOAT')
pack_variables(out_temp, out, ['botz', 'eta', 'temp', 'u', 'v'])

out_temp.unlink()

report(out)
