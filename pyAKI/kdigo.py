import pandas as pd

from probes import (
    Probe,
    UrineOutputProbe,
    AbsoluteCreatinineProbe,
    RelativeCreatinineProbe,
)
from preprocessors import (
    Preprocessor,
    UrineOutputPreProcessor,
    CreatininePreProcessor,
    DemographicsPreProcessor,
)
from utils import Dataset, DatasetType


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
        probes: list[Probe] | None = None,
        preprocessors: list[Preprocessor] | None = None,
        stay_identifier: str = "stay_id",
        time_identifier: str = "charttime",
    ) -> None:
        """
        Initialize the Analyser instance.

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
        """
        if probes is None:
            probes = [
                UrineOutputProbe(),
                AbsoluteCreatinineProbe(),
                RelativeCreatinineProbe(),
            ]
        if preprocessors is None:
            preprocessors = [
                UrineOutputPreProcessor(
                    stay_identifier=stay_identifier, time_identifier=time_identifier
                ),
                CreatininePreProcessor(
                    stay_identifier=stay_identifier, time_identifier=time_identifier
                ),
                DemographicsPreProcessor(stay_identifier=stay_identifier),
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

        This method processes all stays in the input data by applying the configured probes and preprocessors.
        The analysis results for all stays are concatenated and returned as a single DataFrame.

        Returns:
            pd.DataFrame: The analysis results for all stays.
        """
        pass  # TODO: #15 Implement process_stays method

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
        data = [(name, data.loc[stay_id]) for name, data in self._data]

        for probe in self._probes:
            data: pd.DataFrame = probe.probe(data)

        (_, df) = data[0]
        for _, _df in data[1:]:
            if isinstance(_df, pd.Series):
                _df = pd.DataFrame([_df], index=df.index)
            df = df.merge(_df, how="outer", left_index=True, right_index=True)

        df["stage"] = df.filter(like="stage").max(axis=1)
        return df
