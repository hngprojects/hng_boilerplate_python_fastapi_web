-- Lists the number of records with the same score in the second_table

SELECT score, COUNT(*)
AS number
FROM second_table
GROUP BY score
ORDER BY number DESC
