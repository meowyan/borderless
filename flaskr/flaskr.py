#all the imports

import sqlite3
from contextlib import closing
from flask import Flask,request,session,g,redirect,url_for, abort, render_template,flash

#configuration
# DATABASE = 'C://Users//.nagareboshi.ritsuke//PycharmProjects//borderless//flaskr//tmp//flaskr.db'
DATABASE = '/home/jx/borderless/flaskr/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

#create our little appllcaition ;)
app = Flask(__name__)
app.config.from_object(__name__)

#Load app configuration from file
# app.config.from_envvar('FLASK_SETTINGS',silent = True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g.db = connect_db()
    db.row_factory = make_dicts
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_db (query, args=()):
    try:
        db = get_db.execute(query, args)
        db.commit()
        return True
    except:
        return False

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


## ROUTES
@app.route('/main', methods=['GET'])
def main():
    error = None
    return render_template('main.html')

@app.route('/order', methods=['GET','POST'])
def order():
    if request.method == 'POST':
        g.db.execute('insert into entries (title, text) values (?, ?)',
                     [request.form['title'], request.form['text']])
        g.db.commit()
        flash('Order was successfully posted')
        return redirect(url_for('order'))
    elif request.method == 'GET':
        return render_template('order_complete.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        #Username not correct
        the_username = request.form['username']
        password = request.form['password']
        user = query_db('select * from Customers where login_name = ?', [the_username], one=True)
        if user is None:
            error = 'Invalid Username'
        else:
            if password == user['password']:
                session['logged_in'] = True
                session ['user'] = user
                flash('You were logged in')
                return redirect(url_for('main'))
            else:
                error = 'Invalid password'
    return render_template('login.html', error=error)

@app.route('/book/<isbn>', methods=['GET'])
def book(isbn):
    book = query_db('Select * from Books where isbn = ?', [isbn], one=True)
    if book is None:
        error = 'Invalid ISBN'
        return redirect(url_for('main'))
    return render_template('individual_book.html',book=book)

@app.route('/search', methods=['GET'])
def search():
    # book = query_db('Select * from Books where isbn = ?', [isbn], one=True)
    # if book is None:
    #     error = 'Invalid ISBN'
    #     return redirect(url_for('main'))
    return render_template('search_results.html',entries=entries)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    flash('You were logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()

## RUN WITH PYTHON SHELL TO INIT DB
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
