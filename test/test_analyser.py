from unittest import TestCase

import pandas as pd

from pyAKI.probes import Dataset, DatasetType
from pyAKI.kdigo import Analyser


class TestAnalyser(TestCase):
    def test_validation_data(self):
        rrt_df = pd.DataFrame(
            data={
                "rrt_status": [0] * 24 + [1] * 23 + [0] * 23 + [1] * 22 + [-1],
            },
            index=pd.period_range(
                start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"
            ),
        )

        with self.assertRaises(ValueError):
            Analyser(
                [
                    Dataset(
                        DatasetType.RRT,
                        rrt_df,
                    ),
                ],
                probes=[],
                preprocessors=[],
            )
