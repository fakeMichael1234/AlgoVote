import os
import sqlite3
from datetime import datetime
from flask import Flask, g, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'algovote.db')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '')
SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.executescript(f.read())
    db.commit()


def migrate_db():
    # ensure votes table has poll_id and username columns for new user-tracking
    db = get_db()
    cur = db.execute("PRAGMA table_info('votes')")
    rows = cur.fetchall()
    cur.close()
    # rows may be sqlite3.Row or tuples; column name is at index 1 for tuples
    cols = []
    for r in rows:
        try:
            name = r['name']
        except Exception:
            name = r[1]
        cols.append(name)

    # Add missing columns, ignore duplicate column errors
    if 'poll_id' not in cols:
        try:
            db.execute('ALTER TABLE votes ADD COLUMN poll_id INTEGER')
        except sqlite3.OperationalError:
            pass
    if 'username' not in cols:
        try:
            db.execute('ALTER TABLE votes ADD COLUMN username TEXT')
        except sqlite3.OperationalError:
            pass
    db.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid


@app.route('/')
def index():
    poll = query_db('SELECT * FROM polls WHERE active = 1 ORDER BY created_at DESC', (), one=True)
    return render_template('index.html', poll=poll)


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or url_for('index')
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if not username:
            flash('Please enter a username.')
            return redirect(url_for('login', next=next_url))
        session['username'] = username
        flash(f'Logged in as {username}')
        return redirect(next_url)
    return render_template('login.html', next=next_url)


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))


@app.route('/vote/<int:poll_id>')
def vote_page(poll_id):
    poll = query_db('SELECT * FROM polls WHERE id = ? AND active = 1', (poll_id,), one=True)
    if not poll:
        flash('Poll not found or not active.')
        return redirect(url_for('index'))
    # require username in session
    if not session.get('username'):
        return redirect(url_for('login', next=url_for('vote_page', poll_id=poll_id)))
    options = query_db('SELECT * FROM options WHERE poll_id = ?', (poll_id,))
    return render_template('vote.html', poll=poll, options=options)


@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    option_id = request.form.get('option')
    poll_id = request.form.get('poll_id')
    if not option_id or not poll_id:
        flash('Invalid submission.')
        return redirect(url_for('index'))
    opt = query_db('SELECT * FROM options WHERE id = ? AND poll_id = ?', (option_id, poll_id), one=True)
    poll = query_db('SELECT * FROM polls WHERE id = ? AND active = 1', (poll_id,), one=True)
    if not opt or not poll:
        flash('Invalid option or poll closed.')
        return redirect(url_for('index'))

    username = session.get('username')
    if not username:
        flash('Please provide a username before voting.')
        return redirect(url_for('login', next=url_for('vote_page', poll_id=poll_id)))

    # prevent same username voting more than once in same poll
    existing = query_db('SELECT v.id FROM votes v JOIN options o ON v.option_id = o.id WHERE o.poll_id = ? AND v.username = ?', (poll_id, username), one=True)
    if existing:
        flash('This username has already voted in this poll.')
        return redirect(url_for('results', poll_id=poll_id))

    execute_db('INSERT INTO votes (option_id, poll_id, username, created_at) VALUES (?, ?, ?, ?)', (option_id, poll_id, username, datetime.utcnow()))

    return render_template('confirmation.html')


@app.route('/results/<int:poll_id>')
def results(poll_id):
    poll = query_db('SELECT * FROM polls WHERE id = ?', (poll_id,), one=True)
    if not poll:
        flash('Poll not found.')
        return redirect(url_for('index'))
    options = query_db('SELECT o.id, o.text, COUNT(v.id) as votes FROM options o LEFT JOIN votes v ON o.id = v.option_id WHERE o.poll_id = ? GROUP BY o.id ORDER BY votes DESC', (poll_id,))
    total = sum([r['votes'] for r in options])
    return render_template('results.html', poll=poll, options=options, total=total)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and not session.get('admin'):
        password = request.form.get('password', '')
        if password != ADMIN_PASSWORD:
            flash('Incorrect admin password.')
            return redirect(url_for('admin'))
        session['admin'] = True
        return redirect(url_for('admin'))

    if not session.get('admin'):
        return render_template('admin.html', logged_in=False)

    polls = query_db('SELECT * FROM polls ORDER BY created_at DESC')
    return render_template('admin.html', logged_in=True, polls=polls)


@app.route('/admin/voters/<int:poll_id>')
def admin_voters(poll_id):
    if not session.get('admin'):
        flash('Unauthorized')
        return redirect(url_for('admin'))
    poll = query_db('SELECT * FROM polls WHERE id = ?', (poll_id,), one=True)
    if not poll:
        flash('Poll not found')
        return redirect(url_for('admin'))
    voters = query_db("SELECT v.id, v.username, v.created_at, o.text as option_text FROM votes v LEFT JOIN options o ON v.option_id = o.id WHERE v.poll_id = ? ORDER BY v.created_at DESC", (poll_id,))
    return render_template('voters.html', poll=poll, voters=voters)


@app.route('/admin/create', methods=['POST'])
def admin_create():
    if not session.get('admin'):
        flash('Unauthorized')
        return redirect(url_for('admin'))
    question = request.form.get('question', '').strip()
    # accept multiple option inputs named 'options' or a single textarea 'options'
    options_list = request.form.getlist('options')
    options_raw = request.form.get('options', '')
    if not question or (not options_list and not options_raw):
        flash('Question and options are required.')
        return redirect(url_for('admin'))

    if options_list:
        options = [o.strip() for o in options_list if o.strip()]
    else:
        options = [o.strip() for o in options_raw.split('\n') if o.strip()]
    if len(options) < 2:
        flash('Provide at least two options.')
        return redirect(url_for('admin'))

    poll_id = execute_db('INSERT INTO polls (question, active, created_at) VALUES (?, ?, ?)', (question, 0, datetime.utcnow()))
    for opt in options:
        execute_db('INSERT INTO options (poll_id, text) VALUES (?, ?)', (poll_id, opt))

    flash('Poll created. Activate it when ready.')
    return redirect(url_for('admin'))


@app.route('/admin/activate/<int:poll_id>', methods=['POST'])
def admin_activate(poll_id):
    if not session.get('admin'):
        flash('Unauthorized')
        return redirect(url_for('admin'))
    execute_db('UPDATE polls SET active = 0')
    execute_db('UPDATE polls SET active = 1 WHERE id = ?', (poll_id,))
    flash('Poll activated.')
    return redirect(url_for('admin'))


@app.route('/admin/close/<int:poll_id>', methods=['POST'])
def admin_close(poll_id):
    if not session.get('admin'):
        flash('Unauthorized')
        return redirect(url_for('admin'))
    execute_db('UPDATE polls SET active = 0, closed_at = ? WHERE id = ?', (datetime.utcnow(), poll_id))
    flash('Poll closed.')
    return redirect(url_for('admin'))


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash('Logged out.')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        with app.app_context():
            if not os.path.exists(os.path.join(BASE_DIR, 'schema.sql')):
                open(os.path.join(BASE_DIR, 'schema.sql'), 'w', encoding='utf-8').write(open(os.path.join(BASE_DIR, 'schema.sql.example')).read())
            init_db()
    # run migrations (safely add new columns if DB already exists)
    with app.app_context():
        migrate_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
