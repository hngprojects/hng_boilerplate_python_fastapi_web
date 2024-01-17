-- Listing all the genres of the show dexter

SELECT gnr.name
       FROM tv_genres AS gnr
       INNER JOIN tv_show_genres AS tsg
       	     ON gnr.id = tsg.genre_id
       INNER JOIN tv_shows AS ts
       	     ON  ts.id = tsg.show_id
	WHERE ts.title = "Dexter"
	ORDER BY gnr.name
