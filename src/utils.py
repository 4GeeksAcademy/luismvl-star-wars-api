from flask import url_for
from models import db, User, Character, Planet
from sqlalchemy import exc


class APIException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


def generate_sitemap(app):
    links = ['/admin/']
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            if "/admin/" not in url:
                links.append(url)

    links_html = "".join(["<li><a href='" + y + "'>" +
                         y + "</a></li>" for y in links])
    return """
        <div style="text-align: center;">
        <img style="max-height: 80px" src='https://storage.googleapis.com/breathecode/boilerplates/rigo-baby.jpeg' />
        <h1>Rigo welcomes you to your API!!</h1>
        <p>API HOST: <script>document.write('<input style="padding: 5px; width: 300px" type="text" value="'+window.location.href+'" />');</script></p>
        <p>Start working on your proyect by following the <a href="https://start.4geeksacademy.com/starters/flask" target="_blank">Quick Start</a></p>
        <p>Remember to specify a real endpoint path like: </p>
        <ul style="text-align: left;">"""+links_html+"</ul></div>"


# Users utils

def get_all_users():
    users = User.query.all()
    return users


def get_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    return user


def get_user_by_id(id):
    user = User.query.get(id)
    return user


def save_new_user(properties):
    user = User(username=properties['username'], email=properties['email'],
                password=properties['password'], is_active=properties['is_active'])
    db.session.add(user)
    db.session.commit()
    return user


def validate_user(user_dict):
    required_values = ['username', 'email', 'password']
    missing_values = []
    for key in required_values:
        if key not in user_dict:
            missing_values.append(key)
    return missing_values


def update_user_by_id(id, properties):
    user = User.query.get(id)
    if user is None:
        return user

    for key in user.__dict__.keys():
        print('en el for')
        if key in properties:
            setattr(user, key, properties[key])

    db.session.commit()

    return user


def delete_user_by_id(id):
    user = User.query.get(id)
    if user is None:
        return False
    db.session.delete(user)
    db.session.commit()
    return True


def save_favorite_planet(user_id, planet_id):
    planet = get_planet_by_id(planet_id)
    if planet is None:
        raise APIException(
            message='Planet not found', status_code=404)

    user = get_user_by_id(user_id)
    try:
        user.favorite_planets.append(planet)
        db.session.commit()
    except exc.IntegrityError:
        raise APIException(
            message='Planet is already favorite', status_code=400)
    return user.favorite_planets


def save_favorite_character(user_id, character_id):
    character = get_character_by_id(character_id)
    if character is None:
        raise APIException(
            message='Character not found', status_code=404)

    user = get_user_by_id(user_id)
    try:
        user.favorite_characters.append(character)
        db.session.commit()
    except exc.IntegrityError:
        raise APIException(
            message='Character is already favorite', status_code=400)
    return user.favorite_characters


def remove_planet_from_favorites(user_id, planet_id):
    planet = get_planet_by_id(planet_id)
    user = get_user_by_id(user_id)
    if planet is None:
        raise APIException(
            message='Planet not found', status_code=404)
    if planet not in user.favorite_planets:
        raise APIException(
            message='Planet is not saved in favorites', status_code=400)

    user.favorite_planets.remove(planet)
    db.session.commit()
    return user.favorite_planets


def remove_character_from_favorites(user_id, character_id):
    character = get_character_by_id(character_id)
    user = get_user_by_id(user_id)
    if character is None:
        raise APIException(
            message='Character not found', status_code=404)
    if character not in user.favorite_characters:
        raise APIException(
            message='Character is not saved in favorites', status_code=400)

    user.favorite_characters.remove(character)
    db.session.commit()
    return user.favorite_characters


# Characters utils

def get_all_characters():
    characters = Character.query.all()
    return characters


def get_character_by_id(id):
    character = Character.query.get(id)
    return character


def save_new_character(properties):
    character = Character(name=properties['name'], height=properties['height'],
                          mass=properties['mass'], hair_color=properties.get('hair_color'), eye_color=properties.get('eye_color'),
                          skin_color=properties.get('skin_color'), birth_year=properties.get('birth_date'), gender=properties.get('gender'),
                          description=properties.get('description'), planet_id=properties['planet_id'])
    db.session.add(character)
    db.session.commit()
    return character


def validate_character(character_dict):
    required_values = ['name', 'height', 'mass',  'planet_id']
    missing_values = []
    for key in required_values:
        if key not in character_dict:
            missing_values.append(key)
    return missing_values


def update_character_by_id(id, properties):
    character = Character.query.get(id)

    if character is None:
        return character

    for key in character.__dict__.keys():
        if key in properties:
            setattr(character, key, properties[key])

    db.session.commit()
    return character


def delete_character_by_id(id):
    character = Character.query.get(id)
    if character is None:
        return False
    db.session.delete(character)
    db.session.commit()
    return True


# Planets utils

def get_all_planets():
    planets = Planet.query.all()
    return planets


def get_planet_by_id(id):
    planet = Planet.query.get(id)
    return planet


def save_new_planet(properties):
    character = Planet(name=properties['name'], diameter=properties['diameter'],
                       rotation_period=properties['rotation_period'], population=properties['population'],
                       surface_water=properties['surface_water'], gravity=properties['gravity'])
    db.session.add(character)
    db.session.commit()
    return character


def validate_planet(planet_dict):
    required_values = ['name', 'diameter', 'gravity']
    missing_values = []
    for key in required_values:
        if key not in planet_dict:
            missing_values.append(key)
    return missing_values


def update_planet_by_id(id, properties):
    planet = Planet.query.get(id)

    if planet is None:
        return planet

    for key in planet.__dict__.keys():
        if key in properties:
            setattr(planet, key, properties[key])

    db.session.commit()
    return planet


def delete_planet_by_id(id):
    planet = Planet.query.get(id)
    if planet is None:
        return False
    db.session.delete(planet)
    db.session.commit()
    return True
