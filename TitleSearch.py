import psycopg2
import sys
from dbkeys import USER_DB, PASS_DB, HOST_DB, PORT_DB, DB_NAME


def db_connection():
    try:
        connection = psycopg2.connect(user=USER_DB,
                                      password=PASS_DB,
                                      host=HOST_DB,
                                      port=PORT_DB,
                                      database=DB_NAME)
        return connection
    except Exception as error:
        print("Error occurred while connection: ", error)


def title_search(movie_title):
    connection = db_connection()
    cursor = connection.cursor()

    movie_title_frmt = movie_title.lower().replace(' ', ' OR ')

    query = """
            with y as (       
            with x as (select websearch_to_tsquery('english', '%s') q)
            select 
                movie_title, 
                imdb_score,
                actor_1_name,
                genres,
                ts_rank(to_tsvector('english', movies_raw.movie_title), q) rank,
                ts_headline(movie_title, q) 
            from movies_raw, x
                where (to_tsvector('english', movies_raw.movie_title)) @@ q
                order by rank desc, imdb_score limit 5 
            ) select movie_title, 
                imdb_score,
                actor_1_name,
                genres
            from y;
        """ % movie_title_frmt
    cursor.execute(query)

    for row in cursor:
        print(row)

    if connection:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    movie_title = 'Heroes and Money'
    title_search(movie_title)
