from bs4 import BeautifulSoup
import requests
import re
# Database
from database.models import db, TiqetsIDs

def getLinks(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")


    for link in soup.find_all('a'):
        raw = link.get('href').split("/")
        temp = ""
        if raw[1] == "en":
            for i in range(2, len(raw) - 1):
                complete = raw[i].split('-')
                for i in range(0, len(complete)):
                    if complete[i] == "attractions":
                        continue
                    # Localtion name
                    elif not complete[i][-1].isnumeric():
                        if len(temp) > 0:
                            temp += " " + complete[i]
                        else:
                            temp = complete[i]
                    # Location id
                    else:
                        loc = complete[i]
                        # Country
                        if loc[0] == 'z':
                            tiqets_ids = TiqetsIDs(
                                location=temp,
                                loc_type="country",
                                tiq_type="country",
                                tiq_id=loc[1:])
                            tiqets_ids.insert()
                        # Region
                        if loc[0] == 'r':
                            tiqets_ids = TiqetsIDs(
                                location=temp,
                                loc_type="area",
                                tiq_type="region",
                                tiq_id=loc[1:])
                            tiqets_ids.insert()
                        # City
                        if loc[0] == 'c':
                            tiqets_ids = TiqetsIDs(
                                location=temp,
                                loc_type="big_city",
                                tiq_type="city",
                                tiq_id=loc[1:])
                            tiqets_ids.insert()

    return None

if __name__ == '__main__':
    getLinks("https://www.tiqets.com/en/all-destinations")
