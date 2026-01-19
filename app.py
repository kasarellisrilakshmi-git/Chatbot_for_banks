from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret_key'
DATABASE = 'users.db'

notifications_for_receiver = []
notifications_for_donor = []

orphans = [
    {"name": "Orphanage A"},
    {"name": "Orphanage B"},
    {"name": "Orphanage C"},
]

hotels = [
    {"name": "Hotel Paradise"},
    {"name": "Hotel Comfort Inn"},
]

events = [
    {"name": "Charity Event"},
    {"name": "Community Food Drive"},
]

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()



def create_user_table():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                address TEXT,
                phone TEXT
            )
        """)
        db.commit()

def get_user_details(name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name, address, phone FROM users WHERE name=?", (name,))
    return cursor.fetchone()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        role = request.form['role']
        address = request.form['address']
        phone = request.form['phone']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (name, password, role, address, phone) VALUES (?, ?, ?, ?, ?)",
                       (name, password, role, address, phone))
        db.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE name=? AND password=?", (name, password))
        user = cursor.fetchone()

        if user:
            session['name'] = user[1]
            session['role'] = user[3]
            if user[3] == 'donor':
                return redirect(url_for('donor_dashboard'))
            else:
                return redirect(url_for('receiver_dashboard'))
        else:
            return "Invalid credentials! <a href='/login'>Try Again</a>"

    return render_template('login.html')

@app.route('/donor')
def donor_dashboard():
    if 'role' not in session or session['role'] != 'donor':
        return redirect(url_for('login'))
    return render_template('donor_dashboard.html', orphans=orphans, username=session['name'])

@app.route('/receiver')
def receiver_dashboard():
    if 'role' not in session or session['role'] != 'receiver':
        return redirect(url_for('login'))
    return render_template('receiver_dashboard.html', hotels=hotels, events=events, username=session['name'])

@app.route('/donate', methods=['POST'])
def donate():
    orphanage_name = request.form['orphanage']
    donor_details = get_user_details(session['name'])
    notifications_for_receiver.append({
        'name': donor_details[0],
        'address': donor_details[1],
        'phone': donor_details[2],
        'item': orphanage_name
    })
    return jsonify({'success': True, 'message': 'Donation successfully sent!'})

@app.route('/request_food', methods=['POST'])
def request_food():
    item_name = request.form['item_name']
    receiver_details = get_user_details(session['name'])
    notifications_for_donor.append({
        'name': receiver_details[0],
        'address': receiver_details[1],
        'phone': receiver_details[2],
        'item': item_name
    })
    return jsonify({'success': True, 'message': 'Request successfully sent!'})

@app.route('/get_donor_notifications')
def get_donor_notifications():
    return jsonify(notifications_for_donor)

@app.route('/get_receiver_notifications')
def get_receiver_notifications():
    return jsonify(notifications_for_receiver)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    create_user_table()
    app.run(debug=True)


