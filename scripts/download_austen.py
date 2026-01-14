#!/usr/bin/env python3

import pathlib

from emsarray_data.pack import cast_variable, copy_variables, pack_variables
from emsarray_data.utils import report, run

url = "http://data-cbr.csiro.au/opendap/OA_SLE_processed/ARENA_tide/COMPAS_out66_AUSTEn.nc"
out = pathlib.Path("./austen.nc")

out_temp = out.with_name(out.stem + ".temp" + out.suffix)

if out.exists():
    out.unlink()
if out_temp.exists():
    out_temp.unlink()

# The model takes a while to converge, so skip a few days of data.
offset = 5 * 24
records = 24
run(
    'ncks',
    '-d', f'record,{offset},{offset + records - 1}',
    url, out_temp)

copy_variables(out_temp, out, ['t', 'Mesh2', 'Mesh2_face_nodes'])
# This connectivity array has a string-typed start_index.
# This goes against the spec, and raises a warning in emsarray.
# Let's fix it here so our example datasets are well formed.
run('ncatted', '-a', 'start_index,Mesh2_face_nodes,o,i,0', out)

cast_variable(out_temp, out, 'Mesh2_node_x', 'NC_FLOAT')
cast_variable(out_temp, out, 'Mesh2_node_y', 'NC_FLOAT')
cast_variable(out_temp, out, 'Mesh2_depth', 'NC_FLOAT')
pack_variables(out_temp, out, ['eta'])

out_temp.unlink()

report(out)
