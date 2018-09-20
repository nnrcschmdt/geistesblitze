from flask import Flask

from geistesblitze.models import db, User
from geistesblitze.config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


import geistesblitze.views


@app.cli.command()
def create_all():
    """Create all the tables"""
    db.create_all()
