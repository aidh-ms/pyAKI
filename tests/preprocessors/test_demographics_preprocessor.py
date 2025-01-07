from unittest import TestCase
import pandas as pd

from pyAKI.preprocessors import DemographicsPreProcessor
from pyAKI.utils import Dataset, DatasetType


class TestDemographicsPreProcessor(TestCase):
    def setUp(self) -> None:
        self.preprocessor = DemographicsPreProcessor()

    def test_preprocessor(self):
        demo_df = pd.DataFrame(
            data={
                "stay_id": [1, 1],
                "weight": [99, 100],
            },
        )

        _, df = self.preprocessor.process([Dataset(DatasetType.DEMOGRAPHICS, demo_df)])[0]

        pd.testing.assert_series_equal(
            df["weight"],
            pd.Series(data=[100], name="weight", index=[1]),
            check_index=False,
        )
