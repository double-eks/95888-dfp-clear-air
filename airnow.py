'''
Group 9: AirWise
Xiao Xu
xiaoxu@andrew.cmu.edu

Filename: airnow.py

Module: AirNow requests daily AQI data from AirNow open API (API keys pre-embedded)

95-888 Data Focused Python
Spring 2023 Mini 3
'''

from datetime import datetime

import pandas as pd
import requests


class AirNow():

    _HOST = 'http://www.airnowapi.org'
    _ENDPOINT_CURR_ZIP = '/aq/observation/zipCode/current'
    _ENDPOINT_HIST_ZIP = '/aq/observation/zipCode/historical'
    _ENDPOINT_FORECAST_ZIP = '/aq/forecast/zipCode'
    _RETURN_FORMAT = 'application/json'
    _API_KEY = 'A40B3F56-3333-4A88-AD52-ADC3117F4DC2'

    def __init__(self):
        self.rawCurrDate = 'DateObserved'
        self.rawHistDate = 'DateObserved'
        self.rawForecastDate = 'DateForecast'
        self.initLegend()

    def getCurrByZip(self, zipCode: str, distanceMiles: int = 30):
        paraTemplate = '/?format={}&zipCode={}&distance={}&API_KEY={}'
        requestParas = paraTemplate.format(AirNow._RETURN_FORMAT,
                                           zipCode, distanceMiles,
                                           AirNow._API_KEY)
        requestUrl = AirNow._HOST + AirNow._ENDPOINT_CURR_ZIP + requestParas
        return self.requestToDf(requestUrl, self.rawCurrDate, 'Current Observation')

    def getHistByZip(self, zipCode: str, date: datetime, distanceMiles: int = 30):
        paraTemplate = '/?format={}&zipCode={}&date={}T00-0000&distance={}&API_KEY={}'
        if (isinstance(date, datetime)):
            dateStr = date.strftime('%Y-%m-%d')
        else:
            dateStr = date
        requestParas = paraTemplate.format(AirNow._RETURN_FORMAT,
                                           zipCode, dateStr, distanceMiles,
                                           AirNow._API_KEY)
        requestUrl = AirNow._HOST + AirNow._ENDPOINT_HIST_ZIP + requestParas
        return self.requestToDf(requestUrl, self.rawHistDate, 'Historcal Observation')

    def getForecastByZip(self, zipCode: str, date: datetime, distanceMiles: int = 30):
        paraTemplate = '/?format={}&zipCode={}&date={}&distance={}&API_KEY={}'
        dateStr = date.strftime('%Y-%m-%d')
        requestParas = paraTemplate.format(AirNow._RETURN_FORMAT,
                                           zipCode, dateStr, distanceMiles,
                                           AirNow._API_KEY)
        requestUrl = AirNow._HOST + AirNow._ENDPOINT_FORECAST_ZIP + requestParas
        return self.requestToDf(requestUrl, self.rawForecastDate, 'Forecasting')

    def requestToDf(self, url: str, rawDateName: str, time: str):
        response = requests.get(url)
        if (response.status_code == 200):
            data = response.json()
            df = pd.DataFrame(data)
            categories = pd.DataFrame.from_records(df['Category'])
            df['Data Type'] = time
            df.loc[:, 'Number'] = categories['Number']
            df.loc[:, 'Name'] = categories['Name']
            df.loc[:, 'Level'] = categories['Name']
            df.loc[:, 'Date'] = df[rawDateName]
            df.loc[:, 'Pollutant'] = df['ParameterName']
            o3toRename = df['ParameterName'] == 'O3'
            df.loc[o3toRename, 'Pollutant'] = 'Ozone'
            for row in df.index:
                i = int(df.loc[row, 'Number']) - 1
                color = self.legend.color[i]
                colorCols = ['Level'] if (i == 0) else [
                    'Date', 'Data Type', 'Pollutant', 'AQI', 'Level']
                for col in colorCols:
                    df.loc[row, col] = color.format(df.loc[row, col])
            return df
        else:
            print('Oops,\tno data available')

    def initLegend(self):
        colors = ['\u001B[32m{}\u001B[0m', '\u001B[33m{}\u001B[0m',
                  '\u001B[31m{}\u001B[0m', '\u001B[1;31m{}\u001B[0m',
                  '\u001B[1;35m{}\u001B[0m', '\u001B[1;4;35m{}\u001B[0m']
        self.legend = pd.DataFrame(colors,
                                   columns=['color'])
