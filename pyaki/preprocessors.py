from abc import ABC
from typing import Optional

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype

from pyaki.utils import Dataset, DatasetType, dataset_as_df, df_to_dataset


class Preprocessor(ABC):
    """Abstract base class for preprocessors."""

    def __init__(self, stay_identifier: str = "stay_id", time_identifier: str = "charttime") -> None:
        """
        Initialize a new instance of the Preprocessor class.

        Parameters:
            stay_identifier (str, optional): The column name that identifies stays or admissions in the dataset. Defaults to MIMIC standard "stay_id".
            time_identifier (str, optional): The column name that identifies the timestamp or time variable in the dataset. Defaults to MIMIC standard "charttime".
        """
        super().__init__()

        self._stay_identifier: str = stay_identifier
        self._time_identifier: str = time_identifier

    def process(self, datasets: list[Dataset]) -> list[Dataset]:
        """
        Process the given list of datasets and return the processed datasets.

        Parameters:
            datasets (list[Dataset]): The list of datasets to be processed.

        Returns:
            list[Dataset]: The processed datasets.
        """
        raise NotImplementedError()


class TimeIndexCreator(Preprocessor):
    DATASETS: list[DatasetType] = [
        DatasetType.CREATININE,
        DatasetType.URINEOUTPUT,
        DatasetType.RRT,
    ]

    def process(self, datasets: list[Dataset]) -> list[Dataset]:
        _datasets = []
        for dtype, df in datasets:
            if dtype not in self.DATASETS or self._time_identifier not in df.columns:
                _datasets.append(Dataset(dtype, df))
                continue

            if not is_datetime64_any_dtype(df[self._time_identifier]):
                df[self._time_identifier] = pd.to_datetime(df[self._time_identifier])

            _datasets.append(Dataset(dtype, df.set_index(self._time_identifier)))

        return _datasets


class UrineOutputPreProcessor(Preprocessor):
    """Preprocessor for processing the urine output dataset."""

    def __init__(
        self,
        stay_identifier: str = "stay_id",
        time_identifier: str = "charttime",
        interpolate: bool = True,
        threshold: int = 6,
    ) -> None:
        """
        Initialize a new instance of the UrineOutputPreProcessor class.

        Parameters:
            stay_identifier (str, optional): The column name that identifies stays or admissions in the dataset. Defaults to MIMIC standard "stay_id".
            time_identifier (str, optional): The column name that identifies the timestamp or time variable in the dataset. Defaults to MIMIC standard "charttime".
            interpolate (bool, optional): Flag indicating whether to perform interpolation on missing values. Defaults to True.
            threshold (int, optional): The threshold value for limiting the interpolation range. Defaults to 6.
        """
        super().__init__(stay_identifier, time_identifier)
        self._interpolate: bool = interpolate
        self._threshold: int = threshold

    @dataset_as_df(df=DatasetType.URINEOUTPUT)
    @df_to_dataset(DatasetType.URINEOUTPUT)
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process the urine output dataset by resampling, interpolating missing values, and applying threshold-based adjustments.

        Parameters:
            df (pd.DataFrame): The input urine output dataset as a pandas DataFrame.

        Returns:
            pd.DataFrame: The processed urine output dataset as a pandas DataFrame.
        """

        df = df.groupby(self._stay_identifier).resample("1H").sum()  # type: ignore
        df[df["urineoutput"] == 0] = None

        if not self._interpolate:
            return df

        mask = df["urineoutput"].isnull()
        df["urineoutput"] /= (
            (mask.cumsum() - mask.cumsum().where(~mask).ffill().fillna(0))
            .shift(1)
            .clip(upper=self._threshold)
            .add(1)
            .fillna(1)
        )
        return df.bfill(limit=self._threshold)


class CreatininePreProcessor(Preprocessor):
    """Preprocessor for processing the creatinine dataset."""

    def __init__(
        self,
        stay_identifier: str = "stay_id",
        time_identifier: str = "charttime",
        ffill: bool = True,
        threshold: int = 72,
    ) -> None:
        """
        Initialize a new instance of the CreatininePreProcessor class.

        Parameters:
            stay_identifier (str, optional): The column name that identifies stays or admissions in the dataset. Defaults to "stay_id".
            time_identifier (str, optional): The column name that identifies the timestamp or time variable in the dataset. Defaults to "charttime".
            ffill (bool, optional): Flag indicating whether to perform forward filling on missing values. Defaults to True.
            threshold (int, optional): The threshold value for limiting the forward filling range. Defaults to None.
        """
        super().__init__(stay_identifier, time_identifier)

        self._ffill: bool = ffill
        self._threshold: Optional[int] = threshold

    @dataset_as_df(df=DatasetType.CREATININE)
    @df_to_dataset(DatasetType.CREATININE)
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process the creatinine dataset by resampling and performing forward filling on missing values.

        Parameters:
            df (pd.DataFrame): The input creatinine dataset as a pandas DataFrame.

        Returns:
            pd.DataFrame: The processed creatinine dataset as a pandas DataFrame.
        """
        df = df.groupby(self._stay_identifier).resample("1H").mean()  # type: ignore
        if not self._ffill:
            return df

        df[df["creat"] == 0] = None
        return df.ffill(limit=self._threshold)


class DemographicsPreProcessor(Preprocessor):
    """Preprocessor for processing the demographics dataset."""

    @dataset_as_df(df=DatasetType.DEMOGRAPHICS)
    @df_to_dataset(DatasetType.DEMOGRAPHICS)
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process the demographics dataset by aggregating the data based on stay identifiers.

        Parameters:
            df (pd.DataFrame): The input demographics dataset as a pandas DataFrame.

        Returns:
            pd.DataFrame: The processed demographics dataset as a pandas DataFrame.
        """
        return df.groupby(self._stay_identifier).last()


class RRTPreProcessor(Preprocessor):
    """Preprocessor for processing the RRT dataset."""

    @dataset_as_df(df=DatasetType.RRT)
    @df_to_dataset(DatasetType.RRT)
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process the RRT dataset by upsampling the data and forward filling the last value. We expect the dataframe to contain a 1 for RRT in progress, and 0 for RRT not in progress.

        Parameters:
            df (pd.DataFrame): The input RRT dataset as a pandas DataFrame.

        Returns:
            pd.DataFrame: The processed RRT dataset as a pandas DataFrame.
        """
        df = df.groupby(self._stay_identifier).resample("1H").last()  # type: ignore
        return df.ffill()
