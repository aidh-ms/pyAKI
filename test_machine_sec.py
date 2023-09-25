import pyAKI.kdigo
import pandas as pd

if __name__ == "__main__":
    # Load the test data
    data = pd.read_excel("test_aki_combined_prep.xlsx")

    urine_output = data["urineoutput"]
    creatinine = data["creat"]
    weight = data["weight"]
    crrt = data["crrt_status"]
    # prep weights
    weight = weight.drop_duplicates(subset=["weight"], keep="first")

    ana = pyAKI.kdigo.Analyser(
        [
            pyAKI.utils.Dataset(pyAKI.utils.DatasetType.URINEOUTPUT, urine_output),
            pyAKI.utils.Dataset(pyAKI.utils.DatasetType.CREATININE, creatinine),
            pyAKI.utils.Dataset(pyAKI.utils.DatasetType.DEMOGRAPHICS, weight),
            pyAKI.utils.Dataset(pyAKI.utils.DatasetType.CRRT, crrt),
        ]
    )
    ana.process_stays().to_csv("tests/data/test_machine_aki_second.csv")
    ana.process_stays().to_excel("tests/data/test_machine_aki_second.xlsx")
