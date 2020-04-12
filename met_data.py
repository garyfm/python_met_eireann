#!/usr/bin/python3

import os.path
import time
import requests
import xmltodict
import json
from datetime import datetime as dt
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import dates
import matplotlib.dates as mdates
import smtplib
from email.mime.text import MIMEText
import base64
from email.mime.multipart import MIMEMultipart
import mimetypes
from email.mime.image import MIMEImage

#gmail imports
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors, discovery

# Colors
RED = '\033[91m'
GREEN = '\033[92m'
ENDC = '\033[0m'

# Temp should be input to program
CORK_LAT = 51.903614
CORK_LONG = -8.468399 
# CONSTS
SEC_24_HR = 86400

lng = CORK_LONG 
lat = CORK_LAT
MET_API_URL = "http://metwdb-openaccess.ichec.ie/metno-wdb2ts/locationforecast"
MET_DATA_FILE = "met_data.xml"
MET_GRAPH_FILE = "met_graph.png"

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
    # Check if data file exists 
    if (os.path.exists(file_path)):
        # Local data is stale, Request data from API
        if (os.path.getmtime(file_path) < (time.time() - SEC_24_HR)):
                print(RED + "File Data Stale" + ENDC)
                xml_data = get_data_api(api_url, file_path)
        else:
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

    # Get starting daytime for reference
    starting_dt = met_data_xml['weatherdata']['product']['time'][0]
    starting_dt = dt.strptime(starting_dt['@from'], "%Y-%m-%dT%H:%M:%SZ")
    # Index over all data points
    for data_point in met_data_xml['weatherdata']['product']['time']:
        current_dt= dt.strptime(data_point['@from'], "%Y-%m-%dT%H:%M:%SZ")
        if (current_dt.day > starting_dt.day):
            break;
        # Get time points time[[from, to], [from, to], ...]
        time.append([data_point['@from'], data_point['@to']])
        if ((i % 2 ) == 0):
            temperature.append(data_point['location']['temperature'])
            humidity.append(data_point['location']['humidity'])
            # Index for temp and humidity lists
            j += 1
        else:
            rain.append(data_point['location']['precipitation'])
            # Index for rain list
            k += 1

        # Index over all data points 
        i += 1
    return time, temperature, humidity, rain

def plot_data(time, temp, humid, rain):
    temp_series, humid_series, rain_series, time_series = [], [], [], []

    # Get values into a list
    for index, time_point in enumerate(time):
        if ((index % 2) == 0):
            time_series.append(time_point[0])

    for value in temp:
        temp_series.append(float(value['@value']))

    for value in humid:
        humid_series.append(float(value['@value']))
        
    for value in rain:
        rain_series.append(float(value['@value']))

    hours = [dt.strptime(time_hour, "%Y-%m-%dT%H:%M:%SZ") for time_hour in time_series]

    # Ploting
    fig, ax = plt.subplots(nrows = 3, ncols = 1) 
    ax[0].plot_date(hours,  temp_series, ls='-')
    ax[1].plot_date(hours,  humid_series, ls='-')
    ax[2].plot_date(hours,  rain_series, ls='-')

    # Configure x-ticks
    plt.xticks(hours) # Tickmark + label at every plotted point
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    ax[2].xaxis.set_major_formatter(mdates.DateFormatter('%H'))

    # Set lables 
    ax[0].set_xlabel("Time(hr)")
    ax[0].set_ylabel("Temperature(C)")
    ax[1].set_xlabel("Time(hr)")
    ax[1].set_ylabel("Humidity(%)")
    ax[2].set_xlabel("Time(hr)")
    ax[2].set_ylabel("Rain(mm)")

    ax[0].grid(True)
    ax[1].grid(True)
    ax[2].grid(True)

    plt.suptitle("Cork Weather")
    # plt.show()
    plt.savefig(MET_GRAPH_FILE)

    return
def predict_rain(time, rain):
    index = 0
    rain_predict = []

    for value in rain:
        if(float(value['@value']) <= 0): # TODO: Change to >
            # Only use odd indexs in time, TODO: fix this at source
            if((index % 2) == 0):
               index += 1 

            rain_time = time[index][0]
            print(GREEN + value['@value'] + "mm of rain predicted at: " + rain_time) 
            index += 1 
            rain_predict.append([value['@value'], rain_time])

    return rain_predict

def auth_gmail():
    #ripped from https://developers.google.com/gmail/api/quickstart/python?authuser=2

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = 'https://mail.google.com/'

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds
 
def send_email(data):
    # Create Email
    sender = "gmojo.dev@gmail.com"
    revicever = "garyfmullen@gmail.com"
    subject = "[METPY] Cork Weather"
    body = str(data)
    
    msg = MIMEMultipart()
    msg['Subject'] = subject

    msg['To'] = revicever
    msg.attach(MIMEText(body, 'plain'))
    # Attach Image
    image = open(MET_GRAPH_FILE, 'rb').read()
    msg.attach(MIMEImage(image, name=MET_GRAPH_FILE))
    raw = base64.urlsafe_b64encode(msg.as_bytes())
    raw = raw.decode()
    email_msg = {'raw': raw}

        # Auth Gmail
    creds =  auth_gmail()

    if(creds == ''):
        print(RED + "Failed to Get Gmail Creds" + ENDC)
        return False

    # Send Email
    service = build('gmail', 'v1', credentials = creds) 
    results = service.users().messages().send(userId='me', body=email_msg).execute()
    print(results) 
    return results

def main():
    time, temp, humid, rain, predicted_rain = [], [], [], [], []
    
    met_data_xml = get_met_data(MET_API_URL, MET_DATA_FILE)
    if (met_data_xml == ''):
        print(RED + "Failed to get Met Data" + ENDC)
        return None

    time, temp, humid, rain = parse_met_data(met_data_xml)
    plot_data(time, temp, humid, rain)
    predicted_rain = predict_rain(time, rain)
    result = send_email(predicted_rain)
    if (result['labelIds'] != ['SENT']):
        print(RED + "*** Failed to send email ***" + ENDC)
    else:
        print(GREEN + "*** Email send successful ***" + ENDC)

    return

if __name__ == "__main__":
    main()
