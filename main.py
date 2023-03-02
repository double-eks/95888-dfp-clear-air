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

def findSubItem(tag: Tag, itemTag: str, itemName: str) -> Tag:
    for subTag in tag.find_all_next(itemTag):
        if (subTag.text.strip().lower() == itemName.lower()):
            return subTag


def isValidText(text: str):
    text = text.strip()
    if (len(text) <= 1) or (not text[0].isalnum()):
        return False
    else:
        return True


# ============================================================================ #
# Asthma Stats & Triggers
# ============================================================================ #


def asthmaStatsPage():
    console.header('Asthma Statistics © CDC')
    console.header('Asthma FastFacts ', sub=True)
    fastFactsPage()
    console.separator()
    console.header('Asthma Statistical Charts', sub=True)
    asthmaAPI.trend()
    console.checkpoint('')
    asthmaAPI.demography()
    homepage()


def fastFactsPage():
    cardTag = 'div'
    attr = 'class'
    cardClass = 'card mb-3'
    cardHeaderClass = 'bg-primary'
    for card in nchc.find_all(cardTag, attrs={attr: cardClass}):
        header = card.find_next('div')
        if (cardHeaderClass in header.get(attr)):
            console.title(header.text.strip())
            for fact in card.find_all('li'):
                console.bullet(fact.text.strip())


def asthmaTriggerPage():
    console.header('Asthma Triggers © EPA')
    asthmaIntro = ''
    for line in epa.find('article').find_all('p'):
        if (len(line.attrs) == 0):
            asthmaIntro = line.string.strip()
            break
    console.para(asthmaIntro, preIndent=True)
    navTrigger()


def navTrigger():
    triggersListTag = epa.find('article').find('ul')
    triggersList = [s for s in triggersListTag.stripped_strings]
    console.multiChoice(triggersList)
    response = console.prompt(answers=triggersList, menuNavOn=True)
    print(response)
    if (response.lower() == 'h'):
        homepage()
    else:
        i = int(response) - 1
        triggerReport(triggersListTag, triggersList, i)


def triggerReport(triggersListTag: Tag, triggersList: list, triggerIndex: int):
    """
    Generate report for the selected trigger, including About and Actions
    Args:
        triggersListTag (Tag): tag of the trigger ul
        triggersList (list): storing trigger options
        triggerIndex (int): user response - 1 as the index
    """
    header = findSubItem(triggersListTag, 'h2', triggersList[triggerIndex])
    about, action = header.find_all_next('h3', limit=2)
    actionDetail = about.find_next('ul')
    # Report the About part
    console.title(about.text)
    for tag in about.find_all_next():
        if ('h' in tag.name):
            break
        if (('p' or 'li') in tag.name):
            if (isValidText(tag.text)):
                console.para(tag.text.strip())
    # Report the Action You Can Take part
    console.title(action.text)
    for detail in (actionDetail.stripped_strings):
        if (isValidText(detail)):
            console.bullet(detail)
    # Show options
    console.separator()
    navTrigger()


def homepage(new: bool = False):
    return


if __name__ == "__main__":
    console = Console()

    airNowGov = 'https://www.airnow.gov/aqi/'
    airNowAPI = AirNow()

    # Web scraping url
    epaURL = 'https://www.epa.gov/asthma/asthma-triggers-gain-control'
    nchcURL = 'https://www.cdc.gov/nchs/fastats/asthma.htm'
    epa = webScraping(epaURL)
    nchc = webScraping(nchcURL)

    introPage()
    