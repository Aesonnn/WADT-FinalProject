from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spins.db'
db = SQLAlchemy(application)

class SpinCounter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)

@application.route('/')
def index():
    return render_template('index.html')

@application.route('/slot')
def slot():
    counter = SpinCounter.query.first()
    if not counter:
        counter = SpinCounter(count=0, wins=0)
        db.session.add(counter)
        db.session.commit()
    return render_template('slot.html', spin_count=counter.count, win_count=counter.wins)

@application.route('/increment_spins', methods=['POST'])
def increment_spins():
    counter = SpinCounter.query.first()
    counter.count += 1
    db.session.commit()
    return {'count': counter.count}

@application.route('/increment_wins', methods=['POST'])
def increment_wins():
    counter = SpinCounter.query.first()
    counter.wins += 1
    db.session.commit()
    return {'wins': counter.wins}

if __name__ == '__main__':
    with application.app_context():
        db.create_all()
    application.run(debug=True)