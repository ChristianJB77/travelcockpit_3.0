import os
import requests
import urllib.parse
from flask import redirect, render_template, request, session
from functools import wraps
from sqlalchemy import or_, func
# Database
from database.models import db, ReiseKlima, Exceptions


def links(dest, loc_classes, switch):
    # Create site specific search links for country/city/other English/German

    # Google Maps API key
    MAPS_KEY = os.environ['MAPS_KEY']

    # Links dictionary
    links_dic = {}

    # Common variables
    des = dest.replace("ä", "ae")
    des = des.replace("ü", "ue")
    des = des.replace("ö", "oe")
    des = des.replace(" ", "-")

    dest_no_space = dest.replace(" ", "-")

    if loc_classes['loc_type'] == 'country' or \
            loc_classes['loc_type'] == 'area' or \
            loc_classes['loc_type'] == 'big_city':
        country_de = loc_classes['country_de']
        country_en = loc_classes['country_en']
        country_iso = loc_classes['country_iso']
        # Convert country names to link compatible names
        co_en = country_en.replace(" ", "-")
        co_de = country_de.replace(" ", "-")
        co_de = co_de.replace("ä", "ae")
        co_de = co_de.replace("ü", "ue")
        co_de = co_de.replace("ö", "oe")

    else:
        country_iso = 0


    """Michelin Guide"""

    def mich():
        # German
        if switch == "German" or loc_classes['language'] == 'german':
            # Country
            if loc_classes['loc_type'] == 'country':
                links_dic['michelin'] = "https://guide.michelin.com/" \
                    "de/de/selection/" + country_en + "/restaurants"
            # Area
            elif loc_classes['loc_type'] == 'area':
                links_dic['michelin'] = "https://guide.michelin.com/" \
                    "de/de/" + loc_classes['area_loc'] + "/restaurants"
            # Big city
            elif loc_classes['loc_type'] == 'big_city':
                links_dic['michelin'] = "https://guide.michelin.com/" \
                    + country_iso + "/en/search?q=" \
                    + loc_classes['city']
            # Good luck mode
            else:
                links_dic['michelin'] = \
                    "https://guide.michelin.com/de/de/search?q=" \
                    + loc_classes['location']
        # English
        else:
            # Country
            if loc_classes['loc_type'] == 'country':
                links_dic['michelin'] = "https://guide.michelin.com/" \
                    + country_iso + "/en/restaurants"
            # Area
            elif loc_classes['loc_type'] == 'area':
                links_dic['michelin'] = "https://guide.michelin.com/" \
                    + country_iso + "/en/search?q=" \
                    + loc_classes['area_loc']
            # Big city
            elif loc_classes['loc_type'] == 'big_city':
                links_dic['michelin'] = "https://guide.michelin.com/" \
                    + country_iso + "/en/search?q=" \
                    + loc_classes['city']
            # Good luck mode
            else:
                links_dic['michelin'] = \
                    "https://guide.michelin.com/en/en/search?q=" \
                    + loc_classes['location']
        return

    # Exception
    if Exceptions.query \
        .filter(func.lower(Exceptions.dest) == dest).first() is not None:

        if (Exceptions.query \
            .filter(func.lower(Exceptions.dest) == dest).first().mich_link_de \
            != "") and (switch == "German" \
            or loc_classes['language'] == 'german'):

            links_dic['michelin'] = Exceptions.query \
            .filter(func.lower(Exceptions.dest) == dest).first().mich_link_de

        elif Exceptions.query \
            .filter(func.lower(Exceptions.dest) == dest).first().mich_link_en \
            != "":

            links_dic['michelin'] = Exceptions.query \
                .filter(func.lower(Exceptions.dest) == dest).first().mich_link_en

        else:
            mich()

    else:
        mich()


    """Wikipedia"""

    # German
    if switch == "German" or loc_classes['language'] == 'german':
        # Country
        if loc_classes['loc_type'] == 'country':
            links_dic['wiki'] = "https://de.wikipedia.org/wiki/" \
                                + country_de
        # Area
        elif loc_classes['loc_type'] == 'area':
            links_dic['wiki'] = "https://de.wikipedia.org/wiki/" \
                                + loc_classes["area_loc"]
        # Big City
        elif loc_classes['loc_type'] == 'big_city':
            links_dic['wiki'] = "https://de.wikipedia.org/wiki/" \
                                + loc_classes["city_loc"]
        # Good luck mode
        else:
            links_dic['wiki'] = "https://de.wikipedia.org/wiki/" \
                                + loc_classes["location"]

    # English
    else:
        # Country
        if loc_classes['loc_type'] == 'country':
            links_dic['wiki'] = "https://en.wikipedia.org/wiki/" \
                                + country_en
        # Area
        elif loc_classes['loc_type'] == 'area':
            links_dic['wiki'] = "https://en.wikipedia.org/wiki/" \
                                + loc_classes["area_loc"]
        # Big City
        elif loc_classes['loc_type'] == 'big_city':
            links_dic['wiki'] = "https://en.wikipedia.org/wiki/" \
                                + loc_classes["city"]
        # Good luck mode
        else:
            links_dic['wiki'] = "https://en.wikipedia.org/wiki/" \
                                + loc_classes["location"]

    """Lonely Planet"""

    def lp():
        # Country
        if loc_classes['loc_type'] == 'country':
            links_dic['lp'] = "https://www.lonelyplanet.com/" \
                + co_en
        # Area
        elif loc_classes['loc_type'] == 'area':
            links_dic['lp'] = "https://www.lonelyplanet.com/search?q=" \
                + loc_classes["area_loc"]
        # City
        elif loc_classes['loc_type'] == 'big_city':
            links_dic['lp'] = "https://www.lonelyplanet.com/" \
                + country_en.replace(" ", "-") + "/" \
                + loc_classes['city'].replace(" ", "-")
            # Check if site is existing
            res = requests.get(links_dic['lp']).status_code
            if res != 200:
                links_dic['lp'] = "https://www.lonelyplanet.com/search?q=" \
                    + loc_classes["city"]
        # Good luck mode
        else:
            links_dic['lp'] = "https://www.lonelyplanet.com/search?q=" \
                + loc_classes["location"]
        return

    # Exception
    if Exceptions.query \
        .filter(func.lower(Exceptions.dest) == dest).first() is not None:

        if (Exceptions.query \
            .filter(func.lower(Exceptions.dest) == dest).first().lp_link_de \
            != "") and (switch == "German" \
            or loc_classes['language'] == 'german'):

            links_dic['lp'] = Exceptions.query \
            .filter(func.lower(Exceptions.dest) == dest).first().lp_link_de

        elif Exceptions.query \
            .filter(func.lower(Exceptions.dest) == dest).first().lp_link_en \
            != "":

            links_dic['lp'] = Exceptions.query \
                .filter(func.lower(Exceptions.dest) == dest).first().lp_link_en

        else:
            lp()

    # Only English
    else:
        lp()

    """Google Maps"""
    # https://www.google.com/maps/place/Thailand/?hl=de-DE
    # German
    if switch == "German" or loc_classes['language'] == 'german':
        # Country
        if loc_classes['loc_type'] == 'country':
            links_dic['maps'] = "https://www.google.com/maps" \
                + "/embed/v1/search?key=" \
                + MAPS_KEY + country_de + "/&language=de"
        # Area
        elif loc_classes['loc_type'] == 'area':
            links_dic['maps'] = "https://www.google.com/maps" \
                + "/embed/v1/search?key=" \
                + MAPS_KEY + loc_classes["area_loc"] + "/&language=de"
        # Big City
        elif loc_classes['loc_type'] == 'big_city':
            links_dic['maps'] = "https://www.google.com/maps" \
                + "/embed/v1/search?key=" \
                + MAPS_KEY + loc_classes["city_loc"] + "/&language=de"

            print('###', links_dic['maps'])
        # Good luck mode
        else:
            links_dic['maps'] = "https://www.google.com/maps" \
                + "/embed/v1/search?key=" \
                + MAPS_KEY + loc_classes["location"] + "/&language=de"

    # English
    else:
        # Country
        if loc_classes['loc_type'] == 'country':
            links_dic['maps'] = "https://www.google.com/maps" \
                + "/embed/v1/search?key=" \
                + MAPS_KEY + country_en + "/&language=en"
        # Area
        elif loc_classes['loc_type'] == 'area':
            links_dic['maps'] = "https://www.google.com/maps" \
                + "/embed/v1/search?key=" \
                + MAPS_KEY + loc_classes["area_loc"] + "/&language=en"
        # Big City
        elif loc_classes['loc_type'] == 'big_city':
            links_dic['maps'] = "https://www.google.com/maps" \
                + "/embed/v1/search?key=" \
                + MAPS_KEY + loc_classes["city_loc"] + "/&language=en"
        # Good luck mode
        else:
            links_dic['maps'] = "https://www.google.com/maps" \
                + "/embed/v1/search?key=" \
                + MAPS_KEY + loc_classes["location"] + "/&language=en"

    """Climate"""

    # German
    if switch == "German" or loc_classes['language'] == 'german':
        # Available at reise-klima.de, upper/lower check for German Ä/Ö/Ü
        dest_up = dest.upper()
        if ReiseKlima.query \
            .filter(or_(func.upper(ReiseKlima.destination) == dest_up,
                        func.lower(ReiseKlima.destination) == dest)) \
                .one_or_none() is not None:

            links_dic['reise_klima'] = "https://www.reise-klima.de/klima/" \
                + des

        # Else go to optimale-reisezeit.de
        elif loc_classes['loc_type'] == "country" or \
                loc_classes['loc_type'] == "area" or \
                loc_classes['loc_type'] == "big_city":
            links_dic['reisezeit'] = "https://www.optimale-reisezeit.de/" \
                + co_de

        # Good luck mode
        else:
            links_dic['google_clima'] = \
                "https://www.google.com/search?q=climate+" + dest
    # English
    else:
        if loc_classes['loc_type'] == "country" or \
                loc_classes['loc_type'] == "area" or \
                loc_classes['loc_type'] == "big_city":
            links_dic['climate'] = "https://www.climatestotravel.com/climate/"\
                + co_en
        # Good luck mode
        else:
            links_dic['google_clima'] = \
                "https://www.google.com/search?q=climate+" + dest

    """Medicine / Health care"""

    # German
    if switch == "German" or loc_classes['language'] == 'german':
        # Country
        if loc_classes['loc_type'] == 'country':
            links_dic['medi_de'] = "https://www.fit-for-travel.de/reiseziel/" \
                + co_de
        # Area
        elif loc_classes['loc_type'] == 'area':
            links_dic['medi_de'] = "https://www.fit-for-travel.de/reiseziel/" \
                + co_de
        # Big City
        elif loc_classes['loc_type'] == 'big_city':
            links_dic['medi_de'] = "https://www.fit-for-travel.de/reiseziel/" \
                + co_de
        # Good luck mode
        else:
            links_dic['medi_de'] = \
                "https://www.fit-for-travel.de/%c3%bcber-300-reiseziele/"

    # English
    else:
        # Country
        if loc_classes['loc_type'] == 'country':
            links_dic['medi_en'] = \
                "https://wwwnc.cdc.gov/travel/destinations/traveler/none/" \
                + co_en
        # Area
        elif loc_classes['loc_type'] == 'area':
            links_dic['medi_en'] = \
                "https://wwwnc.cdc.gov/travel/destinations/traveler/none/" \
                + co_en
        # Big City
        elif loc_classes['loc_type'] == 'big_city':
            links_dic['medi_en'] = \
                "https://wwwnc.cdc.gov/travel/destinations/traveler/none/" \
                + co_en
        # Good luck mode
        else:
            links_dic['medi_en'] = \
                "https://wwwnc.cdc.gov/travel/destinations/list/"

    """Power plugs"""

    # German
    if switch == "German" or loc_classes['language'] == 'german':
        # Country or big_city -> country knwown
        if loc_classes['loc_type'] == "country" or\
                loc_classes['loc_type'] == "area" or\
                loc_classes['loc_type'] == "big_city":
            links_dic['power_de'] = "https://www.welt-steckdosen.de/" + co_de
        # Good luck mode
        else:
            links_dic['power_de'] = "https://www.welt-steckdosen.de/"
    # English
    else:
        # Country or big_city -> country knwown
        if loc_classes['loc_type'] == "country" or \
                loc_classes['loc_type'] == "area" or\
                loc_classes['loc_type'] == "big_city":
            links_dic['power_en'] = "https://www.power-plugs-sockets.com/" \
                + co_en
        # Good luck mode
        else:
            links_dic['power_en'] = "https://www.power-plugs-sockets.com/"

    """Government travel advisory"""

    # https://www.auswaertiges-amt.de/de/aussenpolitik/laender/korearepublik-node
    # German
    if switch == "German" or loc_classes['language'] == 'german':
        # Country or big_city -> country knwown
        if loc_classes['loc_type'] == "country" or \
                loc_classes['loc_type'] == "area" or\
                loc_classes['loc_type'] == "big_city":
            # Exception
            if country_iso == "kr":
                links_dic['gov_de'] = "https://www.auswaertiges-amt.de/de" \
                    + "/aussenpolitik/laender/korearepublik-node"
            else:
                link = "https://www.auswaertiges-amt.de/de" \
                    + "/aussenpolitik/laender/"
                # Check successful response 200 first
                links_dic['gov_de'] = link + co_de + "-node"
                if requests.get(links_dic['gov_de']).status_code != 200:
                    links_dic['gov_de'] = link + loc_classes['iso3'] + "-node"
                if requests.get(links_dic['gov_de']).status_code != 200:
                    links_dic['gov_de'] = link + co_de.replace("-", "") \
                        + "-node"
                if requests.get(links_dic['gov_de']).status_code != 200:
                    links_dic['gov_de'] = link + des + "-node"


        # Good luck mode
        else:
            links_dic['gov_de'] = \
                "https://www.auswaertiges-amt.de/de/aussenpolitik/laender/"
    # English
    else:
        # Country or big_city -> country knwown
        if loc_classes['loc_type'] == "country" or \
                loc_classes['loc_type'] == "area" or\
                loc_classes['loc_type'] == "big_city":
            links_dic['gov_en'] = "https://travel.state.gov/content/travel" \
                + "/en/traveladvisories/traveladvisories/" \
                + co_en + "-travel-advisory.html"
        # Good luck mode
        else:
            links_dic['gov_en'] = "https://travel.state.gov/content/travel" \
                + "/en/international-travel" \
                + "/International-Travel-Country-Information-Pages.html"

    """Booking.com & AirBnB"""

    # German
    if switch == "German" or loc_classes['language'] == 'german':
        # Country
        if loc_classes['loc_type'] == 'country':
            links_dic['booking'] = \
                "https://www.booking.com/searchresults.de.html?%&ss=" \
                + co_de \
                + "&group_adults=2&group_children=0&no_rooms=1" \
                + "&order=score&nflt=review_score%3D80"

            links_dic['airbnb'] = "https://www.airbnb.de/s/" \
                + country_de + "/homes"

        # Good luck mode or city
        else:
            links_dic['booking'] = \
                "https://www.booking.com/searchresults.de.html?%&ss=" \
                + des \
                + "&group_adults=2&group_children=0&no_rooms=1" \
                + "&order=score&nflt=review_score%3D80"

            links_dic['airbnb'] = "https://www.airbnb.de/s/" \
                + dest_no_space + "/homes"

    # English
    else:
        # Country
        if loc_classes['loc_type'] == 'country':
            links_dic['booking'] = \
                "https://www.booking.com/searchresults.en.html?%&ss=" \
                + co_en \
                + "&group_adults=2&group_children=0&no_rooms=1" \
                + "&order=score&nflt=review_score%3D80"

            links_dic['airbnb'] = "https://www.airbnb.com/s/" \
                + co_en + "/homes"

        # Good luck mode or city
        else:
            links_dic['booking'] = \
                "https://www.booking.com/searchresults.en.html?%&ss=" \
                + des + "&group_adults=2&group_children=0&no_rooms=1" \
                + "&order=score&nflt=review_score%3D80"

            links_dic['airbnb'] = "https://www.airbnb.com/s/" \
                + dest_no_space + "/homes"

    """Kayak & Lufthansa"""

    # German
    if switch == "German" or loc_classes['language'] == 'german':
        links_dic['kayak'] = \
            "https://www.kayak.de/explore/FRA-anywhere?stops=0"
        links_dic['lh'] = "https://www.lufthansa.com/de/de/homepage"

    # English
    else:
        links_dic['kayak'] = \
            "https://www.kayak.com/explore/FRA-anywhere?stops=0"
        links_dic['lh'] = "https://www.lufthansa.com/de/en/homepage"

    """Omio & Trainline"""
    if loc_classes['continent'] == 'eu':
        # German
        if switch == "German" or loc_classes['language'] == 'german':
            links_dic['omio'] = "https://de.omio.com/"
            links_dic['trainline'] = "https://www.thetrainline.com/de"

        # English
        else:
            links_dic['omio'] = "https://omio.com/"
            links_dic['trainline'] = "https://www.thetrainline.com/"

    if loc_classes['continent'] == 'na':
        links_dic['wanderu'] = "https://www.wanderu.com/en-us/"

    """Return links dictionary"""

    return links_dic
