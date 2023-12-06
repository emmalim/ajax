import cs304dbi as dbi
from flask import flash

def get_all(conn):
    """returns tt, title, director, release, 
        and rating of all rows in movie table"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select tt, title, director as name, `release`, 
        rating as avgrating from movie
    ''')
    return curs.fetchall()


def delete_all_ratings(conn, tt):
    """deletes all ratings by user with specified uid for movie
        with specified tt"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        DELETE FROM movie_viewer_rating WHERE 
        tt = %s
        ''', [tt])
    curs.execute('''
        UPDATE movie SET rating = %s WHERE tt=%s
        ''', [None, tt])
    conn.commit()


def rate_movie(conn, urid, tt, uid, stars):
    """takes urid, tt, uid, stars and inserts data into table.
        if the urid is already in the table, then update the 
        score for that row"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO movie_viewer_rating (urid, tt, uid, score) 
        values (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        score = %s
        ''', (urid, tt, uid, stars, stars))
    conn.commit()


def calc_avg(conn, tt):
    """takes in a tt and calculates the average number of
        stars given in all ratings of the movie with specified
        tt. updates the movie.rating column with avg rating"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        UPDATE movie SET rating = (SELECT avg(score) from
        movie_viewer_rating where tt=%s) WHERE tt=%s
    ''', [tt, tt])
    conn.commit()


# for ajax --------------------------------------------------------
def get_one(conn, urid):
    '''returns urid, tt, uid, and rating of user's rating for movie'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select urid, tt, uid, and rating from movie_viewer_rating
        where urid=%s
    ''',[urid])
    return curs.fetchall()

def get_avg(conn, tt):
    '''returns average score for movie with specified tt'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select avg(score) as avg from movie_viewer_rating where
        tt=%s
    ''', [tt])
    return curs.fetchone()

def delete_one(conn, urid):
    '''deletes movie rating with given urid value'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        delete from movie_viewer_ratings where urid=%s
    ''', [urid])
    conn.commit()
