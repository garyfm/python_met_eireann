#!/usr/bin/python3

import requests
import os.path
import xmltodict
import json
import datetime as dt
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import dates

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
    temperature, humidity, rain = [], [], []
    time = []
    i, j, k = 0, 0, 0
    
    # Index over all data points
    for data_point in met_data_xml['weatherdata']['product']['time']:
        # Get time points time[[from, to], [from, to], ...]
        #time[0] = data_point['@from']
        #time_point[1] = data_point['@to']
        time.append([data_point['@from'], data_point['@to']])
        print(str(i) + ". from: " +  time[i][0] + " to: " + time[i][1]) 

        # Even  = temp and humid, Odd = Rain data points
        if ((i % 2 ) == 0):
            temperature.append(data_point['location']['temperature'])
            print("\tTemperature: " + temperature[j]['@value'])
            humidity.append(data_point['location']['humidity'])
            print("\tHumidity: " + humidity[j]['@value'])
            # Index for temp and humidity lists
            j += 1
        else:
            rain.append(data_point['location']['precipitation'])
            print("\tPericipitation: " + rain[k]['@value'])
            # Index for rain list
            k += 1

        # Index over all data points 
        i += 1
    return time, temperature, humidity, rain

def plot_data(time, temp, humid, rain):
    temp_series, time_series = [], []
    i = 0

    for time_point in time:
        if ((i % 2) == 0):
            time_series.append(time_point[0])
        i+=1
    for value in temp:
        temp_series.append(value['@value'])
    
    plt.plot_date(time_series,  temp_series)
    #plt.xticks(np.arange(min(time_series), max(time_series)+1), 5)
#    temp_int = np.arange(min(temp_series), max(temp_series)+1)
    plt.xlabel("Time")
    plt.ylabel("Temperature(C)")
    plt.title("Cork Temperature")
    plt.show()

    return

def main():
    time, temp, humid, rain = [], [], [], [] 
    met_data_xml = get_met_data(MET_API_URL, MET_DATA_FILE)
    if (met_data_xml == ''):
        print(RED + "Failed to get Met Data" + ENDC)
        return None

    time, temp, humid, rain = parse_met_data(met_data_xml)
    plot_data(time, temp, humid, rain)
    return

if __name__ == "__main__":
    main()
