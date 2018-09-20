from flask import jsonify, request, abort, g
from flask_httpauth import HTTPBasicAuth

from geistesblitze import app
from geistesblitze.models import db, User, Idea

auth = HTTPBasicAuth()


@app.route('/api/users', methods=['POST'])
def register_user():
    """registers a new user."""
    username = request.json.get('username')
    password = request.json.get('password')

    if username is None or password is None:
        abort(400)

    if User.query.filter_by(username=username).first() is not None:
        abort(409)

    user = User(username=username, password=password)

    db.session.add(user)
    db.session.commit()

    return jsonify(dict(id=user.id, username=user.username)), 201


@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    """gets a user by id. No authentication is needed."""
    user = User.query.get(user_id)

    if not user:
        abort(400)

    return jsonify(dict(id=user.id, username=user.username))


@auth.verify_password
def verify_password(username_or_token, password):
    """verifies that the password given is correct for the username and sets the g object."""
    user = User.verify_auth_token(username_or_token)

    if not user:
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False

    g.user = user

    return True


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    """generates an authentication token for the user."""
    token = g.user.generate_auth_token()

    return jsonify(dict(token=token.decode('ascii')))


@app.route('/api/ideas/<int:idea_id>')
@auth.login_required
def get_idea(idea_id):
    """gets an idea by id."""
    idea = Idea.query.filter_by(id=idea_id).first()

    if not idea:
        abort(404)

    if idea.user_id != g.user.id:
        abort(403)

    return jsonify(dict(id=idea.id, name=idea.name, description=idea.description))


@app.route('/api/ideas/<int:idea_id>', methods=['DELETE'])
@auth.login_required
def delete_idea(idea_id):
    """"deletes an idea by id."""
    idea = Idea.query.filter_by(id=idea_id).first()

    if not idea:
        abort(404)

    if idea.user_id != g.user.id:
        abort(403)

    db.session.delete(idea)
    db.session.commit()

    return "", 204


@app.route('/api/ideas/')
@auth.login_required
def get_ideas():
    """"gets all the ideas of the current user."""
    ideas = [dict(id=idea.id, name=idea.name, description=idea.description)
             for idea in Idea.query.filter_by(user=g.user).all()]

    return jsonify(ideas)


@app.route('/api/ideas/', methods=['POST'])
@auth.login_required
def add_idea():
    """adds a new idea."""
    name = request.json.get('name')
    description = request.json.get('description')

    idea = Idea(name=name, description=description)
    idea.user = g.user

    db.session.add(idea)
    db.session.commit()

    return jsonify(dict(id=idea.id, name=idea.name, description=idea.description)), 201


@app.route('/api/ideas/<int:idea_id>', methods=['PUT'])
@auth.login_required
def update_idea(idea_id):
    """updates an idea by id."""
    idea = Idea.query.filter_by(id=idea_id).first()

    name = request.json.get('name')
    description = request.json.get('description')

    if not idea:
        abort(404)

    if idea.user_id != g.user.id:
        abort(403)

    idea.name = name
    idea.description = description

    db.session.add(idea)
    db.session.commit()

    return jsonify(dict(id=idea.id, name=idea.name, description=idea.description)), 201
