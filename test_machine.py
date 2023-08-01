import pyAKI.kdigo
import pandas as pd

if __name__ == "__main__":
    # Load the test data
    urine_output = pd.read_csv("tests/data/test_machine_urineoutput.csv")
    creatinine = pd.read_csv("tests/data/test_machine_creatinine.csv")
    crrt = pd.read_csv("tests/data/test_machine_crrt.csv")
    patient_data = pd.read_csv("tests/data/test_machine_weights.csv")

    print(patient_data.head())
    print(patient_data.info())
    print(urine_output.head())
    print(urine_output.info())
    print(creatinine.head())
    print(creatinine.info())
    print(crrt.head())
    print(crrt.info())

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
