"""
This module contains cli commands for pyaki.

To use the CLI you can use the `pyaki-cli` command.
For more information on how to use the CLI, run `pyaki-cli --help`.

```bash
Usage: pyaki-cli [OPTIONS] PATH

CLI tool to process AKI stages from time series data.

Arguments:
    *    path      TEXT  [default: None] [required]

Options:
    --urineoutput-file         TEXT  [default: urineoutput.csv]
    --rrt-file                 TEXT  [default: rrt.csv]
    --demographics-file        TEXT  [default: demographics.csv]
    --help                           Show this message and exit.
```
"""
