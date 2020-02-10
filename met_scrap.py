#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup as bs4
req = requests.get("https://www.met.ie/weather-forecast/cork-city#forecasts")

print("Return code: ", req.status_code)

if (req.status_code == 200):
    html = bs4(req.text, "lxml")
    print (html.title)
