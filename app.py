from flask import (
    Flask,
    render_template,
    make_response,
    url_for,
    request,
    redirect,
    flash,
    session,
    send_from_directory,
    jsonify,
)
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB limit

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi

# import cs304dbi_sqlite3 as dbi

import requests
import random
import queries as queries

app.secret_key = "your secret here"
# replace that with a random key
app.secret_key = "".join(
    [
        random.choice(
            ("ABCDEFGHIJKLMNOPQRSTUVXYZ" + "abcdefghijklmnopqrstuvxyz" + "0123456789")
        )
        for i in range(20)
    ]
)

# This gets us better error messages for certain common request errors
app.config["TRAP_BAD_REQUEST_ERRORS"] = True


@app.route("/", methods=["GET"])
def index():
    '''renders the rate-movies-list-sp22 html file'''
    #return render_template("movies-base.html", title="Main Page")

    conn = dbi.connect()
    all_movies = queries.get_all(conn)

    uid = session.get('uid', None)
    
    #print(all_movies)
    return render_template("rate-movies-list-sp22.html", 
        title="Main Page", uid=uid, movies=all_movies)


@app.route("/set-UID/", methods=["POST"])
def set_UID():
    '''logs the user in'''

    uid = request.form.get('uid')

    if not uid:
        flash("Enter a valid uid")


    session['uid'] = uid
    print("uid====" + str(uid))
    print("session's uid====" + str(session['uid']))
    return redirect(url_for("index"))


@app.route("/rate-one-movie/", methods=["POST"])
def rate_one_movie():
    if "uid" not in session:
        flash("You must be logged in to rate a movie.")
        return redirect(url_for("index"))

    tt = request.form.get('tt')
    stars = request.form.get('stars')
    uid = session.get('uid')
    urid = str(tt) + str(uid)
    print("URID====" + urid)

    conn = dbi.connect()
    queries.rate_movie(conn, urid, tt, uid, stars)
    queries.calc_avg(conn, tt)
    flash(f"User {uid}'s rating for movie TT={tt} updated successfully.")
    return redirect(url_for("index"))


@app.route("/delete-all-ratings/<int:tt>", methods=["POST"])
def delete_all_ratings(tt):
    """deletes all ratings for the given movie TT"""
    if "uid" not in session:
        flash("You must be logged in to delete ratings.")
        return redirect(url_for("index"))

    conn = dbi.connect()

    queries.delete_all_ratings(conn, tt)

    flash(f"All ratings for movie TT={tt} deleted successfully.")
    return redirect(url_for('index'))

# ----------------------------------------------------------------------------
# ---- ajax routes -----------------------------------------------------------
# ----------------------------------------------------------------------------

@app.route("/set-UID-ajax/", methods=["POST"])
def set_UID_ajax():
    """Ajax-style login route that returns jsonified dictionary
        with key uid and the user's uid as the value"""
    to_uid = request.form.get('uid')

    if not to_uid:
        return jsonify({"error": "Enter a valid uid"})

    print("ajax-login uid====" + str(to_uid))
    session['uid'] = to_uid
    
    return jsonify({'error': False})


@app.route("/rating/", methods=["POST"])
def rate_movie():
    """Route to post a new rating for a movie that returns
        a JSON dict that has the new average rating of this
        movie"""
    if "uid" not in session:
        return jsonify({"error": "You must be logged in to rate a movie."})

    tt = request.form.get('tt')
    stars = request.form.get('stars')
    uid = session.get('uid')
    urid = str(tt) + str(uid)

    conn = dbi.connect()
    queries.rate_movie(conn, urid, tt, uid, stars)
    queries.calc_avg(conn, tt)

    avg = float(queries.get_avg(conn,tt)['avg'])

    return jsonify({'tt': tt, 'stars': stars, 'avg': avg}) 


@app.route("/rating/<tt>", methods=["GET", "PUT", "DELETE"])
def ajax_rating(tt):
    """Returns a JSON dictionary that has the current
        average rating for the movie with the specified tt"""
    if "uid" not in session:
        return jsonify({"error": "You must be logged in to rate a movie."})
    
    conn = dbi.connect()
    uid = session.get('uid')
    stars = request.form.get('stars')
    urid = str(tt) + str(uid)
    print("URID=====" + str(urid))
    print(queries.get_avg(conn,tt))

    if request.method == "GET":
        # Returns a JSON dictionary that has the current average rating
        # for the movie with the specified tt
        queries.calc_avg(conn, tt)
        avg = float(queries.get_avg(conn, tt)['avg'])
        print("GET === " + str(avg))
        return jsonify({"tt": tt, "avg": avg })

    elif request.method == "PUT":
        # replaces this user's rating of this movie and  
        # returns the usual JSON dict
        prev = queries.get_one(conn, urid)
        if 'urid' not in prev:
            return jsonify({"error": 'You have not rated this movie yet'})

        queries.rate_movie(conn, urid, tt, uid, stars)
        queries.calc_avg(conn, tt)
        
        print(queries.get_avg(conn,tt))
        avg = float(queries.get_avg(conn,tt)['avg'])
        print("PUT ===== " + str(avg))


        return jsonify({'tt': tt, 'stars': stars, 'avg': avg}) 
 
    elif request.method == "DELETE":
        # deletes this user's rating of this movie and 
        # returns usual JSON dict
        queries.delete_one(conn, urid)
        avg = float(queries.get_avg(conn,tt)['avg'])
        print("DELETE === " + str(avg))
        return jsonify({"tt": tt, "avg": avg })



if __name__ == "__main__":
    import sys, os

    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert port > 1024
    else:
        port = os.getuid()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use = "el110_db"
    print("will connect to {}".format(db_to_use))
    dbi.conf(db_to_use)
    app.debug = True
    app.run("0.0.0.0", port)
