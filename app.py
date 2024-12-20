from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
from functools import wraps
from flask import request, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

application = Flask(__name__)
application.secret_key = 'aef7e260a3049342044a9330'
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spins.db'
db = SQLAlchemy(application)


class SpinCounter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    count = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    user = db.relationship('User', backref=db.backref('spin_counter', uselist=False))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@application.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error = 'Username already exists. Please choose a different one.'
            return render_template('register.html', error=error)
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials'
            return render_template('login.html', error=error)
    return render_template('login.html')


@application.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@application.route('/')
@login_required
def index():
    user_id = session['user_id']
    user = User.query.get(user_id)
    return render_template('index.html', username=user.username)

@application.route('/get_images')
@login_required
def get_images():
    image_dir = os.path.join(application.static_folder, 'images')
    images = []
    for filename in os.listdir(image_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            images.append(f"/static/images/{filename}")
    return jsonify(images)

@application.route('/slot')
@login_required
def slot():
    user_id = session['user_id']
    counter = SpinCounter.query.filter_by(user_id=user_id).first()
    if not counter:
        counter = SpinCounter(user_id=user_id, count=0, wins=0)
        db.session.add(counter)
        db.session.commit()
    return render_template('slot.html', spin_count=counter.count, win_count=counter.wins)

@application.route('/increment_spins', methods=['POST'])
@login_required
def increment_spins():
    user_id = session['user_id']
    counter = SpinCounter.query.filter_by(user_id=user_id).first()
    if counter:
        counter.count += 1
        db.session.commit()
        return {'count': counter.count}
    else:
        return {'error': 'Counter not found'}, 404

@application.route('/increment_wins', methods=['POST'])
@login_required
def increment_wins():
    user_id = session['user_id']
    counter = SpinCounter.query.filter_by(user_id=user_id).first()
    if counter:
        counter.wins += 1
        db.session.commit()
        return {'wins': counter.wins}
    else:
        return {'error': 'Counter not found'}, 404

if __name__ == '__main__':
    with application.app_context():
        db.create_all()
    application.run(debug=True)