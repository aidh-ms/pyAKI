from typing import NamedTuple
from enum import StrEnum, auto

import pandas as pd


class DatasetType(StrEnum):
    """Enumeration class representing different types of datasets."""
    URINEOUTPUT = auto()
    CREATININE = auto()
    DEMOGRAPHICS = auto()


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


def dataset_filter(func):
   """
   Decorator that filters datasets based on predefined dataset names.

    This decorator is intended to be used on methods that operate on datasets.
    It filters the datasets based on a predefined set of dataset names before
    calling the decorated function. If the `self.DATASETS` attribute is empty,
    the decorator directly calls the decorated function with the given arguments
    and returns the result. If `self.DATASETS` is not empty, the decorator filters
    the datasets based on their names and calls the decorated function on the
    remaining datasets whose names are in `self.DATASETS`. The filtered datasets
    are concatenated with the result of the function call, and the final result
    is returned.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function.

    Example:
        @dataset_filter
        def analyze_datasets(self, datasets):
            # Perform analysis operations on the datasets
            ...

        self.DATASETS = ["URINEOUTPUT", "DEMOGRAPHICS"]
        datasets = [(name, dataset) for name, dataset in all_datasets]
        analyzed_datasets = analyze_datasets(datasets)
        # analyzed_datasets will contain the analyzed datasets excluding
        # "URINEOUTPUT" and "DEMOGRAPHICS" datasets.
    """
    
    def wrapper(self, datasets: list[Dataset], *args: list, **kwargs: dict):
        if not self.DATASETS: # If DATASETS is empty, return the result of the function call
            return func(self, datasets, *args, **kwargs)

        # Filter datasets based on DATASETS
        return [
            (name, dataset) for name, dataset in datasets if name not in self.DATASETS
        ] + func( 
            self,
            [(name, dataset) for name, dataset in datasets if name in self.DATASETS],
            *args,
            **kwargs
        )

    return wrapper


def dataset_as_df(func):
    """
    Decorator that extracts a single dataset as a DataFrame.

    This decorator is intended to be used on methods that operate on datasets.
    It ensures that the decorated function is only called with a single
    dataset, represented as a list containing one `Dataset` object.
    The function extracts the name and DataFrame from the dataset list,
    and calls the decorated function on the DataFrame.
    The result is wrapped in a list along with the original name
    and returned.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function.

    Raises:
        ValueError: If the length of the dataset list is not equal to 1.

    Example:
        @dataset_as_df
        def preprocess_dataset(self, df):
            # Perform preprocessing operations on the dataset DataFrame
            ...

        datasets = [(name, dataset)]
        preprocessed_datasets = preprocess_dataset(datasets)
        # preprocessed_datasets will be [(name, preprocessed_df)]
    """

    def wrapper(self, datasets: list[Dataset], *args: list, **kwargs: dict):
        if len(datasets) != 1:
            raise ValueError()

        name, df = datasets[0]

        return [(name, func(self, df, *args, **kwargs))]

    return wrapper
