from unittest import TestCase

import pandas as pd

from pyaki.kdigo import Analyser
from pyaki.probes import Dataset, DatasetType
from tests.set_up import setup_validation_data


class TestAnalyser(TestCase):
    def setUp(self) -> None:
        self.validation_data, self.validation_data_unlabelled = setup_validation_data()
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
            index=pd.period_range(start="2023-01-01 00:00:00", end="2023-01-04 20:00:00", freq="h"),
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
        data = self.validation_data_unlabelled.copy()
        data.reset_index(inplace=True)

        results = Analyser(
            [
                Dataset(
                    DatasetType.URINEOUTPUT,
                    data[["stay_id", "charttime", "urineoutput"]].dropna(),
                ),
                Dataset(
                    DatasetType.CREATININE,
                    data[["stay_id", "charttime", "creat"]].dropna(),
                ),
                Dataset(
                    DatasetType.DEMOGRAPHICS,
                    data[["stay_id", "weight"]].dropna(),
                ),
                Dataset(
                    DatasetType.RRT,
                    data[["stay_id", "charttime", "rrt_status"]].dropna(),
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

    def test_creatinine_settings(self):
        results = Analyser(
            [
                Dataset(
                    DatasetType.URINEOUTPUT,
                    self.validation_data_unlabelled[["urineoutput"]],
                ),
                Dataset(DatasetType.CREATININE, self.validation_data_unlabelled[["creat"]]),
                Dataset(
                    DatasetType.DEMOGRAPHICS,
                    self.validation_data_unlabelled[["weight"]].groupby("stay_id").first(),
                ),
                Dataset(DatasetType.RRT, self.validation_data_unlabelled[["rrt_status"]]),
            ],
            preprocessors=[],
        ).process_stays()
        self.assertEqual(results.shape[1], self.validation_data.shape[1])
        self.assertEqual(results.shape[0], self.validation_data.shape[0])

        results_grouped = results.groupby("stay_id").mean()
        validation_grouped = self.validation_data.groupby("stay_id").mean()

        for col in self.result_cols:
            self.assertEqual(results_grouped[col].dtype, validation_grouped[col].dtype)

        for column in self.result_cols:
            print(column)
            pd.testing.assert_series_equal(
                results[column],
                self.validation_data[column],
                check_index=False,
            )
