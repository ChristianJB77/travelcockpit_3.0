import os
import requests
import urllib.parse
from datetime import datetime


def holiday(loc_classes, switch):
    """Next upcoming national holidays of 1 year"""

    try:
        if loc_classes["country_iso"]:
            iso = loc_classes["country_iso"]

            # Holiday dictionary
            holidays = []
            hd_dic = {}
            hd_dic["flag"] = 0
            area_flag = 0

            # National holiday API url
            url = "https://date.nager.at/Api/v2/NextPublicHolidays/" + iso
            # API response
            hd = requests.get(url).json()

            for row in hd:
                # Get and convert date format
                day = row["date"]
                day = datetime.strptime(day, '%Y-%m-%d')
                date = day.strftime('%d.%m.%y')

                # Area specific national holidays
                if row["counties"] is not None:
                    area_flag = 1
                    hd_dic["flag"] = 1
                    holidays.append({"date": date, "name": row["name"],
                                     "area": 1})
                else:
                    holidays.append({"date": date, "name": row["name"],
                                     "area": 0})

            """Language differing titles/phrases"""
            # German
            if switch == "German" or loc_classes['language'] == 'german':
                hd_dic["title"] = "Feiertage"
                if area_flag == 1:
                    hd_dic["area"] = "Gelten nicht in allen Regionen"
                else:
                    hd_dic["area"] = ""
            # English:
            else:
                hd_dic["title"] = "National holidays"
                if area_flag == 1:
                    hd_dic["area"] = "Not in all regions"
                else:
                    hd_dic["area"] = ""

            return holidays, hd_dic

    except Exception:
        print("######## ERROR HOLIDAYS #########")
        return None
