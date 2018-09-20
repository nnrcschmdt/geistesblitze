from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128), unique=False)
    ideas = db.relationship('Idea', backref='user', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=600):
        serializer = Serializer('hard to guess string', expires_in=expiration)

        return serializer.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        serializer = Serializer('hard to guess string')

        try:
            data = serializer.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token

        user = User.query.get(data['id'])

        return user


class Idea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=False)
    description = db.Column(db.Text(), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
