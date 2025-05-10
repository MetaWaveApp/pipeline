import json
import pymysql 
import os

base_path = os.path.dirname(os.path.abspath(__file__))
file_dtbs = os.path.join(base_path, 'database.json')
file_topg = os.path.join(base_path, "top_games_views.json")

def save_in_database(datetime_value):

    with open(file_dtbs, 'r') as f:
        database_values = json.load(f)

    conn = pymysql.connect(
        host=database_values['host'],
        user=database_values['user'],
        password=database_values['password'],
        database=database_values['database']
    )

    with open(file_topg, 'r') as fv:
        
        objviews = json.load(fv)

        gamelist = []
        viewslist = []

        for obj in objviews:
            gamelist.append((
                int(obj['id']),
                obj['name'],
                obj['box_art_url'],
                0 if obj['igdb_id'] == "" else int(obj['igdb_id']),
                datetime_value
            ))
            viewslist.append((
                int(obj['id']),
                int(obj['totalViews']),
                datetime_value
            ))

    with conn.cursor() as cursor:

        cursor.executemany("""
            INSERT IGNORE INTO game (id_twitch, name, box_art_url, igdb_id, create_at)
            VALUES (%s, %s, %s, %s, %s)
        """, gamelist)

        cursor.executemany("""
            INSERT INTO views (id_twitch, views, create_at)
            VALUES (%s, %s, %s)
        """, viewslist)

    conn.commit()
    conn.close()
