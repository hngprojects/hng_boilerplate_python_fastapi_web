-- Lists all shows and all genres linked to that show

SELECT ts.title, gnr.name
       FROM tv_genres AS gnr
       RIGHT JOIN tv_show_genres AS tsg
       	     ON gnr.id = tsg.genre_id
	RIGHT JOIN tv_shows AS ts
	     ON tsg.show_id = ts.id
	ORDER BY ts.title, gnr.name;
