from unittest import TestCase

import pandas as pd

from pyaki.preprocessors import TimeIndexCreator
from pyaki.utils import Dataset, DatasetType


class TestTimeIndexCreator(TestCase):
    def setUp(self) -> None:
        self.preprocessor = TimeIndexCreator()

    def test_preprocessor(self):
        rrt_df = pd.DataFrame(
            data={
                "stay_id": [1, 1, 1],
                "rrt_status": [0, 1, pd.NA],
                "charttime": [
                    "2023-01-01 00:00:00",
                    "2023-01-01 15:00:00",
                    "2023-01-01 23:00:00",
                ],
            },
        )

        _, df = self.preprocessor.process([Dataset(DatasetType.RRT, rrt_df)])[0]

        pd.testing.assert_series_equal(
            df["rrt_status"],
            pd.Series(
                data=[0, 1, pd.NA],
                name="rrt_status",
                index=pd.to_datetime(
                    [
                        "2023-01-01 00:00:00",
                        "2023-01-01 15:00:00",
                        "2023-01-01 23:00:00",
                    ]
                ),
            ),
            check_index=False,
        )
