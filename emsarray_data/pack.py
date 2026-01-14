import dataclasses
import pathlib
import re
import tempfile
import textwrap
from typing import Hashable, Sequence

import emsarray
import numpy
import xarray

from .utils import run


# Compute the scale and offset values
@dataclasses.dataclass
class ScaleOffset:
    name: Hashable
    dtype: str
    add_offset: float
    scale_power: int
    fill_value: int


@dataclasses.dataclass
class Constant:
    name: Hashable


def copy_variables(
    source: pathlib.Path,
    dest: pathlib.Path,
    variables: Sequence[Hashable],
) -> None:
    run(
        'ncks', '--no-alphabetize', '-h4', '-L9',
        '-c', '-v', ','.join(map(str, variables)),
        str(source), str(dest)
    )


def cast_variable(
    source: pathlib.Path,
    dest: pathlib.Path,
    variable: Hashable,
    dtype: str,
) -> None:
    script = f"'{variable}' = '{variable}'.convert({dtype})"
    run('ncap2', '-4hHAvC', '-L9', '-s', script, str(source), str(dest))


def pack_variables(
    source: pathlib.Path,
    dest: pathlib.Path,
    variables: Sequence[Hashable] | None = None,
) -> None:
    """
    Copy variables from `source` to `dest`,
    packing them in to int16 with scale_factor and add_offset attributes.
    Useful for compressing float data by dropping the precision.
    """
    scale_offset_values = []

    with emsarray.open_dataset(source, decode_timedelta=False) as dataset:
        if variables is None:
            variables = list(dataset.variables.keys())

        for name in variables:
            var = dataset[name]
            scale_offset_values.append(calculate_packing(var))

    for scale_offset in scale_offset_values:
        pack_variable(source, dest, scale_offset)


def calculate_packing(
    data_array: xarray.DataArray,
) -> ScaleOffset:
    # The data type to pack it in to.
    dtype = numpy.int16
    dtype_netcdf_name = 'short'
    fill_value = numpy.iinfo(dtype).min

    # The float variable will be packed in to a signed integer.
    # To restore the variable to a float:
    #     unpacked = (packed * scale_factor) + add_offset
    # To get the best range of values we use the median for `add_offset`,
    # and then find a suitable `scale_factor`.
    # The simplest `scale_factor` would be (max - min) / distinct_values,
    # but it is nicer if `scale_factor` is a power of two for binary reasons.
    # Thus we find the next largest power of two above this computed scale factor.
    var_min, var_max = data_array.min().values, data_array.max().values
    median = var_min + (var_max - var_min) / 2
    width = var_max - var_min

    # If a variable doesn't actually vary, then we can't really do much with it!
    if width == 0:
        raise ValueError(f"{data_array.name!r} does not vary, so can't pack it sensibly!")

    else:
        # Number of distinct values in a short.
        # Need to reserve a value for the fill_value.
        distinct_values = 2**numpy.iinfo(dtype).bits - 1
        step = width / distinct_values
        # Find the next power of two larger than the step size.
        # Using powers of two avoids some subtle rounding issues with floats.
        step2_power = numpy.ceil(numpy.log2(step))

        add_offset = median
        scale_power = step2_power

    return ScaleOffset(
        name=data_array.name,
        dtype=dtype_netcdf_name,
        add_offset=add_offset,
        scale_power=scale_power,
        fill_value=fill_value,
    )


def pack_variable(
    source: pathlib.Path,
    dest: pathlib.Path,
    scale_offset: ScaleOffset,
) -> None:
    name = scale_offset.name
    dtype = scale_offset.dtype
    add_offset = scale_offset.add_offset
    scale_power = scale_offset.scale_power
    fill_value = scale_offset.fill_value

    script = textwrap.dedent(f"""
    if ('{name}'.has_miss()) {{
        *missing_mask = '{name}'.missing();
    }} else if ('{name}@missing_value'.exists()) {{
        *missing_mask = '{name}' == '{name}@missing_value';
    }} else {{
        // This will raise a warning but we can ignore it
        *missing_mask = '{name}'.missing();
    }}

    '{name}'={dtype}(('{name}' - {add_offset}) / (2^{scale_power}));
    '{name}@scale_factor' = (2^{scale_power});
    '{name}@add_offset' = {add_offset};

    '{name}'.set_miss({fill_value});
    where(missing_mask) '{name}' = {fill_value};
    ram_delete(missing_mask);
    ram_delete('{name}@missing_value');
    """)

    safe_name = re.sub(r'[^a-zA-Z0-9_]+', '-', str(name)).strip('-')
    with tempfile.NamedTemporaryFile(prefix=f'pack-{safe_name}.', suffix='.nco', mode='w+') as script_file:
        script_file.write(script)
        script_file.flush()
        run('ncap2', '-4hHAvC', '-L9', '-S', script_file.name, str(source), str(dest))
