from unittest import TestCase

import numpy as np
import pandas as pd

from pyaki.preprocessors import UrineOutputPreProcessor
from pyaki.utils import Dataset, DatasetType


class TestUrineOutputPreProcessor(TestCase):
    def test_preprocessor(self):
        preprocessor = UrineOutputPreProcessor(interpolate=False)

        ou_df = pd.DataFrame(
            data={
                "stay_id": [1, 1, 1, 1],
                "urineoutput": [1, 3, 2, 1],
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

        _, df = preprocessor.process([Dataset(DatasetType.URINEOUTPUT, ou_df)])[0]

        pd.testing.assert_series_equal(
            df["urineoutput"],
            pd.Series(
                data=[4.0] + [np.nan] * 14 + [2] + [np.nan] * 7 + [1],
                name="urineoutput",
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

    def test_interpolate_preprocessor(self):
        preprocessor = UrineOutputPreProcessor(interpolate=True, threshold=1)

        ou_df = pd.DataFrame(
            data={
                "stay_id": [1, 1, 1, 1],
                "urineoutput": [1, 3, 2, 1],
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

        _, df = preprocessor.process([Dataset(DatasetType.URINEOUTPUT, ou_df)])[0]

        pd.testing.assert_series_equal(
            df["urineoutput"],
            pd.Series(
                data=[4.0] + [np.nan] * 13 + [1] * 2 + [np.nan] * 6 + [0.5] * 2,
                name="urineoutput",
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
