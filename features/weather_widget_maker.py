import os
import requests
import urllib.parse
from datetime import datetime, timedelta
from pytz import timezone, utc
from timezonefinder import TimezoneFinder
from sqlalchemy import or_, func
# Database
from database.models import db, DataHubCountries

# Time zone finder


def get_offset(*, lat, lon):
    """Get UTC time zone delta/offset in hours"""
    tf = TimezoneFinder()
    today = datetime.now()
    tz_target = timezone(tf.certain_timezone_at(lng=lon, lat=lat))
    # ATTENTION: tz_target could be None! handle error case
    today_target = tz_target.localize(today)
    today_utc = utc.localize(today)
    hour_offset = (today_utc - today_target).total_seconds() / 3600
    return hour_offset


def weather_widget(loc_classes, switch):
    """Weather widget"""
    # url
    url_city = "https://api.openweathermap.org/data/2.5/forecast?q=" \
        + "{},{}&cnt={}&units=metric&lang={}" \
        + "&appid=0c18985590cdc49853beafcf5eb1edce"
    url_country = "https://api.openweathermap.org/data/2.5/forecast?q=" \
        + "{}&cnt={}&units=metric&lang={}&" \
        + "appid=0c18985590cdc49853beafcf5eb1edce"

    # Global variables
    r = 0
    country = ""
    city = ""
    cnt = 30
    lang = ""

    feels_title = ""
    sunrise_title = ""
    sunset_title = ""

    # Country variable with exception handler to get CAPITAL
    if loc_classes['loc_type'] == 'country':

        iso = loc_classes["country_iso"]
        res = DataHubCountries.query \
            .filter(func.lower(DataHubCountries.iso3166_1_alpha_2)
                    == iso).one_or_none()

        capital = res.capital

    try:
        # German lang=de
        if switch == "German" or loc_classes['language'] == 'german':
            # Language title
            feels_title = "Gefühlt"
            sunrise_title = "Aufgang"
            sunset_title = "Untergang"

            # Country q=country_en
            if loc_classes['loc_type'] == 'country':
                lang = "de"
                # Get capital for time time_zone
                city = capital
                r = requests.get(url_city.format(city, iso, cnt, lang)).json()
            # Area q=area,country_iso
            elif loc_classes['loc_type'] == 'area':
                area = loc_classes['area_loc']
                iso = loc_classes['country_iso']
                lang = "de"
                r = requests.get(url_city.format(area, iso, cnt, lang)).json()
            # Big city q=city,country_iso
            elif loc_classes['loc_type'] == 'big_city':
                city = loc_classes['city']
                iso = loc_classes['country_iso']
                lang = "de"
                r = requests.get(url_city.format(city, iso, cnt, lang)).json()
            # Goog luck q=location
            else:
                loc = loc_classes['location']
                lang = "de"
                r = requests.get(url_country.format(loc, cnt, lang)).json()

        # English lang=en
        else:
            # Language title
            feels_title = "Feels like"
            sunrise_title = "Sunrise"
            sunset_title = "Sunset"
            # Country q=country_en
            if loc_classes['loc_type'] == 'country':
                lang = "en"
                # Get capital for time time_zone
                city = capital
                r = requests.get(url_city.format(city, iso, cnt, lang)).json()
            # Area q=area,country_iso
            elif loc_classes['loc_type'] == 'area':
                area = loc_classes['area_loc']
                iso = loc_classes['country_iso']
                lang = "en"
                r = requests.get(url_city.format(area, iso, cnt, lang)).json()
            # Big city q=city,country_iso
            elif loc_classes['loc_type'] == 'big_city':
                city = loc_classes['city']
                iso = loc_classes['country_iso']
                lang = "en"
                r = requests.get(url_city.format(city, iso, cnt, lang)).json()
            # Goog luck q=location
            else:
                loc = loc_classes['location']
                lang = "en"
                r = requests.get(url_country.format(loc, cnt, lang)).json()

        # Catch relevant data from API response and save in weather list
        weather = []

        # Get next forecast time in local time zone
        # Get first entrance from list, which closest to current time
        unix_time = int(r["list"][0]["dt"])
        # Get time zone offset vs. UTC
        loc = r["city"]["coord"]
        hour_offset = get_offset(**loc)
        # Timedelta
        hour_delta = timedelta(hours=hour_offset)
        # Get today, by converting unix time, as month day integer
        today_utc = datetime.utcfromtimestamp(unix_time)
        today = (today_utc + hour_delta).strftime("%d")
        day_utc = datetime.utcfromtimestamp(unix_time)

        # Language weekday translation
        weekdays_en = {"Mon": "Mo", "Tue": "Di", "Wed": "Mi", "Thu": "Do",
                       "Fri": "Fr", "Sat": "Sa", "Sun": "So"}
        weekdays_de = {"Mo": "Mon", "Di": "Tue", "Mi": "Wed", "Do": "Thu",
                       "Fr": "Fri", "Sa": "Sat", "So": "Sun"}
        day_name = ""
        if lang == "de":
            day_name_raw = (day_utc + hour_delta).strftime('%a')
            if day_name_raw in weekdays_en:
                day_name = weekdays_en[day_name_raw]
            else:
                day_name = day_name_raw

        else:
            day_name_raw = (day_utc + hour_delta).strftime('%a')
            if day_name_raw in weekdays_de:
                day_name = weekdays_de[day_name_raw]
            else:
                day_name = day_name_raw

        # Convert unix time of sunrise and sunset to HH:MM local time
        sunrise_utc = datetime.utcfromtimestamp(int(r["city"]["sunrise"]))
        sunrise = (sunrise_utc + hour_delta).strftime("%H:%M")
        sunset_utc = datetime.utcfromtimestamp(int(r["city"]["sunset"]))
        sunset = (sunset_utc + hour_delta).strftime("%H:%M")
        # Append first entrance of a time which is closet in future to current
        weather.append({
                "dest": r["city"]["name"],
                "hour_offset": hour_offset,
                "sunrise": sunrise,
                "sunrise_title": sunrise_title,
                "sunset": sunset,
                "sunset_title": sunset_title,
                "day": day_name,
                "today": today,  # timestamp in local time
                "temp": round(r["list"][0]["main"]["temp"]),
                "feels_title": feels_title,
                "feels_like": round(r["list"][0]["main"]["feels_like"]),
                "humidity": r["list"][0]["main"]["humidity"],
                "description": r["list"][0]["weather"][0]["description"],
                "icon": r["list"][0]["weather"][0]["icon"],
                "wind": round(r["list"][0]["wind"]["speed"])
                    })

        # Add necessary forecast info, see widget
        days = []
        for i in range(1, cnt):
            unix_time = int(r["list"][i]["dt"])
            # Get forecast day and time
            day_utc = datetime.utcfromtimestamp(unix_time)
            day = (day_utc + hour_delta).strftime('%d')

            if (day != today) and day not in days:
                days.append(day)

        # Loop trough tomorrow and day after tomorrow
        for i in range(0, 2):
            temp_min = 300
            temp_max = -279
            humi_min = 100
            humi_max = 0
            win_min = 300
            win_max = 0
            day_name = ""
            # Find max and min temperature
            for j in range(1, cnt):
                unix_time = int(r["list"][j]["dt"])
                # Get forecast day and time, by converting unix time
                # as month day integer
                day_utc = datetime.utcfromtimestamp(unix_time)
                day = (day_utc + hour_delta).strftime('%d')

                if days[i] == day:
                    # Language weekday
                    day_name = ""
                    if lang == "de":
                        day_name_raw = (day_utc + hour_delta).strftime('%a')
                        if day_name_raw in weekdays_en:
                            day_name = weekdays_en[day_name_raw]
                        else:
                            day_name = day_name_raw

                    else:
                        day_name_raw = (day_utc + hour_delta).strftime('%a')
                        if day_name_raw in weekdays_de:
                            day_name = weekdays_de[day_name_raw]
                        else:
                            day_name = day_name_raw

                    # Find min/max temperature
                    if round(r["list"][j]["main"]["temp"]) > temp_max:
                        temp_max = round(r["list"][j]["main"]["temp"])
                    if round(r["list"][j]["main"]["temp"]) < temp_min:
                        temp_min = round(r["list"][j]["main"]["temp"])
                    # Find min/max humidity
                    if round(r["list"][j]["main"]["humidity"]) > humi_max:
                        humi_max = round(r["list"][j]["main"]["humidity"])
                    if round(r["list"][j]["main"]["humidity"]) < humi_min:
                        humi_min = round(r["list"][j]["main"]["humidity"])
                    # Find min/max wind
                    if r["list"][j]["wind"]["speed"] > win_max:
                        win_max = round(r["list"][j]["wind"]["speed"])
                    if round(r["list"][j]["wind"]["speed"]) < win_min:
                        win_min = round(r["list"][j]["wind"]["speed"])

            weather.append({"day": day_name,
                            "icon": r["list"][i]["weather"][0]["icon"],
                            "temp_max": temp_max,
                            "temp_min": temp_min,
                            "humi_max": humi_max,
                            "humi_min": humi_min,
                            "wind_max": win_max,
                            "wind_min": win_min})

        return weather

    except (KeyError, TypeError, ValueError):
        return None
