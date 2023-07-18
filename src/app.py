"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, Response
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS

from utils import *
from admin import setup_admin
from models import db, User, Character, Planet

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["JWT_SECRET_KEY"] = "wewRe1lpRaJlSpi!lqEr"
jwt = JWTManager(app)

bcrypt = Bcrypt(app)

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


# Auth endpoints

@app.route("/token", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if not email or not password:
        raise APIException(
            message='Email and password are required', status_code=400)

    user = get_user_by_email(email)
    if user is None:
        raise APIException(
            message='User not found', status_code=404)

    is_pswd_correct = bcrypt.check_password_hash(user.password, password)

    if not is_pswd_correct:
        raise APIException(
            message='Password is incorrect', status_code=401)

    access_token = create_access_token(identity=user.id)
    return {"user": user.serialize(), 'token': access_token}, 200


# Users endpoints

@app.route('/users', methods=['GET'])
def all_users():
    users = get_all_users()
    serialized_users = list(map(lambda x: x.serialize(), users))
    return serialized_users, 200


@app.route('/users/favorites', methods=['GET'])
@jwt_required()
def all_favorites():
    current_user_id = get_jwt_identity()
    user = get_user_by_id(current_user_id)
    return {
        'favorite_planets': [p.serialize() for p in user.favorite_planets],
        'favorite_people': [p.serialize() for p in user.favorite_characters]
    }, 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
@jwt_required()
def add_favorite_planet(planet_id):
    current_user_id = get_jwt_identity()
    favorite_planets_updated = save_favorite_planet(current_user_id, planet_id)

    return {'favorite_planets': [p.serialize() for p in favorite_planets_updated]}, 200


@app.route('/favorite/people/<int:character_id>', methods=['POST'])
@jwt_required()
def add_favorite_character(character_id):
    current_user_id = get_jwt_identity()
    favorite_characters_updated = save_favorite_character(
        current_user_id, character_id)
    return {'favorite_characters': [c.serialize() for c in favorite_characters_updated]}, 200


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_planet(planet_id):
    current_user_id = get_jwt_identity()
    favorite_planets_updated = remove_planet_from_favorites(
        current_user_id, planet_id)
    return {'favorite_planets': [p.serialize() for p in favorite_planets_updated]}, 200


@app.route('/favorite/people/<int:character_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_character(character_id):
    current_user_id = get_jwt_identity()
    favorite_characters_updated = remove_character_from_favorites(
        current_user_id, character_id)
    return {'favorite_planets': [c.serialize() for c in favorite_characters_updated]}, 200


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = get_user_by_id(user_id)
    if (user is None):
        return {'message': 'User not found'}, 404

    return user.serialize(), 200


@app.route('/users', methods=['POST'])
def create_user():
    request_body = request.get_json()

    missing_values = validate_user(request_body)
    if len(missing_values) > 0:
        return {'message': f'Missing value for: {", ".join(missing_values)}'}, 400

    # if_active es opcional
    if 'is_active' not in request_body:
        request_body['is_ative'] = False

    request_body['password'] = bcrypt.generate_password_hash(
        request_body['password']).decode('utf-8')
    user = save_new_user(request_body)

    return user.serialize(), 200


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    request_body = request.get_json()
    updated_user = update_user_by_id(user_id, request_body)

    if updated_user is None:
        return {'message': 'User not found'}, 404

    return updated_user.serialize(), 200


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    result = delete_user_by_id(user_id)
    if result:
        return Response(status=204)
    else:
        return {'message': 'User not found'}, 404


# Characters endpoints

@app.route('/people', methods=['GET'])
def all_characters():
    characters = get_all_characters()
    serialized_characters = list(map(lambda x: x.serialize(), characters))
    return serialized_characters, 200


@app.route('/people/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.get(character_id)
    if (character is None):
        return {'message': 'Character not found'}, 404

    return character.serialize(), 200


@app.route('/people', methods=['POST'])
def create_character():
    request_body = request.get_json()

    missing_values = validate_character(request_body)
    if len(missing_values) > 0:
        return {'message': f'Missing value for: {", ".join(missing_values)}'}, 400

    character = save_new_character(request_body)
    db.session.add(character)
    db.session.commit()
    return character.serialize(), 200


@app.route('/people/<int:character_id>', methods=['PUT'])
def update_character(character_id):
    request_body = request.get_json()

    updated_character = update_character_by_id(character_id, request_body)
    if (updated_character is None):
        return {'message': 'Character not found'}, 404

    db.session.commit()
    return updated_character.serialize(), 200


@app.route('/people/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    result = delete_character_by_id(character_id)
    if result:
        return Response(status=204)
    else:
        return {'message': 'Character not found'}, 404


# Planets endpoint

@app.route('/planets', methods=['GET'])
def all_planets():
    planets = get_all_planets()
    serialized_planets = list(map(lambda x: x.serialize(), planets))
    return serialized_planets, 200


@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_planet(planets_id):
    planet = Planet.query.get(planets_id)
    if (planet is None):
        return {'message': 'Planet not found'}, 404

    return planet.serialize(), 200


@app.route('/planets', methods=['POST'])
def create_planet():
    request_body = request.get_json()

    missing_values = validate_planet(request_body)
    if len(missing_values) > 0:
        return {'message': f'Missing value for: {", ".join(missing_values)}'}, 400

    planet = save_new_planet(request_body)
    return planet.serialize(), 200


@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    request_body = request.get_json()
    updated_planet = update_planet_by_id(planet_id, request_body)

    if updated_planet is None:
        return {'message': 'Planet not found'}, 404

    return updated_planet.serialize(), 200


@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    result = delete_planet_by_id(planet_id)
    if result:
        return Response(status=204)
    else:
        return {'message': 'Planet not found'}, 404


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
