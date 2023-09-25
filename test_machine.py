import pyAKI.kdigo
import pandas as pd

if __name__ == "__main__":
    # Load the test data
    urine_output = pd.read_csv("tests/data/test_machine_urineoutput.csv")
    creatinine = pd.read_csv("tests/data/test_machine_creatinine.csv")
    crrt = pd.read_csv("tests/data/test_machine_crrt.csv")
    patient_data = pd.read_csv("tests/data/test_machine_weights.csv")

    ana = pyAKI.kdigo.Analyser(
        [
            pyAKI.utils.Dataset(pyAKI.utils.DatasetType.URINEOUTPUT, urine_output),
            pyAKI.utils.Dataset(pyAKI.utils.DatasetType.CREATININE, creatinine),
            pyAKI.utils.Dataset(pyAKI.utils.DatasetType.DEMOGRAPHICS, patient_data),
            pyAKI.utils.Dataset(pyAKI.utils.DatasetType.CRRT, crrt),
        ]
    )
    ana.process_stays().to_csv("tests/data/test_machine_aki.csv")
    ana.process_stays().to_excel("tests/data/test_machine_aki.xlsx")
