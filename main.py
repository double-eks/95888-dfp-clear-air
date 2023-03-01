import os

os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"

import re
from urllib.request import urlopen

import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import pandas as pd
from bs4 import BeautifulSoup, Tag
from matplotlib.axes import Axes

from airnow import AirNow, EpaAqs
from console import Console


def webScraping(url: str) -> BeautifulSoup:
    domain = re.search(r'(?<=https://www.)[^/]*(?=/)', url).group()
    console.loading(domain)
    html = urlopen(url)
    return BeautifulSoup(html.read(), "lxml")


def aqiVizPage():
    console.header('AQI Visualization')

    aqiTracker()
    # ax.set_xlabel('Dates')
    # aqsAPI.drawTrendPlot(ax, yrDf)
    # homepage()


def aqiTracker():
    fig = plt.figure(tight_layout=True)
    fig.set_size_inches(8, 8)
    gs = gridspec.GridSpec(3, 4)

    dailyAqiAx = fig.add_subplot(gs[0, :])
    cumDayAx = fig.add_subplot(gs[1, :])
    pollutantAx = fig.add_subplot(gs[2, :2])
    tileAx = fig.add_subplot(gs[2, 2:])

    dailyAqiPlot(dailyAqiAx)
    cumGoodDayPlot(cumDayAx)
    # levelBarAx(df, levelBarAx)
    # monthBarAx(df, monthBarAx)
    return


def dailyAqiPlot(ax: Axes):
    df = aqsAPI.dfList[-1]
    movingAvg = df['AQI'].rolling(window=7).mean()
    biWeekAvg = df['AQI'].rolling(window=14).mean()
    dateLim = (df['Date'].min()), (df['Date'].max())
    ax.grid(True, linestyle='dotted')
    ax.plot(df['Date'], movingAvg)
    ax.plot(df['Date'], biWeekAvg)
    ax.plot(df['Date'], df['AQI'])
    aqsAPI.yAxisByAQI(ax, df['AQI'])
    fmtSharingAx(ax, dateLim)
    return
    # ax.set_ylabel('Daily AQI Value', fontweight='bold')


def cumGoodDayPlot(ax: Axes):
    df = aqsAPI.dfList[-1]
    dateLim = (df['Date'].min()), (df['Date'].max())
    ax.grid(True, linestyle='dotted')
    ax.plot(df['Date'], df['CumDays'])
    yrDays = [i for i in range(0, 360, 30)]
    yrDays.append(365)
    ax.set_ylim((0, 365))
    ax.set_yticks(yrDays)
    fmtSharingAx(ax, dateLim)
    return


def fmtSharingAx(ax: Axes, dateLim: tuple):
    ax.tick_params(axis='both', labelsize=8, color='gray')
    ax.tick_params(axis='x', rotation=30)
    ax.set_xlim(dateLim)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))


def levelCountBar(df: pd.DataFrame, ax: Axes):
    return


def monthCumBar(df: pd.DataFrame, ax: Axes):
    return


def homepage(new: bool = False):
    return


if __name__ == "__main__":

    console = Console()

    console.loading('EPA Air Quality System')
    aqsAPI = EpaAqs(console.city, console.state)

    aqiVizPage()

    plt.show()
    plt.close('all')
