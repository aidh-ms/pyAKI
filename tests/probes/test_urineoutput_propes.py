import sys

from unittest import TestCase
from pathlib import Path
from datetime import datetime

import pandas as pd

# sys.path.append(str(Path(__file__).parent.parent))
from pyAKI.probes import (
    UrineOutputProbe,
    AbstractCreatinineProbe,
    AbsoluteCreatinineProbe,
    Dataset,
    DatasetType,
)


class TestUrineOutputProbe(TestCase):
    def setUp(self) -> None:
        self.probe = UrineOutputProbe()

    def test_anuria(self):
        urine_output_df = pd.DataFrame(
            data={"urineoutput": [0] * 12},
            index=pd.DatetimeIndex(
                data=[
                    "2023-01-01 00:00:00",
                    "2023-01-01 01:00:00",
                    "2023-01-01 02:00:00",
                    "2023-01-01 03:00:00",
                    "2023-01-01 04:00:00",
                    "2023-01-01 05:00:00",
                    "2023-01-01 06:00:00",
                    "2023-01-01 07:00:00",
                    "2023-01-01 08:00:00",
                    "2023-01-01 09:00:00",
                    "2023-01-01 10:00:00",
                    "2023-01-01 11:00:00",
                ],
                name="charttime",
            ),
        )

        demographics = pd.Series(data={"weight": 100})

        _type, df = self.probe.probe(
            [
                Dataset(DatasetType.URINEOUTPUT, urine_output_df),
                Dataset(DatasetType.DEMOGRAPHICS, demographics),
            ]
        )[0]

        pd.testing.assert_series_equal(
            df["urineoutput_stage"],
            pd.Series(
                data=[0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 3],
                name="urineoutput_stage",
                index=pd.DatetimeIndex(
                    data=[
                        "2023-01-01 00:00:00",
                        "2023-01-01 01:00:00",
                        "2023-01-01 02:00:00",
                        "2023-01-01 03:00:00",
                        "2023-01-01 04:00:00",
                        "2023-01-01 05:00:00",
                        "2023-01-01 06:00:00",
                        "2023-01-01 07:00:00",
                        "2023-01-01 08:00:00",
                        "2023-01-01 09:00:00",
                        "2023-01-01 10:00:00",
                        "2023-01-01 11:00:00",
                    ]
                ),
            ),
            check_index=False,
        )

    def test_aki(self):
        urine_output_df = pd.DataFrame(
            data={"urineoutput": [25] * 24},
            index=pd.DatetimeIndex(
                data=[
                    "2023-01-01 00:00:00",
                    "2023-01-01 01:00:00",
                    "2023-01-01 02:00:00",
                    "2023-01-01 03:00:00",
                    "2023-01-01 04:00:00",
                    "2023-01-01 05:00:00",
                    "2023-01-01 06:00:00",
                    "2023-01-01 07:00:00",
                    "2023-01-01 08:00:00",
                    "2023-01-01 09:00:00",
                    "2023-01-01 10:00:00",
                    "2023-01-01 11:00:00",
                    "2023-01-01 12:00:00",
                    "2023-01-01 13:00:00",
                    "2023-01-01 14:00:00",
                    "2023-01-01 15:00:00",
                    "2023-01-01 16:00:00",
                    "2023-01-01 17:00:00",
                    "2023-01-01 18:00:00",
                    "2023-01-01 19:00:00",
                    "2023-01-01 20:00:00",
                    "2023-01-01 21:00:00",
                    "2023-01-01 22:00:00",
                    "2023-01-01 23:00:00",
                ],
                name="charttime",
            ),
        )

        demographics = pd.Series(data={"weight": 100})

        _type, df = self.probe.probe(
            [
                Dataset(DatasetType.URINEOUTPUT, urine_output_df),
                Dataset(DatasetType.DEMOGRAPHICS, demographics),
            ]
        )[0]

        pd.testing.assert_series_equal(
            df["urineoutput_stage"],
            pd.Series(
                data=[
                    0,
                    0,
                    0,
                    0,
                    0,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    2,
                    3,
                ],
                name="urineoutput_stage",
                index=pd.DatetimeIndex(
                    data=[
                        "2023-01-01 00:00:00",
                        "2023-01-01 01:00:00",
                        "2023-01-01 02:00:00",
                        "2023-01-01 03:00:00",
                        "2023-01-01 04:00:00",
                        "2023-01-01 05:00:00",
                        "2023-01-01 06:00:00",
                        "2023-01-01 07:00:00",
                        "2023-01-01 08:00:00",
                        "2023-01-01 09:00:00",
                        "2023-01-01 10:00:00",
                        "2023-01-01 11:00:00",
                        "2023-01-01 12:00:00",
                        "2023-01-01 13:00:00",
                        "2023-01-01 14:00:00",
                        "2023-01-01 15:00:00",
                        "2023-01-01 16:00:00",
                        "2023-01-01 17:00:00",
                        "2023-01-01 18:00:00",
                        "2023-01-01 19:00:00",
                        "2023-01-01 20:00:00",
                        "2023-01-01 21:00:00",
                        "2023-01-01 22:00:00",
                        "2023-01-01 23:00:00",
                    ]
                ),
            ),
            check_index=False,
        )
