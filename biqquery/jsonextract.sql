CREATE TABLE dataset_name.table_name (
    id INT64,
    data STRING
);

INSERT INTO dataset_name.table_name (id, data)
VALUES
    (1, '[{"file1": "date1"}, {"file2": "date2"}, {"file3": "date3"}]'),
    (2, '[{"fileA": "dateA"}, {"fileB": "dateB"}, {"fileC": "dateC"}]');


WITH parsed_data AS (
  SELECT
    id,
    JSON_EXTRACT_ARRAY(data) AS file_data
  FROM
    dataset_name.table_name
  WHERE id = 1  
),
extracted_keys_values AS (
  SELECT
    id,
    JSON_QUERY(element, '$') AS key_value_pair
  FROM
    parsed_data,
    UNNEST(file_data) AS element
),

split_keys_values AS (
  SELECT
    id,
    REGEXP_EXTRACT(key_value_pair, r'"([^"]+)":') AS key,
    REGEXP_EXTRACT(key_value_pair, r':\s*"([^"]+)"') AS value
  FROM
    extracted_keys_values
)

SELECT * FROM split_keys_values;
