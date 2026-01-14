import pathlib
import shlex
import subprocess


def run(*cmd, **kwargs):
    cmd = list(map(str, cmd))
    print('$', shlex.join(cmd))
    return subprocess.check_call(cmd, **kwargs)


def report(path: pathlib.Path):
    print(f"{path.name}: {path.stat().st_size / (1024 ** 2):3.2f}MB")
