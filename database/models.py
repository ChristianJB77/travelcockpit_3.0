from sqlalchemy import Column, create_engine, String, Integer, DateTime
from flask_sqlalchemy import SQLAlchemy
import json
import os


database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


"""APP"""


class Month(db.Model):
    __tablename__ = "months"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    name_de = db.Column(db.String(), nullable=False)
    name_en = db.Column(db.String(), nullable=False)
    # Debugging printout formatting

    def __repr__(self):
        return f'<Month {self.id} {self.name_de}>'


class DataHubCountries(db.Model):
    __tablename__ = "data_hub_countries"
    id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String())
    official_name_english = db.Column(db.String())
    iso3166_1_alpha_2 = db.Column(db.String())
    iso316_1_alpha_3 = db.Column(db.String())
    dial = db.Column(db.String())
    iso4217_currency_aplhabetic_code = db.Column(db.String())
    iso4217_currency_country_name = db.Column(db.String())
    iso4217_currency_name = db.Column(db.String())
    capital = db.Column(db.String())
    continent = db.Column(db.String())
    tld = db.Column(db.String())
    # Debugging printout formatting

    def __repr__(self):
        return f'<DataHubCountries {self.id} {self.country_name}>'

# geonames.org, http://download.geonames.org/export/dump/
class CountriesTranslate(db.Model):
    __tablename__ = "countries_translate"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(), nullable=False)
    en = db.Column(db.String(), nullable=False)
    de = db.Column(db.String(), nullable=False)
    # Debugging printout formatting

    def __repr__(self):
        return f'<CountriesTranslate {self.id} {self.area_loc}>'

#Areas/provinces (e.g. Bali)
# GID_0_0,NAME_0,gadm36_1,NAME_1,VARNAME_1,NL_NAME_1,TYPE_1,ENGTYPE_1,CC_1,HASC_1,LAT,LON
class Areas(db.Model):
    __tablename__ = "areas"
    id = db.Column(db.Integer, primary_key=True)
    iso3 = db.Column(db.String(), nullable=False)
    country_en = db.Column(db.String(), nullable=False)
    area_loc = db.Column(db.String(), nullable=False)
    area_eng = db.Column(db.String())
    area_type_loc = db.Column(db.String())
    area_type_en = db.Column(db.String())
    area_iso2 = db.Column(db.String())
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    # Debugging printout formatting

    def __repr__(self):
        return f'<Areas {self.id} {self.area_loc}>'


#41k cities list, https://simplemaps.com/data/world-cities (BASIC) - Update 2021
class Cities41k(db.Model):
    __tablename__ = "cities41k"
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(), nullable=False)
    city_ascii = db.Column(db.String(), nullable=False)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    country = db.Column(db.String())
    iso2 = db.Column(db.String(), nullable=False)
    iso3 = db.Column(db.String(), nullable=False)
    admin_name = db.Column(db.String())
    capital = db.Column(db.String())
    population = db.Column(db.Integer)
    city_id = db.Column(db.Integer)
    # Debugging printout formatting

    def __repr__(self):
        return f'<Cities41k {self.id} {self.city}>'

#Cities translate table (e.g. Munich = München)
class CitiesTranslate(db.Model):
    __tablename__ = "cities_translate"
    id = db.Column(db.Integer, primary_key=True)
    city_ascii = db.Column(db.String(200), nullable=False)
    alternative_name = db.Column(db.String())
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    iso2 = db.Column(db.String(), nullable=False)
    # Debugging printout formatting

    def __repr__(self):
        return f'<CitiesTranslate {self.id} {self.city_ascii}>'

#Cities Areas main table (>140k cities)
# https://data.world/dr5hn/country-state-city
# https://dr5hn.github.io/countries-states-cities-database/
class CitiesAreas(db.Model):
    __tablename__ = "cities_areas"
    id = db.Column(db.Integer, primary_key=True)
    city_ascii = db.Column(db.String(200), nullable=False)
    area = db.Column(db.String(200), nullable=False)
    iso2 = db.Column(db.String(3), nullable=False)
    country_en = db.Column(db.String(200), nullable=False)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    # Debugging printout formatting

    def __repr__(self):
        return f'<CitiesAreas {self.id} {self.city_ascii}>'


class ReiseKlima(db.Model):
    __tablename__ = "reise_klima"
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(), nullable=False)
    # Debugging printout formatting

    def __repr__(self):
        return f'<ReiseKlima {self.id} {self.destination}>'


class CovidCountries(db.Model):
    __tablename__ = "covid_countries"
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(), nullable=False)
    slug = db.Column(db.String(), nullable=False)
    iso2 = db.Column(db.String(), nullable=False)
    # Debugging printout formatting

    def __repr__(self):
        return f'<CovidCountries {self.id} {self.country}>'


class WorldBank(db.Model):
    __tablename__ = "world_bank"
    id = db.Column(db.Integer, primary_key=True)
    CountryName = db.Column(db.String(), nullable=False)
    CountryCode = db.Column(db.String(), nullable=False)
    SeriesName = db.Column(db.String(), nullable=False)
    SeriesCode = db.Column(db.String(), nullable=False)
    year2019 = db.Column(db.String(), nullable=False)
    # Debugging printout formatting

    def __repr__(self):
        return f'<CovidCountries {self.id} {self.SeriesName}>'


# The Economist’s Big Mac index
class BigMac(db.Model):
    __tablename__ = "big_mac"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(), nullable=False)
    iso_a3 = db.Column(db.String(4), nullable=False)
    currency_code = db.Column(db.String(4), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    local_price = db.Column(db.Float, nullable=False)
    dollar_ex = db.Column(db.Float, nullable=False)
    dollar_price = db.Column(db.Float, nullable=False)
    USD_raw = db.Column(db.Float, nullable=False)
    EUR_raw = db.Column(db.Float, nullable=False)
    GBP_raw = db.Column(db.Float, nullable=False)
    JPY_raw = db.Column(db.Float, nullable=False)
    CNY_raw = db.Column(db.Float, nullable=False)
    GDP_dollar = db.Column(db.Float)
    adj_price = db.Column(db.Float)
    USD_adjusted = db.Column(db.Float)
    EUR_adjusted = db.Column(db.Float)
    GBP_adjusted = db.Column(db.Float)
    JPY_adjusted = db.Column(db.Float)
    CNY_adjusted = db.Column(db.Float)
    # Debugging printout formatting

    def __repr__(self):
        return f'<BigMac {self.id} {self.name}>'


"""TIQETS"""


class TiqetsIDs(db.Model):
    __tablename__ = "tiqets_ids"
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(200), nullable=False)
    loc_type = db.Column(db.String(10), nullable=False)
    tiq_type = db.Column(db.String(10), nullable=False)
    tiq_id = db.Column(db.String(15), nullable=False)
    # Insert new model to database

    def insert(self):
        db.session.add(self)
        db.session.commit()
    # Debugging printout formatting

    def __repr__(self):
        return f'<TiqetsIDs {self.id} {self.location}>'


"""USERDATA"""


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(80))
    location_iso2 = db.Column(db.String(2))
    # Insert new model to database

    def insert(self):
        db.session.add(self)
        db.session.commit()
    # Debugging printout formatting

    def __repr__(self):
        return f'<User {self.id} {self.email}>'


class UserHistory(db.Model):
    __tablename__ = "user_history"
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime(), nullable=False)
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Relationship with users
    users = db.relationship('User', backref='user_history', lazy=True)
    # Insert new model to database

    def insert(self):
        db.session.add(self)
        db.session.commit()
    # Debugging printout formatting

    def __repr__(self):
        return f'<UserHistory {self.id} {self.destination} {self.user_id}>'


"""TRAVEL SECRETS BLOG"""


class Secret(db.Model):
    __tablename__ = "secrets"
    id = db.Column(db.Integer, primary_key=True)
    # Blog post title
    title = db.Column(db.String(80))
    # Top 3 reasons to go
    why1 = db.Column(db.String(80))
    why2 = db.Column(db.String(80))
    why3 = db.Column(db.String(80))
    # Blog text
    text = db.Column(db.String())
    # Search link to dashboard
    link = db.Column(db.String())
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Relationship with users
    users = db.relationship('User', backref='secrets', lazy=True)
    # Insert new model to database

    def insert(self):
        db.session.add(self)
        db.session.commit()
    # Delete model in the database

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    # Update model in the database

    def update(self):
        db.session.commit()
    # Debugging printout formatting

    def __repr__(self):
        return f'<Secret {self.id} {self.title}>'


"""TODOS"""


# Parent table for todos list
class Todo_List(db.Model):
    __tablename__ = "todos_list"
    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    todos = db.relationship('Todo', backref='list', lazy=True)
    # Debugging printout formatting

    def __repr__(self):
        return f'<Todo {self.id} {self.list_name}>'

# Child table for todos -> one to many relationship


class Todo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    todos_list_id = db.Column(db.Integer, db.ForeignKey('todos_list.id'),
                              nullable=False)
    # Debugging printout formatting

    def __repr__(self):
        return f'<Todo {self.id} {self.decription}>'
