import os
import requests
import urllib.parse
from flask import redirect, render_template, request, session
from functools import wraps
from sqlalchemy import or_, func
# Database
from database.models import db, DataHubCountries, CountriesTranslate, \
    Cities41k, Areas, CitiesTranslate


def check(destination):
    """Check and format user input"""
    # Format user input
    try:
        dest = destination.replace("-", " ").lower()
        dest = dest.replace("_", " ")
        dest = dest.replace(",", "")
        # Remove space at the end
        wrong_end = " !§$%&/()[]{}?=+*#'-_,;.:<>|@€^°`´"
        while dest[-1] in wrong_end:
            dest = dest[:-1]

        return dest

    except (KeyError, TypeError, ValueError):
        return None


def loc_class(dest):
    """Classify location (country/area/city/other), tranlsate to GER and ENG"""
    dest = dest.lower()
    dest_no_space = dest.replace(" ", "")
    dest_up = dest.upper()
    dest_up_link = dest_up.replace(" ", "-")
    dest_dic = {}

    # Country check
    # Country check English or ISO
    if DataHubCountries.query \
        .filter(or_(func.lower(DataHubCountries.country_name) == dest,
                    func.lower(DataHubCountries.iso3166_1_alpha_2) == dest,
                    func.lower(DataHubCountries.iso316_1_alpha_3) == dest,
                    func.lower(DataHubCountries.official_name_english) == dest,
                    func.lower(DataHubCountries.iso4217_currency_country_name)
                    == dest)).first() is not None:

        # Location type for link functions
        dest_dic['loc_type'] = "country"
        # Get ISO alpha2 code
        country_iso = DataHubCountries.query \
            .filter(or_(func.lower(DataHubCountries.country_name) == dest,
                    func.lower(DataHubCountries.iso3166_1_alpha_2) == dest,
                    func.lower(DataHubCountries.iso316_1_alpha_3) == dest,
                    func.lower(DataHubCountries.official_name_english) == dest,
                    func.lower(DataHubCountries.iso4217_currency_country_name)
                    == dest)).first().iso3166_1_alpha_2.lower()

        dest_dic['country_iso'] = country_iso
        # Translate to German and English
        dest_dic['country_de'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().de.lower()
        dest_dic['country_en'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().en.lower()

        # Language tag
        dest_dic['language'] = "english"
        # Print out for html title
        dest_dic['print'] = dest_dic['country_en'].title()
        return dest_dic

    # Country check GERMAN
    elif CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.de) == dest) \
                .first() is not None:

        # Location type for link functions
        dest_dic['loc_type'] = "country"
        # Get ISO alpha2 code
        country_iso = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.de) == dest) \
            .first().code.lower()

        dest_dic['country_iso'] = country_iso
        # Translate to German and English
        dest_dic['country_de'] = dest
        dest_dic['country_en'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().en.lower()

        dest_dic['language'] = "german"
        # Print out for html title
        dest_dic['print'] = dest_dic['country_de'].title()
        return dest_dic

    # Replace space in German and try again
    elif CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.de) == dest_no_space) \
            .first() is not None:
        dest = dest_no_space
        # Location type for link functions
        dest_dic['loc_type'] = "country"
        # Get ISO alpha2 code
        country_iso = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.de) == dest) \
            .first().code.lower()
        dest_dic['country_iso'] = country_iso
        # Translate to German and English
        dest_dic['country_de'] = dest
        dest_dic['country_en'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().en.lower()

        dest_dic['language'] = "german"
        # Print out for html title
        dest_dic['print'] = dest_dic['country_de'].title()
        return dest_dic

    # Format all to upper case debugging for special character ä, ö, ü
    elif CountriesTranslate.query \
            .filter(func.upper(CountriesTranslate.de) == dest_up) \
            .first() is not None:
        dest = dest_up
        # Location type for link functions
        dest_dic['loc_type'] = "country"
        # Get ISO alpha2 code
        country_iso = CountriesTranslate.query \
            .filter(func.upper(CountriesTranslate.de) == dest) \
            .first().code.lower()
        dest_dic['country_iso'] = country_iso
        # Translate to English and German
        dest_dic['country_de'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().de.lower()
        dest_dic['country_en'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().en.lower()

        dest_dic['language'] = "german"
        # Print out for html title
        dest_dic['print'] = dest_dic['country_de'].title()
        return dest_dic

    # Area/province EXACT check
    elif Areas.query \
        .filter(func.lower(Areas.area_loc) == dest).first() is not None:

        # Check if area = city name
        if Cities41k.query \
                .filter(func.lower(Cities41k.city_ascii) == dest) \
                .first() is not None:
            dest_dic['city'] = dest
            dest_dic['city_pop'] = Cities41k.query \
                .filter(func.lower(Cities41k.city_ascii) == dest) \
                .first().population

        # Location type for link functions
        dest_dic['loc_type'] = "area"
        # Get area local name
        dest_dic['area_loc'] = Areas.query \
            .filter(func.lower(Areas.area_loc) == dest).first().area_loc.lower()
        # Get iso2 for country names in German and English
        iso3 = Areas.query \
            .filter(func.lower(Areas.area_loc) == dest).first().iso3.lower()
        country_iso = DataHubCountries.query \
            .filter(func.lower(DataHubCountries.iso316_1_alpha_3) == iso3) \
            .first().iso3166_1_alpha_2.lower()
        dest_dic['country_iso'] = country_iso
        # Translate to English and German
        dest_dic['country_de'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().de.lower()
        dest_dic['country_en'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().en.lower()

        dest_dic['language'] = "unclear"
        # Print out for html title
        dest_dic['print'] = dest_dic['area_loc'].title()
        return dest_dic


    # Format all to upper case debugging for special character ä, ö, ü
    elif Areas.query \
        .filter(func.upper(Areas.area_loc) == dest_up_link).first() is not None:

        dest = dest_up_link
        # Check if area = city name
        if Cities41k.query \
                .filter(func.upper(Cities41k.city_ascii) == dest) \
                .first() is not None:
            dest_dic['city'] = dest
            dest_dic['city_pop'] = Cities41k.query \
                .filter(func.upper(Cities41k.city_ascii) == dest) \
                .first().population

        # Location type for link functions
        dest_dic['loc_type'] = "area"
        # Get area local name
        dest_dic['area_loc'] = Areas.query \
            .filter(func.upper(Areas.area_loc) == dest).first().area_loc.lower()
        # Get iso2 for country names in German and English
        iso3 = Areas.query \
            .filter(func.upper(Areas.area_loc) == dest).first().iso3.lower()
        country_iso = DataHubCountries.query \
            .filter(func.lower(DataHubCountries.iso316_1_alpha_3) == iso3) \
            .first().iso3166_1_alpha_2.lower()
        dest_dic['country_iso'] = country_iso
        # Translate to English and German
        dest_dic['country_de'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().de.lower()
        dest_dic['country_en'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().en.lower()

        dest_dic['language'] = "german"
        # Print out for html title
        dest_dic['print'] = dest_dic['area_loc'].title()
        return dest_dic


    # City check
    # Big city check from 41k list
    elif Cities41k.query \
            .filter(func.lower(Cities41k.city_ascii) == dest).first() is not None:

        # Location type for link functions
        dest_dic['loc_type'] = "big_city"
        # Save city name
        dest_dic['city'] = dest
        # Get ISO alpha2 code
        country_iso = Cities41k.query \
            .filter(func.lower(Cities41k.city_ascii) == dest) \
            .first().iso2.lower()
        dest_dic['country_iso'] = country_iso
        # Get population
        dest_dic['city_pop'] = Cities41k.query \
            .filter(func.lower(Cities41k.city_ascii) == dest) \
            .first().population
        # Translate to English and German
        dest_dic['country_de'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().de.lower()
        dest_dic['country_en'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().en.lower()

        dest_dic['language'] = "unclear"
        # Print out for html title
        dest_dic['print'] = dest_dic['city'].title()
        return dest_dic


    # City check LOCAL language
    elif CitiesTranslate.query \
        .filter(CitiesTranslate.alternative_name.ilike('%{}%'.format(dest))) \
        .first() is not None:

        # Location type for link functions
        dest_dic['loc_type'] = "big_city"
        # Get response from cities translate
        r = CitiesTranslate.query \
            .filter(CitiesTranslate.alternative_name \
            .ilike('%{}%'.format(dest))) \
            .first()
        # Get city name
        dest_dic['city'] = r.city_ascii.lower()
        # Get ISO alpha2 code
        country_iso = r.iso2.lower()
        dest_dic['country_iso'] = country_iso
        # Get population
        dest_dic['city_pop'] = Cities41k.query \
            .filter(func.lower(Cities41k.city_ascii) == dest_dic['city']) \
            .first().population
        # Translate to English and German
        dest_dic['country_de'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().de.lower()
        dest_dic['country_en'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().en.lower()

        dest_dic['language'] = "unclear"
        # Print out for html title
        dest_dic['print'] = dest.title()
        return dest_dic


    # Area/province SIMILAR check
    elif Areas.query \
        .filter(Areas.area_eng.ilike('%{}%'.format(dest))).first() is not None:

        # Location type for link functions
        dest_dic['loc_type'] = "area"
        # Get area local name
        dest_dic['area_loc'] = Areas.query \
            .filter(Areas.area_eng.ilike('%{}%'.format(dest))) \
            .first().area_loc.lower()
        # Get iso2 for country names in German and English
        iso3 = Areas.query \
            .filter(Areas.area_eng.ilike('%{}%'.format(dest))) \
                .first().iso3.lower()
        country_iso = DataHubCountries.query \
            .filter(func.lower(DataHubCountries.iso316_1_alpha_3) == iso3) \
            .first().iso3166_1_alpha_2.lower()
        dest_dic['country_iso'] = country_iso
        # Translate to English and German
        dest_dic['country_de'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().de.lower()
        dest_dic['country_en'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().en.lower()

        dest_dic['language'] = "unclear"
        # Print out for html title
        dest_dic['print'] = dest_dic['area_loc'].title()
        return dest_dic

    # Search, if user input is misspelled
    elif DataHubCountries.query \
        .filter(DataHubCountries.country_name.ilike('%{}%'.format(dest))) \
        .first() is not None:

        # Location type for link functions
        dest_dic['loc_type'] = "country"
        # Get ISO alpha2 code
        country_iso = DataHubCountries.query \
            .filter(DataHubCountries.country_name.ilike('%{}%'.format(dest))) \
            .first().iso3166_1_alpha_2.lower()

        dest_dic['country_iso'] = country_iso
        # Translate to German and English
        dest_dic['country_de'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().de.lower()
        dest_dic['country_en'] = CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.code)
                    == country_iso).first().en.lower()

        # Language tag
        dest_dic['language'] = "english"
        # Print out for html title
        dest_dic['print'] = dest_dic['country_en'].title()
        return dest_dic

    # Good luck, country and city unknown
    else:
        dest_dic['loc_type'] = "good_luck"
        dest_dic['location'] = dest
        dest_dic['language'] = "unclear"
        # Print out for html title
        dest_dic['print'] = "Good Luck Mode for: " \
            + dest_dic['location'].title()
        return dest_dic
