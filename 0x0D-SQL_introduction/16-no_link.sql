-- List all the records of second_table except Null entries

SELECT score, name FROM second_table
WHERE name IS NOT NULL
ORDER BY score DESC
