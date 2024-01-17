-- Lists all the genres of the tvshow database

SELECT gnr.name AS 'genre', count(*) AS  'number_of_shows'
       FROM tv_genres AS gnr
       	    INNER JOIN tv_show_genres AS tsg
	    ON gnr.id = tsg.genre_id
      GROUP BY gnr.name
      ORDER BY number_of_shows DESC;
