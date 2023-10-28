#! /usr/bin/env python3

import typer

from pathlib import Path

import pandas as pd

from pyAKI.kdigo import Analyser
from pyAKI.utils import Dataset, DatasetType


def main(
    path: str,
    urineoutput_file: str = "urineoutput.csv",
    creatinine_file: str = "creatinine.csv",
    rrt_file: str = "rrt.csv",
    demographics_file: str = "demographics.csv",
):
    root_dir = Path(path)
    datasets = []

    if (ou_file := root_dir / urineoutput_file).is_file():
        datasets.append(Dataset(DatasetType.URINEOUTPUT, pd.read_csv(ou_file)))

    if (scr_file := root_dir / creatinine_file).is_file():
        datasets.append(Dataset(DatasetType.CREATININE, pd.read_csv(scr_file)))

    if (rrt_file := root_dir / rrt_file).is_file():
        datasets.append(Dataset(DatasetType.RRT, pd.read_csv(rrt_file)))

    if (demo_file := root_dir / demographics_file).is_file():
        datasets.append(Dataset(DatasetType.DEMOGRAPHICS, pd.read_csv(demo_file)))

    ana: Analyser = Analyser(datasets)
    ana.process_stays().to_csv(root_dir / "aki.csv")


if __name__ == "__main__":
    typer.run(main)
