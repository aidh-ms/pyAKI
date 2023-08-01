from unittest import TestCase

import pandas as pd

from pyAKI.probes import (
    RelativeCreatinineProbe,
    AbsoluteCreatinineProbe,
    CreatinineBaselineMethod,
    AbstractCreatinineProbe,
    Dataset,
    DatasetType,
)


class TestAbsCreatinineProbe(TestCase):
    def setUp(self) -> None:
        self.probe = AbsoluteCreatinineProbe(baseline_timeframe="1d")

    def test_abs_creatinine_aki(self):
        creatinine_df = pd.DataFrame(
            data={"creat": [1] * 24 + [1.3] * 23 + [6] * 23},
            index=pd.period_range(
                start="2023-01-01 00:00:00", end="2023-01-03 21:00:00", freq="h"
            ),
        )

        _type, df = self.probe.probe(
            [
                Dataset(DatasetType.CREATININE, creatinine_df),
                Dataset(DatasetType.DEMOGRAPHICS, pd.DataFrame()),
            ]
        )[0]

        pd.testing.assert_series_equal(
            df["abs_creatinine_stage"],
            pd.Series(
                data=[0.0] * 24 + [1.0] * 23 + [3.0] * 23,
                name="abs_creatinine_stage",
                index=pd.period_range(
                    start="2023-01-01 00:00:00", end="2023-01-03 21:00:00", freq="h"
                ),
            ),
            check_index=False,
        )


class TestRelCreatinineProbe(TestCase):
    def setUp(self) -> None:
        self.probe = RelativeCreatinineProbe(baseline_timeframe="1d")

    def test_rel_creatinine_aki(self):
        creatinine_df = pd.DataFrame(
            data={"creat": [1] * 24 + [1.5] * 23 + [2] * 23 + [3] * 23},
            index=pd.period_range(
                start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"
            ),
        )

        _type, df = self.probe.probe(
            [
                Dataset(DatasetType.CREATININE, creatinine_df),
                Dataset(DatasetType.DEMOGRAPHICS, pd.DataFrame()),
            ]
        )[0]

        pd.testing.assert_series_equal(
            df["rel_creatinine_stage"],
            pd.Series(
                data=[0.0] * 24 + [1.0] * 23 + [2.0] * 23 + [3.0] * 23,
                name="rel_creatinine_stage",
                index=pd.period_range(
                    start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"
                ),
            ),
            check_index=False,
        )
