from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    is_active = db.Column(db.Boolean(), nullable=False, default=False)
    favorite_characters = db.relationship(
        'Character', secondary='favorite_characters', backref='users', lazy=True)
    favorite_planets = db.relationship(
        'Planet', secondary='favorite_planets', backref='users', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "is_active": self.is_active
        }


class Character(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    height = db.Column(db.Integer, nullable=False)
    mass = db.Column(db.Integer, nullable=False)
    hair_color = db.Column(db.String(250))
    eye_color = db.Column(db.String(250))
    skin_color = db.Column(db.String(250))
    birth_year = db.Column(db.String(250))
    gender = db.Column(db.String(250))
    description = db.Column(db.String(250))
    planet_id = db.Column(db.Integer, db.ForeignKey(
        'planets.id'), nullable=False)
    homeworld = db.relationship('Planet', lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "skin_color": self.skin_color,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "description": self.description,
            "homeworld": self.homeworld.serialize()
        }


class Planet(db.Model):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    diameter = db.Column(db.Integer, nullable=False)
    gravity = db.Column(db.String(250), nullable=False)
    rotation_period = db.Column(db.Integer)
    orbital_period = db.Column(db.Integer)
    population = db.Column(db.Integer)
    surface_water = db.Column(db.Integer)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "rotation_period": self.rotation_period,
            "population": self.population,
            "surface_water": self.surface_water,
            "gravity": self.gravity,
        }


favorite_characters = db.Table('favorite_characters',
                               db.Column('user_id', db.Integer,
                                         db.ForeignKey('users.id'), primary_key=True),
                               db.Column('character_id', db.Integer,
                                         db.ForeignKey('characters.id'), primary_key=True)
                               )

favorite_planets = db.Table('favorite_planets',
                        db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                        db.Column('planet_id', db.Integer, db.ForeignKey('planets.id'), primary_key=True)
                    )
