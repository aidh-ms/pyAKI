from typing import Union, List
import datetime

import pytest
import pandas as pd

from pyAKI.kdigo import kdigo_uo_criterion


class TestKDIGO:

    def setup_test_df(self,
                      desired_length: int,
                      urineoutput: Union[List, float],
                      creatinine: Union[List, float]) -> pd.DataFrame:
        if not isinstance(urineoutput, list):
            urineoutput = [urineoutput] * desired_length
        if not isinstance(creatinine, list):
            creatinine = [creatinine] * desired_length
        if len(urineoutput) != desired_length or len(creatinine) != desired_length:
            raise ValueError('Length of urine output or creatinine output does not match desired length')

        base_date = datetime.datetime.now()
        data = {'charttime': [base_date - datetime.timedelta(hours=x) for x in range(desired_length)],
                'urineoutput': urineoutput,
                'creatinine': creatinine}
        df = pd.DataFrame(data=data)
        df['charttime'] = pd.to_datetime(df['charttime'])
        df = df.set_index(df['charttime'])
        return df


    def test_kdigo_uo_criterion_all_true(self):
        df = self.setup_test_df(desired_length=50, urineoutput=70, creatinine=.5)
        df = kdigo_uo_criterion(input_ts=df, weight=70)
        assert((df.kdigo_uo_criterion == 0).all())

    def test_kdigo_uo_criterion_all_stage_three(self):
        # Output of 20 with weight of 70 => 0.28 ml/kg/h => STAGE 3 for all TS
        df = self.setup_test_df(desired_length=50, urineoutput=20, creatinine=.5)
        df = kdigo_uo_criterion(input_ts=df, weight=70)
        assert((df.kdigo_uo_criterion == 3).all())

    def test_kdigo_uo_criterion_all_stage_two(self):
        # Output of 20 with weight of 70 => 0.486 ml/kg/h => STAGE 2 for all TS
        df = self.setup_test_df(desired_length=50, urineoutput=30, creatinine=.5)
        df = kdigo_uo_criterion(input_ts=df, weight=70)
        assert((df.kdigo_uo_criterion == 2).to_numpy().all())

    def test_kdigo_uo_criterion_stage_one(self):
        df = self.setup_test_df(desired_length=50, urineoutput=[24]*5+[70]*45, creatinine=.5)
        df = kdigo_uo_criterion(input_ts=df, weight=70, mode='constant', cval=70)
        assert((df.kdigo_uo_criterion == 1).sum() == 2)
        assert((df.kdigo_uo_criterion == 0).sum() == 48)

    # todo: crea tests
