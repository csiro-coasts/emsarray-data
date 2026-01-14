#!/usr/bin/env python3

import pathlib


from emsarray_data.pack import pack_variables, copy_variables
from emsarray_data.utils import run, report

url = "https://data-cbr.csiro.au/thredds5/dodsC/catch_all/oa-vankirap/SCHISM-hindcast/vankirap_hindcast_202012.nc"
out = pathlib.Path("./vanuatu.nc")

if out.exists():
    out.unlink()

# Make a new output file where we can accumulate variables as we pack them
out_temp = out.with_name(out.stem + ".temp" + out.suffix)
if out_temp.exists():
    out_temp.unlink()


# Fetch one day of data in two-hourly steps.
run('ncks', '-d', 'time,0,23,2', url, out_temp)

# Which variables to copy over and which to pack in to int16s
to_copy = [
    'time',
	'SCHISM_hgrid',
	'SCHISM_hgrid_face_nodes',
	'SCHISM_hgrid_node_x',
	'SCHISM_hgrid_node_y',
    'depth', 'projected_coordinate_system',
]
to_pack = [
    "zos",
    "hs", "t01", "t02", "tp", "dp", "spr",
    "u0", "v0",
]

copy_variables(out_temp, out, to_copy)
pack_variables(out_temp, out, to_pack)

out_temp.unlink()

report(out)
