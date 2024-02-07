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
        self.validation_data.drop(columns=["Unnamed: 11"], inplace=True)
        self.result_cols = [
            "urineoutput_stage",
            "abs_creatinine_stage",
            "rel_creatinine_stage",
            "rrt_stage",
            "stage",
        ]

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
        results = Analyser(
            [
                Dataset(
                    DatasetType.URINEOUTPUT,
                    self.validation_data_unlabelled[
                        ["stay_id", "charttime", "urineoutput"]
                    ].dropna(),
                ),
                Dataset(
                    DatasetType.CREATININE,
                    self.validation_data_unlabelled[
                        ["stay_id", "charttime", "creat"]
                    ].dropna(),
                ),
                Dataset(
                    DatasetType.DEMOGRAPHICS,
                    self.validation_data_unlabelled[["stay_id", "weight"]].dropna(),
                ),
                Dataset(
                    DatasetType.RRT,
                    self.validation_data_unlabelled[
                        ["stay_id", "charttime", "rrt_status"]
                    ].dropna(),
                ),
            ]
        ).process_stays()
        results.drop(columns=["stay_id"], inplace=True)
        self.assertEqual(results.shape[1], self.validation_data.shape[1])
        self.assertEqual(results.shape[0], self.validation_data.shape[0])

        results_grouped = results.groupby("stay_id").mean()
        validation_grouped = self.validation_data.groupby("stay_id").mean()

        # check if the resulting columns have the same dtype (actual results might vary slightly due to different preprocessing)
        for col in self.result_cols:
            self.assertEqual(results_grouped[col].dtype, validation_grouped[col].dtype)
