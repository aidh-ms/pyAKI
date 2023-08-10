DROP VIEW IF EXISTS mimiciv_custom.pyaki_test_urineoutput;
CREATE VIEW mimiciv_custom.pyaki_test_urineoutput AS (
SELECT
  d.stay_id,
  u.charttime,
  u.urineoutput
FROM
  mimiciv_custom.pyaki_test_demographics AS d
INNER JOIN mimiciv_derived.urine_output AS u USING(stay_id)
ORDER BY stay_id, charttime);