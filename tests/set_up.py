import pandas as pd


def setup_validation_data():
    validation_data = pd.read_csv("test/data/validation_data.csv")
    # coerce stay_id to int
    validation_data["stay_id"] = validation_data["stay_id"].astype(int)
    # convert charttime to datetime
    validation_data["charttime"] = pd.to_datetime(validation_data["charttime"])
    validation_data = validation_data.set_index(["stay_id", "charttime"])
    # drop stages
    validation_data_unlabelled = validation_data.drop(
        columns=[col for col in validation_data.columns if col.endswith("_stage")]
    )

    return validation_data, validation_data_unlabelled
