-- Prints all cities in th database in the format
-- city_id citie_name states_name
SELECT c.`id`, c.`name`, s.`name`
       FROM `cities` AS c
       	    INNER JOIN `states` AS s
       	    ON c.`state_id` = s.`id`
       ORDER BY c.`id`;
