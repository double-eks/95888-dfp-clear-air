import os

os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"

import copy
import io
import zipfile

import matplotlib.dates as mdates
import pandas as pd
import requests
from matplotlib import gridspec
from matplotlib import pyplot as plt
from matplotlib.axes import Axes


class AirQualitySys():
    def __init__(self) -> None:
        self.url = 'https://aqs.epa.gov/aqsweb/airdata/daily_aqi_by_cbsa_{}.zip'
        self.yrBulk = []
        self.initLegendDf()

    def requestSingleYr(self, yr: int, city: str, state: str):
        # Request zip file
        url = self.url.format(yr)
        response = requests.get(url)
        zippedFile = zipfile.ZipFile(io.BytesIO(response.content))
        csvFilename = zippedFile.namelist()[0]
        csvFile = zippedFile.open(csvFilename)
        df = pd.read_csv(csvFile)
        csvFile.close()
        zippedFile.close()
        # Clean dataframe
        df = df.loc[df['CBSA'] == f'{city}, {state}', :]
        df['Date'] = pd.to_datetime(df['Date'])
        # Exculde 366
        mmyy = df['Date'].dt.strftime('%m%d')
        if (len(df.index) == 366):
            df = df.loc[mmyy != '0229', :]
        # Pre-statistic
        df = df.sort_values('Date')
        df = df.set_index('Date')

        df['Level'] = [self.palette.index[self.palette.Category == category][0]
                       for category in df.Category]
        df['Month'] = df.index.month
        df['Good Days'] = [1 if (int(aqi) <= 50) else 0 for aqi in df['AQI']]
        df['Cum Days'] = df['Good Days'].cumsum()
        return df

    def initLegendDf(self):
        result = {
            'Color': ['#00e400', '#ffff00', '#ff7e00', '#ff0000', '#8f3f97', '#7e0023'],
            'Monochrome': ['#FFDCC2', '#FFC599', '#DA7E37',
                           '#C06722', '#8F3E00', '#713200'],
            'Bottom': [0, 50, 100, 150, 200, 300],
            'Cap': [50, 100, 150, 200, 300, 500],
            'Category': ['Good', 'Moderate', 'Unhealthy for Sensitive Groups',
                         'Unhealthy', 'Very Unhealthy', 'Hazardous'],
            'Level': [i for i in range(1, 7)],
        }
        df = pd.DataFrame(result)
        self.palette = df.set_index('Level')

    def categorizeAQI(self, aqiDf: pd.DataFrame):
        levelDf = aqiDf.copy()
        for col in aqiDf.columns:
            for index in aqiDf.index:
                # print(col, index)
                currAQI = aqiDf[col][index]
                if (currAQI > 0):
                    if (currAQI <= 200):
                        levelDf[col][index] = currAQI // 50 + 1
                    elif (currAQI <= 300):
                        levelDf[col][index] = 5
                    else:
                        levelDf[col][index] = 6
        return levelDf

    def drawBackground(self, ax: Axes, worstLevelRow):
        background = 0.2
        for row in range(worstLevelRow + 1):
            currRange = self.aqiDict.aqi[row]
            currColor = self.aqiDict.color[row]
            ax.axhspan(currRange[0], currRange[1],
                       facecolor=currColor, alpha=background)
            if (row < worstLevelRow):
                ax.axhline(currRange[1], color=currColor, alpha=0.5)


def setFrame(ax: Axes, *args):
    ax.spines['top'].set_color(*args)
    ax.spines['bottom'].set_color(*args)
    ax.spines['left'].set_color(*args)
    ax.spines['right'].set_color(*args)


# ============================================================================ #
# Figure 1 - Air Quality in A Year
# ============================================================================ #


def aqiTrackerByYear(yrDf: pd.DataFrame, **kwargs):
    fig = plt.figure(tight_layout=True)
    fig.set_size_inches(8, 6)
    gs = gridspec.GridSpec(2, 2)

    dailyAqiAx = fig.add_subplot(gs[:1, :])
    cumDayAx = fig.add_subplot(gs[1:, :])

    dailyAqiPlot(dailyAqiAx, yrDf['AQI'])
    cumGoodDayPlot(cumDayAx, yrDf['Cum Days'])

    dailyAqiAx.legend(ncol=2, fontsize=8, loc='upper left')
    cumDayAx.legend(fontsize=8, loc='upper left')
    dailyAqiAx.set_ylabel('Daily AQI', **kwargs)
    cumDayAx.set_ylabel('Cumulative Days', **kwargs)
    dailyAqiAx.set_xlabel(f'Air Quality Annual Trend', **kwargs)
    cumDayAx.set_xlabel(f'Cumulative Good AQI Days (AQI<50)', **kwargs)
    return fig


def dailyAqiPlot(ax: Axes, sAQI: pd.Series):
    moving = 7
    lagging = 14
    movingAvg = sAQI.rolling(window=moving).mean()
    laggingAvg = sAQI.rolling(window=lagging).mean()
    avgMax = (movingAvg.max() // 50 + 1) * 50

    ax.grid(True, linestyle='dotted')
    ax.plot(sAQI.index, laggingAvg, linewidth=10, alpha=0.3,
            label=f'{lagging}-lagging-day moving average', color='gray')
    ax.plot(sAQI.index, movingAvg, linewidth=3, alpha=0.8,
            label=f'{moving}-day moving average', color='deepskyblue')
    ax.axhline(avgMax, 0, 1, linestyle='dashed',
               label='Worst cap of moving average', color='#ff7e00')
    ax.plot(sAQI, linewidth=1.2, label=sAQI.index.year[0],
            color='steelblue')

    yLimEnd = (sAQI.max() // 50 + 1) * 50
    ax.set_ylim((0, yLimEnd))
    fmtDateAxis(ax, sAQI)


def cumGoodDayPlot(ax: Axes, sCumDay: pd.Series):
    interval = 50
    sumDay = sCumDay.max()
    breakPoint = sumDay // interval * interval
    goodDays = [day for day in range(0, breakPoint, interval)]
    badDays = [day for day in range(breakPoint, 365, interval)]
    dayTicks = copy.copy(goodDays)
    dayTicks.extend(badDays[1:])
    dayTicks.extend([sumDay, 365])

    ax.grid(True, linestyle='dotted')
    ax.fill_between(sCumDay.index, sumDay, 365, alpha=0.1,
                    color='#ff7e00')
    ax.axhline(sumDay, 0, 1, color='#ff7e00')
    ax.plot(sCumDay, linewidth=3,
            label='Cumulative Good Days (AQI<50)', color='steelblue')

    ax.set_ylim((0, 365))
    ax.set_yticks(dayTicks)
    fmtDateAxis(ax, sCumDay)


def fmtDateAxis(ax: Axes, s: pd.Series):
    dateLim = (s.index[0], s.index[-1])
    ax.set_xlim(dateLim)
    ax.tick_params(axis='both', labelsize=8)
    ax.tick_params(axis='x', rotation=15)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
