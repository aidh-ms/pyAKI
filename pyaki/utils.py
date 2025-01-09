import logging
from enum import StrEnum, auto
from functools import wraps
from typing import Any, Callable, NamedTuple, cast

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class DatasetType(StrEnum):
    """Enumeration class representing different types of datasets."""

    URINEOUTPUT = auto()
    CREATININE = auto()
    DEMOGRAPHICS = auto()
    RRT = auto()


class Dataset(NamedTuple):
    """
    Named tuple representing a dataset.

    This class represents a dataset consisting of a dataset type and a DataFrame.
    It is defined as a named tuple, which is an immutable data structure with
    named fields. The `dataset_type` field is of type `DatasetType` and represents
    the type of the dataset. The `df` field is of type `pd.DataFrame` and represents
    the actual data stored in a pandas DataFrame object.

    Attributes:
        dataset_type (DatasetType): The type of the dataset.
        df (pd.DataFrame): The DataFrame object containing the dataset.

    Example:
        dataset = Dataset(dataset_type=DatasetType.URINEOUTPUT, df=my_dataframe)
    """

    dataset_type: DatasetType
    df: pd.DataFrame


def dataset_as_df(**mapping: DatasetType) -> Callable:
    """
    Decorator factory for methods that process datasets with dataframes.

    This decorator is intended to be used with methods in a class that handle datasets
    consisting of dataframes. It allows you to specify a mapping of dataset types to
    corresponding dataframe names. The decorator then replaces the dataframes of the
    specified types with the results of the decorated method.

    Args:
        **mapping (dict[str, DatasetType]): A mapping of dataset type names to their
            corresponding `DatasetType`. Dataset types not found in this mapping will
            be ignored.

    Returns:
        decorator: A decorator that can be applied to methods in a class. The decorated
            method is expected to accept a list of `Dataset` objects and optional
            additional arguments and keyword arguments.

    Example:
        Suppose you have a method `process_data` that takes a list of `Dataset` objects
        and a `mapping` as specified in the decorator:

        @dataset_as_df(data=DatasetType.DATA, labels=DatasetType.LABELS)
        def process_data(self, data: pd.DataFrame, labels: pd.DataFrame):
            # Your data processing logic here
            return processed_data, labels

        When you call `process_data` with a list of `Dataset` objects containing data
        and labels, the decorator will automatically replace the dataframes based on
        the mapping and pass them to the method:

        processed_datasets = my_instance.process_data(datasets)
    """
    # swap keys and values in the mapping
    in_mapping: dict[DatasetType, str] = {}
    for k, v in mapping.items():
        in_mapping[cast(DatasetType, v)] = k

    # in_mapping: Dict[DatasetType, str] = {v: k for k, v in mapping.items()}

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self: Any, datasets: list[Dataset], *args: Any, **kwargs: Any) -> list[Dataset]:
            # map the dataset types to corresponding DataFrames
            _mapping: dict[str, pd.DataFrame] = {
                in_mapping[dtype]: df for dtype, df in datasets if dtype in in_mapping.keys()
            }
            # check if all datasets are mapped, otherwise return the original datasets
            if len(in_mapping) != len(_mapping):
                logger.warning(
                    "Skip %s because one or more datasets are missing to probe",
                    self.__class__.__name__,
                )
                return datasets

            # call the wrapped function with the converted DataFrames
            _dtype, _df = func(self, *args, **_mapping, **kwargs)

            # return the updated datasets
            return [Dataset(dtype, _df if dtype == _dtype else df) for dtype, df in datasets]

        return wrapper

    return decorator


def df_to_dataset(dtype: DatasetType) -> Callable:
    """
    Decorator that converts a DataFrame into a dataset with the specified type.

    This decorator is intended to be used with a method that returns a DataFrame.
    It wraps the method and converts the returned DataFrame into a dataset object
    with the specified type. The converted dataset is then returned.

    Args:
        dtype: The DatasetType enum value representing the type of the dataset.

    Returns:
        A decorated function that takes the original arguments, performs the wrapped
        function, converts the returned DataFrame into a Dataset object with the
        specified type, and returns the converted dataset.

    Example:
        @df_to_dataset(DatasetType.URINEOUTPUT)
        def process_dataframe(self, *args: list, **kwargs: dict) -> pd.DataFrame:
            # Process the DataFrame
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Dataset:
            return Dataset(dtype, func(self, *args, **kwargs))

        return wrapper

    return decorator


def approx_gte(x: pd.Series, y: pd.Series | float) -> bool | np.ndarray:
    return np.logical_or(np.asarray(x >= y), np.isclose(x, y))
