from typing import Optional

import pandas as pd

from pyAKI.probes import (
    Probe,
    UrineOutputProbe,
    AbsoluteCreatinineProbe,
    RelativeCreatinineProbe,
    RRTProbe,
)
from pyAKI.preprocessors import (
    Preprocessor,
    TimeIndexCreator,
    UrineOutputPreProcessor,
    CreatininePreProcessor,
    DemographicsPreProcessor,
    RRTPreProcessor,
)

from pyAKI.utils import Dataset


class Analyser:
    """
    Class for data analysis using probes and preprocessors.

    This class provides functionality for analyzing data using a collection of probes and preprocessors.
    It processes the input data through the specified preprocessors and applies the probes to perform
    the analysis. The analysis results are returned as a DataFrame.

    Args:
        data (list[Dataset]): A list of Dataset objects containing the input data.
        probes (list[Probe], optional): A list of Probe objects representing the analysis probes to apply.
            If not provided, default probes including UrineOutputProbe, AbsoluteCreatinineProbe, and
            RelativeCreatinineProbe will be used.
        preprocessors (list[Preprocessor], optional): A list of Preprocessor objects representing the
            preprocessors to apply on the input data. If not provided, default preprocessors including
            UrineOutputPreProcessor, CreatininePreProcessor, and DemographicsPreProcessor will be used.
        stay_identifier (str, optional): The column name in the input data representing the stay identifier.
            Defaults to "stay_id".
        time_identifier (str, optional): The column name in the input data representing the time identifier.
            Defaults to "charttime".

    Example:
        # Instantiate the Analyser class with custom data, probes, and preprocessors
        analyser = Analyser(data=my_datasets, probes=[MyProbe()], preprocessors=[MyPreprocessor()])

        # Process stays and obtain the analysis results
        result_df = analyser.process_stays()
    """

    def __init__(
        self,
        data: list[Dataset],
        probes: Optional[list[Probe]] = None,
        preprocessors: Optional[list[Preprocessor]] = None,
        stay_identifier: str = "stay_id",
        time_identifier: str = "charttime",
    ) -> None:
        """
        Initialize the Analyser instance.
        """
        if probes is None:  # apply default probes if not provided
            probes = [
                UrineOutputProbe(),
                AbsoluteCreatinineProbe(),
                RelativeCreatinineProbe(),
                RRTProbe(),
            ]
        if preprocessors is None:  # apply default preprocessors if not provided
            preprocessors = [
                TimeIndexCreator(
                    stay_identifier=stay_identifier, time_identifier=time_identifier
                ),
                UrineOutputPreProcessor(
                    stay_identifier=stay_identifier, time_identifier=time_identifier
                ),
                CreatininePreProcessor(
                    stay_identifier=stay_identifier, time_identifier=time_identifier
                ),
                DemographicsPreProcessor(stay_identifier=stay_identifier),
                RRTPreProcessor(
                    stay_identifier=stay_identifier, time_identifier=time_identifier
                ),
            ]
        # apply preprocessors to the input data
        for preprocessor in preprocessors:
            data = preprocessor.process(data)

        self._data: list[Dataset] = data
        self._probes: list[Probe] = probes
        self._stay_identifier: str = stay_identifier

    def process_stays(self) -> pd.DataFrame:
        """
        Process all stays in the input data.

        This method processes all stays in the input data by applying the configured probes.
        The analysis results for all stays are concatenated and returned as a single DataFrame.

        Returns:
            pd.DataFrame: The analysis results for all stays.
        """
        (_, df), *datasets = self._data
        stay_ids: pd.Index = df.index.get_level_values("stay_id").unique()
        for _, df in datasets:
            stay_ids.join(df.index.get_level_values("stay_id").unique())

        data: pd.DataFrame = self.process_stay(stay_ids.values[0])
        for stay_id in stay_ids.values[1:]:
            data = pd.concat([data, self.process_stay(stay_id)])
        # data = data.drop(columns=["stay_id"])  # remove additional stay_id column
        return data

    def process_stay(self, stay_id: str) -> pd.DataFrame:
        """
        Process a specific stay in the input data by patient identificator.

        This method processes a specific stay in the input data by applying the configured probes and preprocessors.
        The analysis results for the stay are returned as a DataFrame.

        Args:
            stay_id (str): The identifier of the stay to process.

        Returns:
            pd.DataFrame: The analysis results for the specific stay.
        """

        data_sets = [(name, data.loc[stay_id]) for name, data in self._data]

        for probe in self._probes:
            data: Dataset = probe.probe(data_sets)

        (_, df), *datasets = data
        for _, _df in datasets:
            if isinstance(_df, pd.Series):
                _df = pd.DataFrame([_df], index=df.index)
            df: pd.DataFrame = df.merge(
                _df, how="outer", left_index=True, right_index=True
            )

        df["stage"] = df.filter(like="stage").max(axis=1)
        return df.set_index([pd.Index([stay_id] * len(df), name="stay_id"), df.index])
