DROP VIEW
  IF EXISTS mimiciv_custom.pyaki_test_weight;

CREATE VIEW
  mimiciv_custom.pyaki_test_weight AS (
    SELECT
      d.stay_id,
      w.weight
    FROM
      mimiciv_custom.pyaki_test_demographics AS d
      INNER JOIN mimiciv_derived.first_day_weight AS w USING (stay_id)
    ORDER BY
      stay_id
  );