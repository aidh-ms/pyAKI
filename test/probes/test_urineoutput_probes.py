from unittest import TestCase

import pandas as pd

from pyAKI.probes import UrineOutputProbe, Dataset, DatasetType, UrineOutputMethod
from pyAKI.kdigo import Analyser

from .set_up import setup_validation_data


class TestUrineOutputProbe(TestCase):
    def setUp(self) -> None:
        self.validation_data, self.validation_data_unlabelled = setup_validation_data()
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
                dtype=float,
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
                dtype=float,
            ),
            check_index=False,
        )

    def test_validation_data(self):
        analyser = Analyser(
            [
                Dataset(
                    DatasetType.URINEOUTPUT,
                    self.validation_data_unlabelled[["urineoutput"]],
                ),
                Dataset(
                    DatasetType.DEMOGRAPHICS,
                    self.validation_data_unlabelled[["weight"]]
                    .groupby("stay_id")
                    .first(),
                ),
            ],
            probes=[UrineOutputProbe()],
            preprocessors=[],
        )

        df = analyser.process_stays()

        pd.testing.assert_series_equal(
            df["urineoutput_stage"].astype(float),
            self.validation_data["urineoutput_stage"],
        )

    def test_aki_strict(self):
        urine_output_df = pd.DataFrame(
            data={"urineoutput": [100] + [25] * 24},
            index=pd.period_range(
                start="2023-01-01 00:00:00", end="2023-01-02 00:00:00", freq="h"
            ),
        )

        demographics = pd.Series(data={"weight": 100})

        _, df = UrineOutputProbe(method=UrineOutputMethod.STRICT).probe(
            [
                Dataset(DatasetType.URINEOUTPUT, urine_output_df),
                Dataset(DatasetType.DEMOGRAPHICS, demographics),
            ]
        )[0]

        pd.testing.assert_series_equal(
            df["urineoutput_stage"],
            pd.Series(
                data=[0] * 6 + [1] * 6 + [2] * 12 + [3],
                name="urineoutput_stage",
                index=pd.period_range(
                    start="2023-01-01 00:00:00", end="2023-01-02 00:00:00", freq="h"
                ),
                dtype=float,
            ),
            check_index=False,
        )
