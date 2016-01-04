from flask import Flask, jsonify, render_template, request, g, redirect, url_for
import sqlite3
from contextlib import closing
from helpers import Helper

# db configuration
DATABASE = './entries.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

DOOR_1_THRESHOLD = 1
DOOR_2_THRESHOLD = 3
DOOR_3_THRESHOLD = 8
DOOR_4_THRESHOLD = 50
DOOR_5_THRESHOLD = 50

MAPPING = [DOOR_2_THRESHOLD, DOOR_3_THRESHOLD, DOOR_4_THRESHOLD, DOOR_5_THRESHOLD]

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def main():
    return render_template('homepage.html')

@app.route('/access', methods=['POST'])
def get_access_token():
    access_token = request.form.get('access_token')
    user_id = request.form.get('user_id')
    
    # FOR DEBUGGING PURPOSES, TOGGLE BETWEEN THESE TWO LINES OF CODE
    # number = Helper.calculate_num_countries(access_token=access_token, user_id=user_id)
    number = 21
    
    # save user_id, access_token, and number in db 
    insert_kv(user_id, access_token, number)
    if number >= DOOR_1_THRESHOLD:
        return render_template('1.html', user_id=user_id)
    else:
        return redirect(url_for('goodbye'))

@app.route('/goodbye')
def goodbye():
    return render_template('byebye.html')

@app.route('/<number>/marco_polo_status', methods=['POST'])
@app.route('/<number>/always_on_the_move', methods=['POST'])
@app.route('/<number>/youve_seen_a_plane', methods=['POST'])
@app.route('/<number>/good_job', methods=['POST'])
def door_access(number):
    
    user_id = request.form.get('user_id')
    user_row = get_kv(user_id)[0]
    countries = user_row[2]
    print number
    print MAPPING[int(number) - 1]
    if countries >= MAPPING[int(number) - 1]:
        title = str(int(number) + 1) + ".html"
        print title
        return render_template(title, user_id=user_id)
    else:
        return redirect(url_for('goodbye'))

def insert_kv(user_id, access, number):
    db = get_db()
    sql = """ INSERT OR REPLACE INTO entries (user_id, access_token, countries) 
              VALUES  ('{uid}','{access_token}',{countries})
              """.format(uid=user_id,access_token=access,countries=number)
    db.execute(sql)
    db.commit()

def get_kv(user_id):
    db = get_db()
    sql = """ SELECT user_id, access_token, countries from entries WHERE user_id = '{uid}'""".format(uid=user_id)
    cur = db.execute(sql)
    cur = cur.fetchall()
    return cur


if __name__ == '__main__':
    app.run(debug=True)
