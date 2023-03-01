import os

os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"

import logging
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


def introPage():
    brief = '{}\t{}'.format(console.location,
                            console.today.strftime('%a, %b %d, %Y, %I:%M %p'))
    aqiIntroTag = webScraping(airNowGov).find(
        'div', attrs={'class': 'container related-announcements-container pull-left'})
    aqiIntro = aqiIntroTag.text.strip()
    console.header('WELCOME to ClearAir for Better Asthma Management')
    console.header(brief, sub=True)
    console.para(aqiIntro, preIndent=True)
    # console.requesting(f'AirNow API for a quick view of AQI in {console.city}')
    current = airNowAPI.getCurrByZip(console.zip)
    forecasting = airNowAPI.getForecastByZip(console.zip,
                                             console.today + pd.Timedelta(days=1))
    columns = ['Date', 'Data Type', 'Pollutant', 'AQI', 'Level']
    masterTable = pd.concat([current[columns], forecasting[columns]])
    # console.requested()
    console.table(masterTable)


def homepage(new: bool = False):
    return


if __name__ == "__main__":
    console = Console()

    airNowGov = 'https://www.airnow.gov/aqi/'
    airNowAPI = AirNow()

    introPage()
    