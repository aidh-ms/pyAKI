from unittest import TestCase
import pandas as pd

from pyAKI.probes import RRTProbe, Dataset, DatasetType
from pyAKI.kdigo import Analyser

from .set_up import setup_validation_data


class TestRRTProbe(TestCase):
    def setUp(self) -> None:
        self.validation_data, self.validation_data_unlabelled = setup_validation_data()
        self.probe = RRTProbe()

    def test_rrt_probe(self):
        rrt_df = pd.DataFrame(
            data={
                "rrt_status": [0] * 24 + [1] * 23 + [0] * 23 + [1] * 23,
            },
            index=pd.period_range(
                start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"
            ),
        )

        _, df = self.probe.probe([Dataset(DatasetType.RRT, rrt_df)])[0]

        pd.testing.assert_series_equal(
            df["rrt_stage"],
            pd.Series(
                data=[0] * 24 + [3] * 23 + [0] * 23 + [3] * 23,
                name="rrt_stage",
                index=pd.period_range(
                    start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"
                ),
                dtype=float,
            ),
            check_index=False,
        )

    def test_validation_data(self):
        analyser = Analyser(
            [
                Dataset(
                    DatasetType.RRT,
                    self.validation_data_unlabelled[["rrt_status"]],
                ),
            ],
            probes=[RRTProbe()],
            preprocessors=[],
        )

        df = analyser.process_stays()

        calculated_labels = df["rrt_stage"].astype(float)
        true_labels = self.validation_data["rrt_stage"]

        pd.testing.assert_series_equal(
            calculated_labels,
            true_labels,
            check_index=False,
        )
