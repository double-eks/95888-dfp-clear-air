'''
95-888 Data Focused Python
Spring 2023 Mini 3

Group 9: AirWise Asthma
Xiao Xu
xiaoxu@andrew.cmu.edu

ps: oringal project name: ClearAir
'''

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


def homepage(new: bool = False):
    return


'''
    features = [
        'AQI ?????',
        'Asthma Statistics',
        'Asthma Triggers',
    ]
    if (not new):
        console.separator()
    console.multiChoice(features)
    response = console.prompt(answers=features)
    if (response == '1'):
        aqiVizPage()
    elif (response == '2'):
        asthmaStatsPage()
    elif (response == '3'):
        asthmaTriggerPage()

'''

if __name__ == "__main__":

    console = Console()
