#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup as bs4
req = requests.get("https://www.met.ie/weather-forecast/cork-city#forecasts")

print("Return code: ", req.status_code)

if (req.status_code == 200):
    met_soup = bs4(req.text, "lxml")
    print ("Location: ", met_soup.title.string)
    met_text = met_soup.get_text()
    met_text = met_text.split(" ")
    print (met_text)

    cork = [x for x in met_text if x == "Temperature"]
    print(cork)
    
