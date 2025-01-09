#! /usr/bin/env python3
"""pyaki CLI tool"""

from pathlib import Path

import pandas as pd
import typer

from pyaki.kdigo import Analyser
from pyaki.utils import Dataset, DatasetType


def main(
    path: str,
    urineoutput_file: str = "urineoutput.csv",
    creatinine_file: str = "creatinine.csv",
    rrt_file: str = "rrt.csv",
    demographics_file: str = "demographics.csv",
) -> None:
    """
    CLI tool to process AKI stages from time series data.

    CLI tool to process AKI stages from time series data. The tool expects
    the following files to be present in the given path: urineoutput.csv, creatinine.csv, rrt.csv, demographics.csv.

    Parameters
    ----------
    path : str
        Path to the folder containing the data files.
    urineoutput_file : str, optional
        Name of the file containing urine output data, by default "urineoutput.csv"
    creatinine_file : str, optional
        name of the file containing creatinine data, by default "creatinine.csv"
    rrt_file : str, optional
        Name of the file containing rrt data, by default "rrt.csv"
    demographics_file : str, optional
        Name of the file containing demographic data of the patient like the patients weight, by default "demographics.csv"
    """
    root_dir = Path(path)
    datasets = []

    if (ou_file := root_dir / urineoutput_file).is_file():
        datasets.append(Dataset(DatasetType.URINEOUTPUT, pd.read_csv(ou_file)))

    if (scr_file := root_dir / creatinine_file).is_file():
        datasets.append(Dataset(DatasetType.CREATININE, pd.read_csv(scr_file)))

    if (_rrt_file := root_dir / rrt_file).is_file():
        datasets.append(Dataset(DatasetType.RRT, pd.read_csv(_rrt_file)))

    if (demo_file := root_dir / demographics_file).is_file():
        datasets.append(Dataset(DatasetType.DEMOGRAPHICS, pd.read_csv(demo_file)))

    ana: Analyser = Analyser(datasets)
    ana.process_stays().to_csv(root_dir / "aki.csv")


def run() -> None:
    """Run the CLI tool"""
    typer.run(main)


if __name__ == "__main__":
    run()
