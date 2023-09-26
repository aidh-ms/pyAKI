import pyAKI.kdigo
import pandas as pd

if __name__ == "__main__":
    # Load the test data
    data = pd.read_excel("tests/experiment/data/test_aki_combined_prep.xlsx")
    data["stay_id"] = data["stay_id"].ffill()
    data.set_index(["stay_id", "charttime"], inplace=True)

    urine_output = data.drop(columns=["creat", "weight", "crrt_status"]).reset_index()
    creatinine = data.drop(
        columns=["urineoutput", "weight", "crrt_status"]
    ).reset_index()
    weight = data.drop(columns=["urineoutput", "creat", "crrt_status"]).reset_index()
    crrt = data.drop(columns=["urineoutput", "creat", "weight"]).reset_index()
    # prep weights
    weight = weight.drop_duplicates(subset=["weight"], keep="first").reset_index()

    ana = pyAKI.kdigo.Analyser(
        [
            pyAKI.utils.Dataset(pyAKI.utils.DatasetType.URINEOUTPUT, urine_output),
            pyAKI.utils.Dataset(pyAKI.utils.DatasetType.CREATININE, creatinine),
            pyAKI.utils.Dataset(pyAKI.utils.DatasetType.DEMOGRAPHICS, weight),
            pyAKI.utils.Dataset(pyAKI.utils.DatasetType.CRRT, crrt),
        ]
    )
    ana.process_stays().to_csv("tests/experiment/data/test_machine_aki_second.csv")
    ana.process_stays().to_excel("tests/experiment/data/test_machine_aki_second.xlsx")
