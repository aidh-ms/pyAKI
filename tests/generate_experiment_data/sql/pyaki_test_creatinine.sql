DROP VIEW
  IF EXISTS mimiciv_custom.pyaki_test_creatinine;

CREATE VIEW
  mimiciv_custom.pyaki_test_creatinine AS (
    SELECT
      d.stay_id,
      u.charttime,
      u.creat
    FROM
      mimiciv_custom.pyaki_test_demographics AS d
      INNER JOIN mimiciv_derived.kdigo_creatinine AS u USING (stay_id)
    ORDER BY
      stay_id,
      charttime
  );