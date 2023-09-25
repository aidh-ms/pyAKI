DROP VIEW
  IF EXISTS mimiciv_custom.pyaki_test_crrt;

CREATE VIEW
  mimiciv_custom.pyaki_test_crrt AS (
    SELECT
      d.stay_id,
      MAX(c.charttime) as charttime,
      MAX(c.dialysis_present) as dialysis_present
    FROM
      mimiciv_custom.pyaki_test_demographics AS d
      INNER JOIN mimiciv_derived.rrt AS c USING (stay_id)
    GROUP BY
      stay_id,
      charttime
    ORDER BY
      stay_id,
      charttime
  );