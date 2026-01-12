#!/usr/bin/env python3

import dataclasses
import pathlib
import tempfile
import textwrap
import shlex
import shutil
import subprocess
import sys

import numpy as np

import emsarray

url = "https://data-cbr.csiro.au/thredds5/dodsC/catch_all/oa-vankirap/SCHISM-hindcast/vankirap_hindcast_202012.nc"
out = pathlib.Path("./vanuatu.nc")

if out.exists():
    out.unlink()

# Make a new output file where we can accumulate variables as we pack them
out_accum = out.with_name(out.stem + "_accum" + out.suffix)
if out_accum.exists():
    out_accum.unlink()


def run(*cmd, **kwargs):
    cmd = list(map(str, cmd))
    print('$', shlex.join(cmd))
    return subprocess.check_call(cmd, **kwargs)


run('ncks', '-d', 'time,0,23,2', url, out)

# Copy over the variables we do _not_ want to pack
dont_pack = [
    'time',
	'SCHISM_hgrid',
	'SCHISM_hgrid_face_nodes',
	'SCHISM_hgrid_node_x',
	'SCHISM_hgrid_node_y',
    'depth', 'projected_coordinate_system',
]
print("Copying variables to output:", ", ".join(dont_pack))
run(
    'ncks', '--no-alphabetize', '-h4',
    '-c', '-v', ','.join(dont_pack),
    str(out), str(out_accum)
)

do_pack = [
    "zos",
    "hs", "t01", "t02", "tp", "dp", "spr",
    "u0", "v0",
]


# Compute the scale and offset values
@dataclasses.dataclass
class ScaleOffset:
    name: str
    dtype: str
    add_offset: float
    scale_power: int
    fill_value: int


scale_offset_values = []
with emsarray.open_dataset(out, decode_timedelta=False) as dataset:
    for name in do_pack:
        var = dataset[name]

        # The float variable will be packed in to a signed integer.
        # To restore the variable to a float:
        #     unpacked = (packed * scale_factor) + add_offset
        # To get the best range of values we use the median for `add_offset`,
        # and then find a suitable `scale_factor`.
        # The simplest `scale_factor` would be (max - min) / distinct_values,
        # but it is nicer if `scale_factor` is a power of two for binary reasons.
        # Thus we find the next largest power of two above this computed scale factor.
        var_min, var_max = var.min().values, var.max().values
        median = var_min + (var_max - var_min) / 2
        width = var_max - var_min

        # If a variable doesn't actually vary, then we can't really do much with it!
        # Just compress it in place later I guess?!
        # TODO Actually copy these variables across, currently they are just dropped entirely.
        if width == 0:
            print(f"Variable {name} is constant, skipping")
            continue

        # Number of distinct values in a short.
        # Need to reserve a value for the fill_value.
        distinct_values = 2**16 - 1
        step = width / distinct_values
        # Find the next power of two larger than the step size.
        # Using powers of two avoids some subtle rounding issues with floats.
        step2_power = np.ceil(np.log2(step))

        # The data type to pack it in to.
        dtype = np.int16
        dtype_netcdf_name = 'short'

        add_offset = median
        scale_power = step2_power
        fill_value = np.iinfo(dtype).min

        scale_offset_values.append(ScaleOffset(
            name=name,
            dtype='short',
            add_offset=add_offset,
            scale_power=scale_power,
            fill_value=fill_value,
        ))

print("Packing variables...")

for scale_offset in scale_offset_values:
    name = scale_offset.name
    dtype = scale_offset.dtype
    add_offset = scale_offset.add_offset
    scale_power = scale_offset.scale_power
    fill_value = scale_offset.fill_value


    script = textwrap.dedent(f"""
    *missing_mask='{name}'.missing();

    '{name}'={dtype_netcdf_name}(('{name}' - {add_offset}) / (2^{scale_power}));
    '{name}@scale_factor' = (2^{scale_power});
    '{name}@add_offset' = {add_offset};

    '{name}'.set_miss({fill_value});
    where(missing_mask) '{name}' = {fill_value};
    ram_delete(missing_mask);
    ram_delete('{name}@missing_value');
    """)

    with tempfile.NamedTemporaryFile(mode='w+') as script_file:
        script_file.write(script)
        script_file.flush()
        run('ncap2', '-4hHAvC', '-L2', '-S', script_file.name, str(out), str(out_accum))

shutil.move(out_accum, out)

print(f"{out.name}: {out.stat().st_size / (1024 ** 2):3.2f}MB")
