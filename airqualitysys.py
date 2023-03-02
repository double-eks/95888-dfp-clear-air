import os

os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"

import io
import zipfile

import pandas as pd
import progressbar
import requests
from matplotlib.axes import Axes


class EpaAqs():
    def __init__(self, city: str, state: str) -> None:
        self.url = 'https://aqs.epa.gov/aqsweb/airdata/daily_aqi_by_cbsa_{}.zip'
        self.initRequest(city, state)
        self.initLegendDf()

    def initRequest(self, city: str, state: str):
        dfs = []
        for yr in progressbar.progressbar(range(2010, 2022), redirect_stdout=True):
            url = self.url.format(yr)
            response = requests.get(url)
            zippedFile = zipfile.ZipFile(io.BytesIO(response.content))
            csvFilename = zippedFile.namelist()[0]
            csvFile = zippedFile.open(csvFilename)
            df = pd.read_csv(csvFile)
            csvFile.close()
            zippedFile.close()
            df = df.loc[df['CBSA'] == f'{city}, {state}', :]
            df['Date'] = pd.to_datetime(df['Date'])
            df['Day'] = df['Date'].dt.strftime('%m-%d')
            if (len(df.index) == 366):
                df = df.loc[df.Day != '02-29', :]
            df = df.sort_values('Date')
            df['Good'] = [1 if (int(aqi) <= 50) else 0
                          for aqi in df['AQI']]
            df['CumDays'] = df['Good'].cumsum()
            dfs.append(df)
        self.dfList = dfs

    def initLegendDf(self):
        result = {
            'color': ['#00e400', '#ffff00', '#ff7e00', '#ff0000', '#8f3f97', '#7e0023'],
            'range': [range(0, 50), range(50, 100), range(100, 150),
                      range(150, 200), range(200, 300), range(300, 500)],
            'category': ['Good', 'Moderate', 'Unhealthy for Sensitive Groups',
                         'Unhealthy', 'Very Unhealthy', 'Hazardous'],
            'number': [i for i in range(1, 7)]
        }
        df = pd.DataFrame(result)
        df['cap'] = [(list(levelRange)[-1] + 1)
                     for levelRange in df.range]
        self.aqiDict = df

    def yAxisByAQI(self, ax: Axes, aqiCol: pd.Series):
        ticks = [0]
        worstAQI = aqiCol.max()
        for row in self.aqiDict.index:
            levelCap = self.aqiDict.cap[row]
            levelColor = self.aqiDict.color[row]
            ticks.append(levelCap)
            # ax.axhline(y=levelCap, color=levelColor, linewidth=1, alpha=0.5)
            if (worstAQI < levelCap):
                break
        ax.set_yticks(ticks)
        ax.set_ylim((0, ticks[-1]))

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
        ax.tick_params(axis='x', labelrotation=15)
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
