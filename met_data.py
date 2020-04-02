#!/usr/bin/python3

import requests
import os.path
import xmltodict
import json

# Colors
RED = '\033[91m'
GREEN = '\033[92m'
ENDC = '\033[0m'

# Temp should be input to program
CORK_LAT = 51.903614
CORK_LONG = -8.468399 

lng = CORK_LONG 
lat = CORK_LAT
MET_API_URL = "http://metwdb-openaccess.ichec.ie/metno-wdb2ts/locationforecast"
MET_DATA_FILE = "met_data.xml"

payload = {'lat':lat, 'long':lng}

def get_data_api(api_url, file_path):
    print(GREEN + "Requesting Data" + ENDC) 
    req = requests.get(api_url, params=payload) 
    if (req.status_code == 200):
        print(GREEN + "API Request Success: " + str(req.status_code) + ENDC)
        f = open(file_path, "w") 
        f.write(req.text)
        f.close()
        return req.text
    else:
        print(RED + "API Request Fail: " + str(req.status_code) + ENDC)
        return None

def get_met_data(api_url, file_path):
    # Check if data in file
    if (os.path.exists(file_path)):
        print(GREEN + "Reading File: " + file_path + ENDC)
        f = open(file_path, "r") 
        xml_data = f.read()
        f.close()
        if (xml_data == ''):
            #File Empty, Request data from API
            print(RED + "File Empty: " + file_path + ENDC)
            xml_data = get_data_api(api_url, file_path)
    else:
        #File Does not exist, Request data from API
        xml_data = get_data_api(api_url, file_path)

    return xml_data

def parse_met_data(xml_data):
    met_data_xml = xmltodict.parse(xml_data)
   
    # Loop over all data points
    #for point_data in data_points:
    # Loop over indvidual weather parameters 
    i = 0
    for data_point in met_data_xml['weatherdata']['product']['time']:
        # print(data_point)
        print(str(i) + ". from: " + data_point['@from'] + " to: " + data_point['@to']) 
        i += 1

    return

def main():
    met_data_xml = get_met_data(MET_API_URL, MET_DATA_FILE)
    if (met_data_xml == ''):
        print(RED + "Failed to get Met Data" + ENDC)
        return None

    parse_met_data(met_data_xml)
    return

if __name__ == "__main__":
    main()
