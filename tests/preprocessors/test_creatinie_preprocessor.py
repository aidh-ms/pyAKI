from unittest import TestCase

import numpy as np
import pandas as pd

from pyaki.preprocessors import CreatininePreProcessor
from pyaki.utils import Dataset, DatasetType


class TestCreatininePreProcessor(TestCase):
    def test_preprocessor(self):
        preprocessor = CreatininePreProcessor(ffill=False)

        creat_df = pd.DataFrame(
            data={
                "stay_id": [1, 1, 1, 1],
                "creat": [1, 3, 2, 1],
            },
            index=pd.to_datetime(
                [
                    "2023-01-01 00:00:00",
                    "2023-01-01 00:15:00",
                    "2023-01-01 15:00:00",
                    "2023-01-01 23:00:00",
                ]
            ),
        )

        _, df = preprocessor.process([Dataset(DatasetType.CREATININE, creat_df)])[0]

        pd.testing.assert_series_equal(
            df["creat"],
            pd.Series(
                data=[2.0] + [np.nan] * 14 + [2] + [np.nan] * 7 + [1],
                name="creat",
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
            ),
            check_index=False,
        )

    def test_ffill_preprocessor(self):
        preprocessor = CreatininePreProcessor(ffill=True, threshold=1)

        creat_df = pd.DataFrame(
            data={
                "stay_id": [1, 1, 1, 1],
                "creat": [1, 3, 2, 1],
            },
            index=pd.to_datetime(
                [
                    "2023-01-01 00:00:00",
                    "2023-01-01 00:15:00",
                    "2023-01-01 15:00:00",
                    "2023-01-01 23:00:00",
                ]
            ),
        )

        _, df = preprocessor.process([Dataset(DatasetType.CREATININE, creat_df)])[0]

        pd.testing.assert_series_equal(
            df["creat"],
            pd.Series(
                data=[2.0] * 2 + [np.nan] * 13 + [2] * 2 + [np.nan] * 6 + [1],
                name="creat",
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
            ),
            check_index=False,
        )
