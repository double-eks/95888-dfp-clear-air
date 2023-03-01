import os

os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"

import io
import zipfile
from datetime import datetime

import pandas as pd
import requests
from matplotlib.axes import Axes


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
        dateStr = date.strftime('%Y-%m-%d')
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

    def initLegend(self):
        colors = ['\u001B[32m{}\u001B[0m', '\u001B[33m{}\u001B[0m',
                  '\u001B[31m{}\u001B[0m', '\u001B[1;31m{}\u001B[0m',
                  '\u001B[1;35m{}\u001B[0m', '\u001B[1;4;35m{}\u001B[0m']
        self.legend = pd.DataFrame(colors,
                                   columns=['color'])
        ozone = ["It's a great day to be active outside.",

                 "Unusually sensitive people consider reducing prolonged or "
                 "heavy outdoor exertion, and watch for symptoms such as coughing or "
                 "shortness of breath. These are signs to take it easier.\n"
                 "For everyone else, it's a good day to be active outside.",

                 'People with asthma should follow their asthma action plans and '
                 'keep quick-relief medicine handy.\n'
                 'Sensitive groups reduce prolonged or heavy outdoor exertion, '
                 'take more breaks, do less intense activities, watch for symptoms '
                 'such as coughing or shortness of breath, and schedule outdoor '
                 'activities in the morning when ozone is lower.',

                 'People with asthma keep quick-relief medicine handy.\n'
                 'Sensitive groups avoid prolonged or heavy outdoor exertion, '
                 'schedule outdoor activities in the morning when ozone is lower. '
                 'and consider moving activities indoors.\n'
                 'Everyone else reduces prolonged or heavy outdoor exertion. Take more breaks, do less intense activities. Schedule outdoor activities in the morning when ozone is lower. '
                 ]


class EpaAqs():
    def __init__(self) -> None:
        self.url = 'https://aqs.epa.gov/aqsweb/airdata/{}_aqi_by_{}_{}.zip'
        self.aqiDict = self.initLegendDf()

    def request(self, year: int, city: str, state: str,
                stats: str = 'daily', area: str = 'cbsa'):
        url = self.url.format(stats, area, year)
        response = requests.get(url)
        zippedFile = zipfile.ZipFile(io.BytesIO(response.content))
        csvFilename = zippedFile.namelist()[0]
        csvFile = zippedFile.open(csvFilename)
        df = pd.read_csv(csvFile)
        csvFile.close()
        zippedFile.close()
        df = df.loc[df['CBSA'] == f'{city}, {state}', :]
        return df

    def initLegendDf(self):
        result = {
            'color': ['#00e400', '#ffff00', '#ff7e00', '#ff0000', '#8f3f97', '#7e0023'],
            'aqi': [(0, 50), (50, 100), (100, 150), (150, 200), (200, 300), (300, 500)],
            'category': ['Good', 'Moderate', 'Unhealthy for Sensitive Groups',
                         'Unhealthy', 'Very Unhealthy', 'Hazardous'],
            'number': [i for i in range(1, 7)]
        }
        df = pd.DataFrame(result)
        return df

    def findWorstRange(self, worst):
        for row in self.aqiDict.index:
            levelMax = self.aqiDict.loc[row, 'aqi'][1]
            if (worst < levelMax):
                return row

    def drawTrendPlot(self, ax: Axes, df: pd.DataFrame):
        dates = pd.to_datetime(df['Date'])
        worstAQI = df['AQI'].values.max()
        worstLevelRow = self.findWorstRange(worstAQI)
        yMax = self.aqiDict.loc[worstLevelRow, 'aqi'][1]
        self.setFrame(ax, 'gray')
        self.drawBackground(ax, worstLevelRow)
        # ax.grid(True, axis='y', linestyle='dotted')
        ax.set_xlim(dates.min(), dates.max())
        ax.set_ylim(0, yMax)
        ax.tick_params(axis='both', labelsize=8, color='gray')
        ax.tick_params(axis='x', labelrotation=45)
        ax.plot(dates, df['AQI'].values)

    def drawBackground(self, ax: Axes, worstLevelRow):
        background = 0.2
        for row in range(worstLevelRow + 1):
            currRange = self.aqiDict.aqi[row]
            currColor = self.aqiDict.color[row]
            ax.axhspan(currRange[0], currRange[1],
                       facecolor=currColor, alpha=background)
            if (row < worstLevelRow):
                ax.axhline(currRange[1], color=currColor, alpha=0.5)

    def setFrame(self, ax: Axes, *args):
        ax.spines['top'].set_color(*args)
        ax.spines['bottom'].set_color(*args)
        ax.spines['left'].set_color(*args)
        ax.spines['right'].set_color(*args)
