#!/usr/bin/env python3

import pathlib

from emsarray_data.pack import pack_variables, copy_variables
from emsarray_data.utils import run, report

url = "https://thredds.nci.org.au/thredds/dodsC/fx3/gbr4_H4p0_ABARRAr2_OBRAN2020_FG2Gv3_Dhnd/gbr4_simple_2022-10-16.nc"
out = pathlib.Path("./gbr4.nc")
out_temp = out.with_name(out.stem + ".temp" + out.suffix)

if out.exists():
    out.unlink()
if out_temp.exists():
    out_temp.unlink()

run('ncks', '-d', 'time,0,0', url, out_temp)

copy_variables(out_temp, out, ['zc', 'longitude', 'latitude', 'time'])
pack_variables(out_temp, out, ['botz', 'eta', 'salt', 'temp'])

out_temp.unlink()

report(out)
