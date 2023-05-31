import numpy as np
import pandas as pd
from scipy.ndimage import uniform_filter1d


def process_stay(stay_id: int,
                 urine_output: pd.DataFrame,
                 creatinine: pd.DataFrame,
                 weight: float,
                 stay_identifier: str = 'stay_id',
                 time_identifier: str = 'charttime') -> pd.DataFrame:
    """
    Process a stay and annotate with KDIGO AKI stage

    Parameters
    ----------
    stay_id: int
        stay_identifier
    urine_output: pd.DataFrame
        DataFrame containing information about urine output
    creatinine: pd.DataFrame
        DataFrame containing information about creatinine level
    weight: float
        weight in kg of the current subject
    stay_identifier: str
        stay label in `urine_output` and `creatinine`
    time_identifier: str
        timestamp label in `urine_output` and `creatinine`

    Returns
    -------
    pd.DataFrame
        Containing the aki_stage and aki sub-stages for urine output, relative and absolute creatinine
    """
    if stay_id not in np.unique(urine_output.stay_id) or stay_id not in np.unique(creatinine.stay_id):
        raise ValueError('stay_id not found in input data')
    urine_output = refactor_timeseries(stay_id,
                                       input_ts=urine_output,
                                       stay_identifier=stay_identifier,
                                       time_identifier=time_identifier)
    creatinine = refactor_timeseries(stay_id,
                                     input_ts=creatinine,
                                     stay_identifier=stay_identifier,
                                     time_identifier=time_identifier)
    df = urine_output.join(creatinine).fillna(0)
    kdigo_uo_criterion(input_ts=df, weight=weight)
    kdigo_rel_crea_criterion(input_ts=df, baseline=.5)
    # todo: kdigo abs crea criterion
    df['aki_stage'] = np.maximum(df.kdigo_uo_criterion, df.kdigo_rel_crea_criterion)
    return df


def refactor_timeseries(stay_id: int,
                        input_ts: pd.DataFrame,
                        stay_identifier: str = 'stay_id',
                        time_identifier: str = 'charttime'):
    input_ts = input_ts[input_ts[stay_identifier] == stay_id].drop(columns=stay_identifier)
    input_ts[time_identifier] = pd.to_datetime(input_ts[time_identifier])
    input_ts = input_ts.set_index(time_identifier)
    return input_ts.resample('1H').sum()


def kdigo_uo_criterion(input_ts: pd.DataFrame,
                       weight: float,
                       mode: str = 'constant_init',
                       cval: float = 0.0) -> pd.DataFrame:
    """
    KDIGO urineoutput criterion

    Stage 1: <0.5 ml/kg/h for 6-12h
    Stage 2: <0.5 ml/kg/h for > 12h
    Stage 3: <0.3 ml/kg/h for > 24h OR Anuria for > 12h

    Parameters
    ----------
    input_ts: pd.DataFrame
        Index: Timestamp, hourly
        urineoutput: Urine output in ml per hour
    weight: flot
        Patient weight in kg
    mode: str, default = 'constant_init'
        * see https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.uniform_filter1d.html

        * constant_init:
             Initial value of input_ts is used as constant
    cval: float, default = 0.0
        constant value if mode is `constant`

    Returns
    -------
    pd.DataFrame
        Dataframe with kdigo_uo_criterion
    """
    if 'urineoutput' not in input_ts.columns:
        raise ValueError('Expected key `urineoutput` in input_ts.')
    var_name = 'kdigo_uo_criterion'
    input_ts[var_name] = [0 for _ in range(len(input_ts))]
    if mode == 'constant_init':
        mode = 'constant'
        cval = input_ts.urineoutput[0]
    for i in range(6, min(len(input_ts), 48)):
        origin = int(i/2) if i % 2 == 1 else int(i/2) - 1
        current_mean = uniform_filter1d(input_ts.urineoutput, size=i, origin=origin, mode=mode, cval=cval)
        if i < 12:
            input_ts[var_name] = np.maximum(input_ts[var_name], (current_mean/weight < .5) * 1)
            continue
        if 12 <= i < 24:
            input_ts[var_name] = np.maximum(input_ts[var_name], (current_mean/weight < .5) * 2)
            input_ts[var_name] = np.maximum(input_ts[var_name], (current_mean/weight == 0) * 3)
            continue
        if i >= 24:
            input_ts[var_name] = np.maximum(input_ts[var_name], (current_mean/weight < .3) * 3)
            input_ts[var_name] = np.maximum(input_ts[var_name], (current_mean/weight == 0) * 3)

    return input_ts


def kdigo_abs_crea_criterion():
    raise NotImplemented()


def kdigo_rel_crea_criterion(input_ts: pd.DataFrame,
                             baseline: float) -> pd.DataFrame:
    """
    KDIGO relative serum creatinine criterion

    Parameters
    ----------
    input_ts: pd.DataFrame
        Index: Timestamp, hourly
        urineoutput: Urine output in ml per hour
    baseline: float
        Baseline serum creatinine
        todo: Auto-Baseline export

    Returns
    -------
    pd.DataFrame
        Dataframe with kdigo_rel_crea_criterion
    """
    if 'creat' not in input_ts.columns:
        raise ValueError('Expected key `creat` in input_ts')
    var_name = 'kdigo_rel_crea_criterion'
    input_ts[var_name] = [0 for _ in range(len(input_ts))]
    crea_raise = input_ts.creat.to_numpy() / baseline
    input_ts[var_name] = np.maximum(input_ts[var_name], ((crea_raise > 1.5) & (crea_raise < 1.9)) * 1)
    input_ts[var_name] = np.maximum(input_ts[var_name], ((crea_raise > 2.0) & (crea_raise < 2.9)) * 2)
    input_ts[var_name] = np.maximum(input_ts[var_name], ((crea_raise > 3.0)) * 3)
    return input_ts
