from unittest import TestCase

import pandas as pd

from pyAKI.probes import Dataset, DatasetType
from pyAKI.kdigo import Analyser
from .set_up import setup_validation_data


class TestAnalyser(TestCase):
    def setUp(self) -> None:
        self.validation_data, self.validation_data_unlabelled = setup_validation_data()
        self.validation_data_unlabelled.reset_index(inplace=True)
        self.validation_data_unlabelled.drop(columns=["Unnamed: 11"], inplace=True)

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

    def test_full_analyser(self):
        print(self.validation_data_unlabelled.head())
        results = Analyser(
            [
                Dataset(
                    DatasetType.URINEOUTPUT,
                    self.validation_data_unlabelled[
                        ["stay_id", "charttime", "urineoutput"]
                    ],
                ),
                Dataset(
                    DatasetType.CREATININE,
                    self.validation_data_unlabelled[["stay_id", "charttime", "creat"]],
                ),
                Dataset(
                    DatasetType.DEMOGRAPHICS,
                    self.validation_data_unlabelled[["stay_id", "weight"]],
                ),
                Dataset(
                    DatasetType.RRT,
                    self.validation_data_unlabelled[
                        ["stay_id", "charttime", "rrt_status"]
                    ],
                ),
            ]
        ).process_stays()

        self.assertEqual(len(results["stay_id"].unique()), 15)
        self.assertEqual(results.shape[1], 12)
