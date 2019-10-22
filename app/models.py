from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


gravatar = 'http://www.gravatar.com/avatar/?d=mm'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    user_info = db.Column(db.String(150))
    user_photo = db.Column(db.String(150), default=gravatar)
    active = db.Column(db.Boolean, default=True)
    admin = db.Column(db.Boolean, default=False)
    reminder = db.relationship('Reminder', backref='creator', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def deactivate(self):
        self.active = False
        db.session.commit()

    def activate(self):
        self.active = True
        db.session.commit()

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

    def save_profile_photo(self, filename):
        self.user_photo = current_app.config['PHOTOS'] + '/{}'.format(filename)
        db.session.commit()

    def get_profile_photo(self):
        return self.user_photo


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), index=True, unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    archived = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Reminder {}>'.format(self.text)

