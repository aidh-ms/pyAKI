from unittest import TestCase

import pandas as pd
import numpy as np
from pyAKI.probes import (
    RelativeCreatinineProbe,
    AbsoluteCreatinineProbe,
    CreatinineBaselineMethod,
    AbstractCreatinineProbe,
    Dataset,
    DatasetType,
)
from pyAKI.kdigo import Analyser

from ..set_up import setup_validation_data


class TestAbsCreatinineProbe(TestCase):
    def setUp(self) -> None:
        self.validation_data, self.validation_data_unlabelled = setup_validation_data()
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

    def test_validation_data(self):
        analyser = Analyser(
            [
                Dataset(
                    DatasetType.CREATININE,
                    self.validation_data_unlabelled[["creat"]],
                ),
                Dataset(
                    DatasetType.DEMOGRAPHICS,
                    self.validation_data_unlabelled[["weight"]],
                ),
            ],
            probes=[AbsoluteCreatinineProbe()],
            preprocessors=[],
        )

        df = analyser.process_stays()

        pd.testing.assert_series_equal(
            df["abs_creatinine_stage"],
            self.validation_data["abs_creatinine_stage"],
            check_index=False,
        )


class TestRelCreatinineProbe(TestCase):
    def setUp(self) -> None:
        self.validation_data, self.validation_data_unlabelled = setup_validation_data()
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

    def test_validation_data(self):
        analyser = Analyser(
            [
                Dataset(
                    DatasetType.CREATININE,
                    self.validation_data_unlabelled[["creat"]],
                ),
                Dataset(
                    DatasetType.DEMOGRAPHICS,
                    self.validation_data_unlabelled[["weight"]],
                ),
            ],
            probes=[RelativeCreatinineProbe()],
            preprocessors=[],
        )

        df = analyser.process_stays()

        pd.testing.assert_series_equal(
            df["rel_creatinine_stage"],
            self.validation_data["rel_creatinine_stage"],
            check_index=False,
        )


class TestBaselineCreatinine(TestCase):
    def test_rolling_min_baseline(self):
        probe = AbstractCreatinineProbe(
            baseline_timeframe="1d", method=CreatinineBaselineMethod.ROLLING_MIN
        )
        series = pd.Series(
            data=[1.0] * 47 + [1.5] * 23 + [2.0] * 23,
            name="creat",
            index=pd.period_range(
                start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"
            ),
        )

        self._test_helper(probe, series)

    def test_rolling_first_baseline(self):
        probe = AbstractCreatinineProbe(
            baseline_timeframe="1d", method=CreatinineBaselineMethod.ROLLING_FIRST
        )

        series = pd.Series(
            data=[1.0] * 47 + [1.5] * 23 + [2.0] * 23,
            name="creat",
            index=pd.period_range(
                start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"
            ),
        )

        self._test_helper(probe, series)

    def test_rolling_mean_baseline(self):
        probe = AbstractCreatinineProbe(
            baseline_timeframe="1d", method=CreatinineBaselineMethod.ROLLING_MEAN
        )
        series = pd.Series(
            data=[1] * 24 + [1.5] * 23 + [2] * 23 + [3] * 23,
            name="creat",
            index=pd.period_range(
                start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"
            ),
        )
        series = series.rolling(24).mean()  # rolling window of 24 hours
        series = series.bfill()  # backwards fill
        self._test_helper(probe, series)

    def test_fixed_min_baseline(self):
        probe = AbstractCreatinineProbe(
            baseline_timeframe="1d", method=CreatinineBaselineMethod.FIXED_MIN
        )

        series = pd.Series(
            data=[1.0] * 93,
            name="creat",
            index=pd.period_range(
                start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"
            ),
        )

        self._test_helper(probe, series)

    def test_fixed_mean_baseline(self):
        probe = AbstractCreatinineProbe(
            baseline_timeframe="2d", method=CreatinineBaselineMethod.FIXED_MEAN
        )
        data_list = [1] * 24 + [1.5] * 23 + [2] * 23 + [3] * 23
        mean_value = np.mean(data_list[:49])
        series = pd.Series(
            data=[mean_value] * 93,
            name="creat",
            index=pd.period_range(
                start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"
            ),
        )

        self._test_helper(probe, series)

    def test_overall_first_baseline(self):
        probe = AbstractCreatinineProbe(method=CreatinineBaselineMethod.OVERALL_FIRST)

        series = pd.Series(
            data=[1.0] * 93,
            name="creat",
            index=pd.period_range(
                start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"
            ),
        )

        self._test_helper(probe, series)

    def test_overall_min_baseline(self):
        probe = AbstractCreatinineProbe(method=CreatinineBaselineMethod.OVERALL_MIN)

        series = pd.Series(
            data=[1.0] * 93,
            name="creat",
            index=pd.period_range(
                start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"
            ),
        )

        self._test_helper(probe, series)

    def test_overall_mean_baseline(self):
        probe = AbstractCreatinineProbe(method=CreatinineBaselineMethod.OVERALL_MEAN)

        data = [1] * 24 + [1.5] * 23 + [2] * 23 + [3] * 23
        mean_value = np.mean(data)
        series = pd.Series(
            data=[mean_value] * 93,
            name="creat",
            index=pd.period_range(
                start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"
            ),
        )

        self._test_helper(probe, series)

    def test_constant_baseline(self):
        probe = AbstractCreatinineProbe(method=CreatinineBaselineMethod.CONSTANT)

        series = pd.Series(
            data=[1.0] * 93,
            name="creat",
            index=pd.period_range(
                start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"
            ),
        )

        self._test_helper(probe, series)

    def test_calculated_baseline(self):
        probe = AbstractCreatinineProbe(method=CreatinineBaselineMethod.CALCULATED)

        series = pd.Series(
            data=[2.9159636295463067] * 93,
            name="creat",
            index=pd.period_range(
                start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"
            ),
        )

        self._test_helper(probe, series)

    def _test_helper(self, probe, series):
        creatinine_df = pd.DataFrame(
            data={"creat": [1] * 24 + [1.5] * 23 + [2] * 23 + [3] * 23},
            index=pd.period_range(
                start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"
            ),
        )

        patient_df = pd.Series(
            {
                "baseline_constant": 1.0,
                "weight": 90,
                "age": 25,
                "height": 180,
                "gender": "M",
            }
        )

        pd.testing.assert_series_equal(
            probe.creatinine_baseline(
                creatinine_df,
                patient_df,
            ),
            series,
            check_index=False,
        )
