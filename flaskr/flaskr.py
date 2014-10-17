# all the imports
import oper
import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/history')
def show_history():
    cur = g.db.execute('SELECT * FROM history ORDER BY id DESC')
    entries = [dict(op1=row[1], oper=row[2], op2=row[3], res=row[4]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

@app.route('/', methods=['GET', 'POST'])
def calculator():
    if request.method == 'POST':
        op1 = int(request.form['op1'])
        op2 = int(request.form['op2'])
        oper = getattr(oper, request.form['oper'], operator.add)
        result = oper(op1, op2)
        cur = g.db.execute('INSERT INTO history VALUES %s, %s, "%s", %s;' % (op1, oper, op2, result))
    else:
        if request.form['op1']:
            result = request.form['op1']
    return render_template('main.html', op1=result)

#@app.route('/add', methods=['POST'])
#def add_entry():
    #if not session.get('logged_in'):
        #abort(401)
    #g.db.execute('insert into entries (title, text) values (?, ?)',
                 #[request.form['title'], request.form['text']])
    #g.db.commit()
    #flash('New entry was successfully posted')
    #return redirect(url_for('show_entries'))

#@app.route('/login', methods=['GET', 'POST'])
#def login():
    #error = None
    #if request.method == 'POST':
        #if request.form['username'] != app.config['USERNAME']:
            #error = 'Invalid username'
        #elif request.form['password'] != app.config['PASSWORD']:
            #error = 'Invalid password'
        #else:
            #session['logged_in'] = True
            #flash('You were logged in')
            #return redirect(url_for('show_entries'))
    #return render_template('login.html', error=error)

#@app.route('/logout')
#def logout():
    #session.pop('logged_in', None)
    #flash('You were logged out')
    #return redirect(url_for('show_entries'))
    

if __name__ == '__main__':
    app.run()


