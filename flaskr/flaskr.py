# all the imports
import logging
import operator
import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

# configuration
DATABASE = 'flaskr.db'
DEBUG = True

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
# app.debug = True


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
    history = g.db.execute('SELECT * FROM entries ORDER BY id DESC').fetchall()
    entries = [dict(op1=row[1], oper=row[2], op2=row[3], res=row[4]) for row in history]
    return render_template('show_history.html', entries=entries)


@app.route('/clear_history')
def clear_history():
    g.db.execute('DELETE FROM entries;')
    g.db.commit()
    return show_history()


def _to_poly_number(number):
    n = float(number)
    if n.is_integer():
        n = int(n)
    return n

@app.route('/', methods=['GET', 'POST'])
def calculator():
    new_oper = ''
    result = ''
    if request.method == 'POST':
        op1 = request.form['op1']
        op2 = request.form['op2']
        cur_oper = request.form['cur_oper']
        new_oper = request.form['new_oper']
        try:
            operation = getattr(operator, cur_oper, operator.add)
            operand1 = _to_poly_number(op1)
            operand2 = _to_poly_number(op2)
            result = _to_poly_number(operation(operand1, operand2))
        except:
            logging.exception("Operational error")

        if result != '':
            g.db.execute("""
                INSERT INTO entries (operand1, operator, operand2, result) 
                VALUES ('%s', '%s', '%s', '%s');""" % (op1, cur_oper, op2, result)
            )
            g.db.commit()

        logging.info(operand1, cur_oper, operand2, result)

    return render_template('calculator.html', op=result, oper=new_oper)

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
    app.run(debug=True)
