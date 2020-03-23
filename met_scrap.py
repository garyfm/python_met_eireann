#!/usr/bin/python3

import requests

# Colors
RED = '\033[91m'
GREEN = '\033[92m'
ENDC = '\033[0m'

# Temp should be input to program
CORK_LONG = 51.903614
CORK_LAT = -8.468399 

lng = CORK_LONG 
lat = CORK_LAT
MET_API_URL = "http://metwdb-openaccess.ichec.ie/metno-wdb2ts/locationforecast?"

def get_met_data(api_url):
    req = requests.get(MET_API_URL + "lat=" + str(lng) + ";long=" + str(lat))

    if (req.status_code == 200):
        print(GREEN + "API Request Success: " + str(req.status_code) + ENDC)
        return req.text
    else:
        print(RED + "API Request Fail: " + str(req.status_code) + ENDC)

    return

def main():
   met_data = get_met_data(MET_API_URL) 

if __name__ == "__main__":
    main()
