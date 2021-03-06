import os
import requests
import urllib.parse
import locale
from sqlalchemy import or_, and_, func
# Database
from database.models import db, DataHubCountries, WorldBank, TiqetsIDs, BigMac

# FX rate API key
FX_KEY = os.environ['FX_KEY']

def fx_rate(iso):
    # FX-rate
    try:
        info_fx = {}
        # FX-rate API -> Get JSON (https://exchangeratesapi.io/)
        res = DataHubCountries.query \
            .filter(func.lower(DataHubCountries.iso3166_1_alpha_2)
                    == iso).one_or_none()

        currency = res.iso4217_currency_aplhabetic_code
        cur_name = res.iso4217_currency_name

        # Exchange rate API url
        url = "http://api.exchangeratesapi.io/latest?symbols=USD," + currency \
                + "&access_key=" + FX_KEY

        # If requested country is using Euro, get only USD
        if currency == "EUR":
            url = "http://api.exchangeratesapi.io/latest?symbols=USD" \
                   + "&access_key=" + FX_KEY

        cur_list = requests.get(url).json()

        if currency == "EUR":
            info_fx["eur_usd"] = round(cur_list["rates"]["USD"], 2)
            info_fx["100_usd"] = round(100 / cur_list["rates"]["USD"], 2)
            info_fx["cur_name"] = "Euro"

        else:
            info_fx["cur_eur"] = round(cur_list["rates"][currency], 2)
            info_fx["cur_usd"] = round(info_fx["cur_eur"]
                                       / cur_list["rates"]["USD"], 2)
            info_fx["eur_usd"] = round(cur_list["rates"]["USD"], 2)
            info_fx["cur_name"] = cur_name
            # Get feeling for local expenses
            # idea 100 bucks of local currency in EUR
            feeling = 100 / cur_list["rates"][currency]
            # If 100 bucks in local currency are smaller than 10 EUR
            # then scale up
            factor = 100
            while feeling < 10:
                feeling *= 10
                factor *= 10

            feeling = round(feeling, 2)
            # 1000 , splitter for readability
            # Use '' for auto, or force e.g. to 'en_US.UTF-8'
            locale.setlocale(locale.LC_ALL, '')
            factor_read = f'{factor:n}'

            info_fx["feeling_cur"] = round(feeling, 1)
            info_fx["feeling_factor"] = factor_read

        return info_fx

    except Exception:
        print("######## ERROR FX-rate #########")
        info_fx = {}
        return info_fx


def info_widget(loc_classes, switch, weather):
    # Info box widget with relevant country data

    try:
        if loc_classes["country_iso"]:
            info = {}
            iso = loc_classes["country_iso"]
            # FX-rate function
            info = fx_rate(iso)
            # Language differing titles/phrases
            # German
            if switch == "German" or loc_classes['language'] == 'german':
                info["country"] = loc_classes["country_de"].title()
                info["title_euro"] = "Wechselkurse Eurol??nder"
                info["title"] = "Wechselkurse"
            # English:
            else:
                info["country"] = loc_classes["country_en"].title()
                info["title_euro"] = "FX box Euro countries"
                info["title"] = "FX box"


            """City data"""
            try:
                if loc_classes["city_loc"]:
                    info["city"] = loc_classes["city_loc"].title()
                    if loc_classes["city_pop"]:
                        # 1000 (3 comma digits), splitter for readability
                        info["city_pop"] = f'{loc_classes["city_pop"]:,}'
                elif loc_classes["city"]:
                    info["city"] = loc_classes["city"].title()
                    if loc_classes["city_pop"]:
                        # 1000 (3 comma digits), splitter for readability
                        info["city_pop"] = f'{loc_classes["city_pop"]:,}'
            except Exception:
                info["city"] = 0

            """Area data"""
            try:
                if loc_classes["area_loc"]:
                    info["area_loc"] = loc_classes["area_loc"].title()
            except Exception:
                None


            """Big Mac Index"""
            try:
                iso3 = DataHubCountries.query \
                    .filter(func.lower(DataHubCountries.iso3166_1_alpha_2) \
                    == iso).first().iso316_1_alpha_3.lower()

                # Euro currency adjusted base line price
                euro_base = BigMac.query \
                    .filter(and_(func.lower(BigMac.iso_a3) == 'euz'), \
                    BigMac.date > "2021-12-31").first().adj_price
                # Destination country
                res = BigMac.query \
                    .filter(and_(func.lower(BigMac.iso_a3) == iso3), \
                    BigMac.date > "2021-12-31").first()
                # Destination country's adjusted price
                adj_price = res.adj_price
                # Euro area adjusted price
                eur_adj = res.EUR_adjusted

                # Relative delta in percantage Euro basline vs. destination
                delta = ((adj_price + eur_adj) / euro_base) - 1
                delta_per = int(delta * 100)
                if delta_per > 0:
                    delta_per = "+" + str(delta_per)

                info["big_mac"] = delta_per

            except Exception:
                info["big_mac"] = 0


            """Tiqet ID"""
            try:
                if loc_classes["loc_type"] == "country":
                    dest = loc_classes["country_en"]
                elif loc_classes["loc_type"] == "area":
                    dest = loc_classes["area_loc"]
                elif loc_classes["city"]:
                    dest = loc_classes["city"]
                elif loc_classes["city_loc"]:
                    dest = loc_classes["city_loc"]
                else:
                    None

                if TiqetsIDs.query.filter(TiqetsIDs.location \
                    .ilike('{}%'.format(dest))).first() is not None:

                    res = TiqetsIDs.query.filter(TiqetsIDs.location \
                        .ilike('{}%'.format(dest))).first()

                    info["tiq_id"] = res.tiq_id
                    info["tiq_type"] = res.tiq_type

            except Exception:
                None

            """GDP and population"""

            # World Band database needs iso3 country code
            iso_3 = DataHubCountries.query \
                .filter(func.lower(DataHubCountries.iso3166_1_alpha_2)
                        == iso).one_or_none().iso316_1_alpha_3

            # Country population in millions
            pop = WorldBank.query.filter(WorldBank.CountryCode == iso_3) \
                .filter(WorldBank.SeriesCode == 'SP.POP.TOTL') \
                .one_or_none().year2019

            pop = round(int(pop) / (1000 * 1000), 1)
            info["pop"] = pop

            # GDP per capita
            gdp = WorldBank.query.filter(WorldBank.CountryCode == iso_3) \
                .filter(WorldBank.SeriesCode == 'NY.GDP.PCAP.CD') \
                .one_or_none().year2019

            # Convert from USD to EUR
            gdp_raw = 0.0
            gdp_cur = 0
            # Try/except loop, if fx-rate not available at API
            try:
                gdp_raw = round(float(gdp) / info["eur_usd"])
                gdp_cur = "Euro"

            except Exception:
                if gdp == '..':
                    gdp = None
                    gdp_cur = None

                else:
                    gdp_raw = round(float(gdp))
                    gdp_cur = "USD"

            # 1000 (3 comma digits), splitter for readability
            gdp = f'{gdp_raw:,}'
            info["gdp"] = gdp
            info["gdp_cur"] = gdp_cur

            """Capital, Internet domain, Country phone code"""

            # Capital
            res = DataHubCountries.query \
                .filter(func.lower(DataHubCountries.iso3166_1_alpha_2)
                        == iso).one_or_none()

            info["capital"] = res.capital
            # Internet domain
            info["internet"] = res.tld
            # country phone code
            info["phone"] = "+" + res.dial

            """GMT time zone"""
            # Get time zone delta from weather dictionary
            time_zone = weather[0]["hour_offset"]
            zone = 0

            if (int(time_zone) - time_zone) == 0:
                zone = round(time_zone)
                if zone > 0:
                    gmt = "+" + str(zone)
                else:
                    gmt = str(zone)
            else:
                zone = time_zone
                if zone > 0:
                    gmt = "+" + str(zone)
                else:
                    gmt = str(zone)

            info["time_zone"] = gmt

            return info

    except Exception:
        print("######## ERROR INFO #########")
        return None
