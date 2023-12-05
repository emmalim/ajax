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
    return render_template("rate-movies-list-sp22.html", title="Main Page", uid=uid, movies=all_movies)


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
