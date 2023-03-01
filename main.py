import os

os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"

import re
from datetime import timedelta
from urllib.request import urlopen

import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, Tag
from matplotlib.axes import Axes

from airnow import AirNow, EpaAqs
from asthmaindicator import cdcAPI
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
    gs = gridspec.GridSpec(3, 3)

    dailyAqiAx = fig.add_subplot(gs[0, :])
    cumDayAx = fig.add_subplot(gs[1, 0])
    pollutantAx = fig.add_subplot(gs[2, 1])
    tileAx = fig.add_subplot(gs[2, 2])

    dailyAqPlot(dailyAqiAx, cumDayAx)
    # levelBarAx(df, levelBarAx)
    # monthBarAx(df, monthBarAx)
    return


def dailyAqPlot(ax1: Axes, ax2: Axes):
    dfs = aqsAPI.dfList
    latestDf = dfs[-1]
    halfDF = pd.concat(dfs[(len(dfs) // 2):])
    mergedDF = pd.concat(dfs)
    averageAQI = halfDF.groupby('Day')['AQI'].mean(numeric_only=True)
    periodMax = mergedDF.groupby('Day')['AQI'].max(numeric_only=True)
    periodMin = mergedDF.groupby('Day')['AQI'].min(numeric_only=True)

    ax1.grid(True, axis='y', linestyle='dotted')
    ax1.fill_between(latestDf['Date'], periodMin, periodMax, alpha=0.3,
                     color='lightgray')
    ax1.plot(latestDf['Date'], averageAQI, linewidth=4, alpha=0.3)
    ax1.plot(latestDf['Date'], latestDf['AQI'], label='2022')
    ax1.tick_params(axis='both', labelsize=8, color='gray')
    ax1.tick_params(axis='x', rotation=30)
    ax1.set_xlim((latestDf['Date'].min()), (latestDf['Date'].max()))
    ax1.set_ylabel('Daily AQI Value', fontweight='bold')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    aqsAPI.yAxisByAQI(ax1, latestDf['AQI'])
    plt.show()


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
    plt.close('all')
