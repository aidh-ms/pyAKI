from unittest import TestCase
import pandas as pd
import numpy as np


from pyAKI.preprocessors import RRTPreProcessor
from pyAKI.utils import Dataset, DatasetType


class TestRRTPreProcessor(TestCase):
    def setUp(self) -> None:
        self.preprocessor = RRTPreProcessor()

    def test_preprocessor(self):
        rrt_df = pd.DataFrame(
            data={
                "stay_id": [1, 1, 1],
                "rrt_status": [0, 1, np.nan],
            },
            index=pd.to_datetime(
                [
                    "2023-01-01 00:00:00",
                    "2023-01-01 15:00:00",
                    "2023-01-01 23:00:00",
                ]
            ),
        )

        _, df = self.preprocessor.process([Dataset(DatasetType.RRT, rrt_df)])[0]

        pd.testing.assert_series_equal(
            df["rrt_status"],
            pd.Series(
                data=[0] * 15 + [1] * 9,
                name="rrt_status",
                index=pd.MultiIndex.from_arrays(
                    [
                        [1] * 24,
                        pd.period_range(
                            start="2023-01-01 00:00:00",
                            end="2023-01-01 23:00:00",
                            freq="h",
                        ),
                    ],
                    names=("stay_id", ""),
                ),
                dtype=float,
            ),
            check_index=False,
        )
