# Citing

If you are a researcher and use this project as part of your research, please feel free to cite our publication.

## Paper

Our paper has been published in [PLOS One](https://doi.org/10.1371/journal.pone.0315325). You can use the following Bibtex to cite it.

```bibtex
@article{10.1371/journal.pone.0315325,
    doi = {10.1371/journal.pone.0315325},
    author = {Porschen, Christian AND Ernsting, Jan AND Brauckmann, Paul AND Weiss, Raphael AND Würdemann, Till AND Booke, Hendrik AND Amini, Wida AND Maidowski, Ludwig AND Risse, Benjamin AND Hahn, Tim AND von Groote, Thilo},
    journal = {PLOS ONE},
    publisher = {Public Library of Science},
    title = {pyAKI—An open source solution to automated acute kidney injury classification},
    year = {2025},
    month = {01},
    volume = {20},
    url = {https://doi.org/10.1371/journal.pone.0315325},
    pages = {1-14},
    abstract = {Objective Acute kidney injury (AKI) is a frequent complication in critically ill patients, affecting up to 50% of patients in the intensive care units. The lack of standardized and open-source tools for applying the Kidney Disease Improving Global Outcomes (KDIGO) criteria to time series, requires researchers to implement classification algorithms of their own which is resource intensive and might impact study quality by introducing different interpretations of edge cases. This project introduces pyAKI, an open-source pipeline addressing this gap by providing a comprehensive solution for consistent KDIGO criteria implementation.   Materials and methods The pyAKI pipeline was developed and validated using a subset of the Medical Information Mart for Intensive Care (MIMIC)-IV database, a commonly used database in critical care research. We constructed a standardized data model in order to ensure reproducibility. PyAKI implements the Kidney Disease: Improving Global Outcomes (KDIGO) guideline on AKI diagnosis. After implementation of the diagnostic algorithm, using both serum creatinine and urinary output data, pyAKI was tested on a subset of patients and diagnostic accuracy was compared in a comparative analysis against annotations by physicians.   Results Validation against expert annotations demonstrated pyAKI’s robust performance in implementing KDIGO criteria. Comparative analysis revealed its ability to surpass the quality of human labels with an accuracy of 1.0 in all categories.   Discussion The pyAKI pipeline is the first open-source solution for implementing KDIGO criteria in time series data. It provides a standardized data model and a comprehensive solution for consistent AKI classification in research applications for clinicians and data scientists working with AKI data. The pipeline’s high accuracy make it a valuable tool for clinical research and decision support systems.   Conclusion This work introduces pyAKI as an open-source solution for implementing the KDIGO criteria for AKI diagnosis using time series data with high accuracy and performance.},
    number = {1},
}
```

## Preprint

Our preprint is available on [Arxiv](https://arxiv.org/abs/2401.12930).

```bibtex
@misc{porschen2024pyakiopensource,
      title={pyAKI -- An Open Source Solution to Automated KDIGO classification},
      author={Christian Porschen and Jan Ernsting and Paul Brauckmann and Raphael Weiss and Till Würdemann and Hendrik Booke and Wida Amini and Ludwig Maidowski and Benjamin Risse and Tim Hahn and Thilo von Groote},
      year={2024},
      eprint={2401.12930},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2401.12930},
}
```
