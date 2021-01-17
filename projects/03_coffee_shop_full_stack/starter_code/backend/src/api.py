import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
import sys

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES

# It is a public endpoint and it contain the drink.short() data representation.


@app.route('/drinks', methods=['GET'])
def get_drinks():

    total_drinks = Drink.query.all()
    drinks = [drink.short() for drink in total_drinks]

    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200

# GET /drinks-detail endpoint it require the 'get:drinks-detail'
# permission and it contain the drink.long() data representation.


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):

    try:
        total_drinks = Drink.query.all()

        drinks = [drink.long() for drink in total_drinks]

        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200

    except BaseException:
        abort(404)

# POST /drinks endpoint it create a new row in the drinks table, it
# require the 'post:drinks' permission, and it contain the drink.long()
# data representation.


@app.route("/drinks", methods=['POST'])
@requires_auth("post:drinks")
def post_drink(jwt):

    try:
        body = request.get_json()
        title = body.get('title')
        recipe = body.get('recipe')

        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200

    except BaseException:
        abort(422)

# PATCH /drinks/<id> endpoint it require the 'patch:drinks' permission and
# it contain the drink.long() data representation.


@app.route("/drinks/<drink_id>", methods=['PATCH'])
@requires_auth("patch:drinks")
def patch_drink(jwt, drink_id):

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if not drink:
        abort(404)

    try:
        body = request.get_json()

        if 'title' in body:
            drink.title = body.get('title')

        if 'recipe' in body:
            drink.recipe = json.dumps(body.get('recipe'))

        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200

    except BaseException:
        abort(422)

# DELETE /drinks/<id> endpoint it require the 'delete:drinks' permission.


@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):

    drink = Drink.query.get(drink_id)

    if not drink:
        abort(404)

    try:
        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        }), 200

    except BaseException:
        abort(422)

# Error Handling.


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'unauthorized '
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': 'forbidden'
    }), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resourse not found'
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'method not allowed'
    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'internal server errors'
    }), 500

# error handler for AuthError error handler should conform to general task
# above.


@app.errorhandler(AuthError)
def AuthError_handler(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code
