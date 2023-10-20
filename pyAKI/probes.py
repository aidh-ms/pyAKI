""" This module contains the Probe abstract base class and its subclasses,
used for probing for the different KDIGO criteria."""

from abc import ABC, ABCMeta
from enum import StrEnum, auto
from typing import Optional, Dict

import pandas as pd
import numpy as np


from pyAKI.utils import dataset_as_df, df_to_dataset, approx_gte, Dataset, DatasetType


class Probe(ABC):
    """
    Abstract base class representing a data analysis probe.

    This class serves as an abstract base class (ABC) for data analysis probes.
    It declares the abstract method `probe()` that must be implemented by its subclasses.
    The `RESNAME` attribute can be overridden by subclasses to specify the name of the
    result column generated by the probe.

    Attributes:
        RESNAME (str): The name of the result column generated by the probe.

    Methods:
        probe(datasets: list[Dataset], **kwargs) -> pd.DataFrame:
            Abstract method to be implemented by subclasses.
            It performs data analysis on the provided datasets and returns a DataFrame
            with the analysis results.

    Example:
        class MyProbe(Probe):
            RESNAME = "my_result"

            def probe(self, datasets: list[Dataset], **kwargs) -> pd.DataFrame:
                # Implementation of the probe's analysis...

        my_probe = MyProbe()
        result_df = my_probe.probe(datasets=my_datasets, additional_arg=value)
    """

    RESNAME: str = ""  # name of the column that will be added to the dataframe

    def probe(self, datasets: list[Dataset], **kwargs) -> pd.DataFrame:
        """
        Abstract method to be implemented by subclasses.

        This method performs data analysis on the provided datasets and returns a DataFrame
        with the analysis results. Subclasses must override this method.

        Args:
            datasets (list[Dataset]): A list of Dataset objects containing the input data.
            **kwargs: Additional keyword arguments for the analysis.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.

        Returns:
            pd.DataFrame: The DataFrame containing the analysis results.

        """
        raise NotImplementedError()


class UrineOutputMethod(StrEnum):
    """
    Enumeration class representing different methods for urine output calculations

    Attributes:
        STRICT (str): Strict method for urine output calculations. Using this method, the urine output stage is calculated based on the maximum urine output in the past 6, 12, and 24 hours.
        MEAN (str), default: Mean method for urine output calculations.
    """

    STRICT = auto()
    MEAN = auto()


class UrineOutputProbe(Probe):
    """
    Subclass of Probe representing a probe calculating KDIGO stages according to urine output.

    This class specializes the abstract base class `Probe` to perform calculations of KDIGO stages based on urine output. Common KDIGO criteria apply.
    It overrides the `RESNAME` attribute to set the name of the result column.
    The `probe()` method performs urine output analysis on the provided DataFrame and returns a modified DataFrame
    with a column containing the appropriate KDIGO stage, according to urine output, added.

    Attributes:
        RESNAME (str): The name of the result column representing urine output stage.

    Args:
        column (str): The name of the column representing urine output in the DataFrame.
        anuria_limit (float): The anuria limit for urine output calculations.

    Example:
        probe = UrineOutputProbe(column="urineoutput", anuria_limit=0.1)
        result_df = probe.probe(df=my_dataframe, patient=patient_df)
    """

    RESNAME = "urineoutput_stage"

    def __init__(
        self,
        column: str = "urineoutput",
        anuria_limit: float = 0.1,
        method: UrineOutputMethod = UrineOutputMethod.MEAN,
    ) -> None:
        """
        Initialize the UrineOutputProbe instance.

        Args:
            column (str): The name of the column representing urine output in the DataFrame.
            anuria_limit (float): The anuria limit for urine output calculations. Defaults to 0.1ml/kg/h.
        """
        super().__init__()

        self._column: str = column
        self._anuria_limit: float = anuria_limit
        self._method: UrineOutputMethod = method

    @dataset_as_df(df=DatasetType.URINEOUTPUT, patient=DatasetType.DEMOGRAPHICS)
    @df_to_dataset(DatasetType.URINEOUTPUT)
    def probe(
        self,
        df: pd.DataFrame = None,
        patient: pd.DataFrame = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Perform urine output analysis on the provided DataFrame.

        This method calculates the KDIGO stage according to urine output based on the provided DataFrame and patient information DataFrame.
        It modifies the DataFrame by adding the urine output stage column with appropriate values based on the calculations.

        Args:
            df (pd.DataFrame): The DataFrame containing the urine output data. We expect the DataFrame to contain urine output values in ml, sampled hourly.
            patient (pd.DataFrame): The DataFrame containing patient information. Should contain the patients weight in kg.

        Returns:
            pd.DataFrame: The modified DataFrame with the urine output stage column added.
        """
        weight: pd.Series = patient["weight"]
        # fmt: off
        df = df.copy()
        df[self.RESNAME] = 0 # set all urineoutput_stage values to 0
        if self._method == UrineOutputMethod.STRICT:
            df.loc[(df.rolling(6).max()[self._column] / weight) < 0.5, self.RESNAME] = 1
            df.loc[(df.rolling(12).max()[self._column] / weight) < 0.5, self.RESNAME] = 2
            df.loc[(df.rolling(24).max()[self._column] / weight) < 0.3, self.RESNAME] = 3
            df.loc[(df.rolling(12).max()[self._column] / weight) < self._anuria_limit, self.RESNAME] = 3
        elif self._method == UrineOutputMethod.MEAN:
            df.loc[(df.rolling(6).mean()[self._column] / weight) < 0.5, self.RESNAME] = 1
            df.loc[(df.rolling(12).mean()[self._column] / weight) < 0.5, self.RESNAME] = 2
            df.loc[(df.rolling(24).mean()[self._column] / weight) < 0.3, self.RESNAME] = 3
            df.loc[(df.rolling(12).mean()[self._column] / weight) < self._anuria_limit, self.RESNAME] = 3
        else:
            raise ValueError(f"Invalid method: {self._method}")
        # fmt: on
        return df


class CreatinineBaselineMethod(StrEnum):
    """
    Enumeration class representing different methods for creatinine baseline calculations.

    This class defines the available methods for calculating creatinine values.
    It is a subclass of the `StrEnum` class, which is a string-based enumeration.
    The available methods are `MIN` and `FIRST`.

    Attributes:
        MIN: Represents the minimum method for creatinine calculations. Minimum creatinine value within the specified time window before observation is used as baseline.
        FIRST: Represents the first method for creatinine calculations. First creatinine value within the specified time window before observation is used as baseline.
        FIXED: Represents the fixed method for creatinine calculations. A fixed window (default 7 days) ist used for baseline calculation. Values from the window are used as baseline throughout the observation period.
    """

    MIN = auto()
    FIRST = auto()
    FIXED = auto()


class AbstractCreatinineProbe(Probe, metaclass=ABCMeta):
    """
    Abstract base class representing a creatinine probe.

    This class serves as an abstract base class for creatinine probes.
    It extends the `Probe` class and provides common functionality and attributes
    for creatinine probe implementations.

    Attributes:
        column (str): The name of the column containing creatinine values.
        baseline_timeframe (str): The baseline_timeframe over which creatinine values are analyzed.
        method (CreatinineBaselineMethod): The method used for creatinine baseline calculations.

    Example:
        class MyCreatinineProbe(AbstractCreCreatinineProbe):
            def __init__(self, column="creatinine", baseline_timeframe="7d", method=CreatinineBaselineMethod.MIN):
                super().__init__(column, baseline_timeframe, method)
                # Additional initialization

            def probe(self, df, **kwargs):
                # Probe implementation specific to the derived class
    """

    def __init__(
        self,
        column: str = "creat",
        baseline_timeframe: str = "7d",
        method: CreatinineBaselineMethod = CreatinineBaselineMethod.FIXED,
    ) -> None:
        super().__init__()

        self._column: str = column
        self._baseline_timeframe: str = baseline_timeframe
        self._method: CreatinineBaselineMethod = method

    def creatinine_baseline(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate the creatinine baseline values.

        This method calculates the creatinine baseline values based on the configured
        parameters and the provided DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the creatinine data.

        Returns:
            pd.Series: The calculated creatinine baseline values.

        """
        if self._method == CreatinineBaselineMethod.FIRST:
            return (
                df[df[self._column] > 0]
                .rolling(self._baseline_timeframe)
                .agg(lambda rows: rows[0])
                .resample("1h")
                .first()
                .ffill()[self._column]
            )

        if self._method == CreatinineBaselineMethod.MIN:
            return (
                df[df[self._column] > 0]
                .rolling(self._baseline_timeframe)
                .min()
                .resample("1h")
                .min()
                .ffill()[self._column]
            )

        if self._method == CreatinineBaselineMethod.FIXED:
            values = (
                df[df[self._column] > 0]
                .rolling(self._baseline_timeframe)
                .min()
                .resample("1h")
                .min()
                .ffill()[self._column]
            )
            min_value = values[
                values.index
                <= (values.index[0] + pd.Timedelta(self._baseline_timeframe))
            ].min()  # calculate min value for first 7 days
            values[
                values.index
                > (values.index[0] + pd.Timedelta(self._baseline_timeframe))
            ] = min_value  # set all values after first 7 days to min value

            return values


class AbsoluteCreatinineProbe(AbstractCreatinineProbe):
    """
    Probe class for absolute creatinine criterion, according to KDIGO criteria.

    This class represents a probe that calculates AKI stages according to absolute rises in creatinine, according to the KDIGO criteria.
    It extends the `AbstractCreCreatinineProbe` class.

    Attributes:
        RESNAME (str): The name of the resulting stage column.

    Example:
        probe = AbsoluteCreatinineProbe(column="creatinine", baseline_timeframe="7d", method=CreatinineMethod.MIN)
        df_result = probe.probe(df)
    """

    RESNAME = "abs_creatinine_stage"

    @dataset_as_df(df=DatasetType.CREATININE)
    @df_to_dataset(DatasetType.CREATININE)
    def probe(self, df: pd.DataFrame = None, **kwargs) -> pd.DataFrame:
        """
        Perform KDIGO stage calculation based on absolute creatinine elevations on the provided DataFrame.

        This method calculates the KDIGO stage based on the provided DataFrame
        and the configured baseline values. It calculates the stage according to KDIGO criteria.

        Args:
            df (pd.DataFrame): The DataFrame containing the creatinine data. It should have a column
                with the name specified in the `column` attribute of the probe.

        Returns:
            pd.DataFrame: The modified DataFrame with the absolute creatinine stage column added.
        """
        baseline_values: pd.Series = self.creatinine_baseline(df)
        df = df.copy()
        df[self.RESNAME] = 0
        df.loc[(df[self._column] - baseline_values) >= 0.3, self.RESNAME] = 1
        df.loc[df[self._column] >= 4, self.RESNAME] = 3

        df.loc[approx_gte((df[self._column] - baseline_values), 0.3), self.RESNAME] = 1
        df.loc[approx_gte(df[self._column], 4), self.RESNAME] = 3

        df.loc[df[self._column] == 0, self.RESNAME] = None
        df[self.RESNAME] = df[self.RESNAME].ffill().fillna(0)

        return df


class RelativeCreatinineProbe(AbstractCreatinineProbe):
    """
    Probe class for relative creatinine measurements.

    This class represents a probe calculates KDIGO stages based on relative creatinine elevations.

    Attributes:
        RESNAME (str): The name of the resulting stage column.

    Example:
        probe = RelativeCreatinineProbe(column="creatinine", baseline_timeframe="7d", method=CreatinineBaselineMethod.MIN)
        df_result = probe.probe(df)
    """

    RESNAME = "rel_creatinine_stage"

    @dataset_as_df(df=DatasetType.CREATININE)
    @df_to_dataset(DatasetType.CREATININE)
    def probe(self, df: pd.DataFrame = None, **kwargs) -> pd.DataFrame:
        """
        Perform calculation of relative creatinine elevations on the provided DataFrame.

        This method calculates the relative creatinine stage based on the provided DataFrame
        and the configured baseline values. It modifies the DataFrame by adding the relative
        creatinine stage column with appropriate values based on the calculations.

        Args:
            df (pd.DataFrame): The DataFrame containing the creatinine data. It should have a column
                with the name specified in the `column` attribute of the probe.

        Returns:
            pd.DataFrame: The modified DataFrame with the relative creatinine stage column added.
        """
        baseline_values: pd.Series = self.creatinine_baseline(df)

        df[self.RESNAME] = 0
        df.loc[approx_gte((df[self._column] / baseline_values), 1.5), self.RESNAME] = 1
        df.loc[approx_gte((df[self._column] / baseline_values), 2), self.RESNAME] = 2
        df.loc[approx_gte((df[self._column] / baseline_values), 3), self.RESNAME] = 3

        df.loc[df[self._column] == 0, self.RESNAME] = None
        df[self.RESNAME] = df[self.RESNAME].ffill().fillna(0)

        return df


class CRRTProbe(Probe):
    """
    Probe class for CRRT.

    This class represents a probe that calculates CRRT. It will return a KDIGO stage 3 if the patient is on CRRT at any time during the ICU stay. It will return 0 otherwise.


    Args:
        df (pd.DataFrame): The DataFrame containing the CRRT data. It should have a column with the name specified in the `column` attribute of the probe.
            It is expected that the DataFrame is indexed by patient ID and time by an hourly interval.
            If the patient is on CRRT the value should be 1, otherwise 0.
        column (str): The name of the column containing the CRRT data.

        Returns:
            pd.DataFrame: The modified DataFrame with the CRRT stage column added.
    """

    RESNAME = "crrt_stage"

    def __init__(self, column: str = "crrt_status") -> None:
        """Initialize the probe."""
        super().__init__()

        self._column: str = column

    @dataset_as_df(df=DatasetType.CRRT)
    @df_to_dataset(DatasetType.CRRT)
    def probe(
        self, df: pd.DataFrame = None, **kwargs: Optional[Dict[str, str]]
    ) -> pd.DataFrame:
        """Perform calculation of CRRT on the provided DataFrame."""
        df[self.RESNAME] = 0
        df.loc[df[self._column] == 1, self.RESNAME] = 3
        # transfer nans
        df.loc[df[self._column].isna(), self.RESNAME] = np.nan

        return df
