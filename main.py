
import logging
import os
import re
from datetime import timedelta
from urllib.request import urlopen

os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, Tag
from sodapy import Socrata

from airnow import AirNow
from console import Console
from trend import cdcAPI


def webScraping(url: str) -> BeautifulSoup:
    domain = re.search(r'(?<=https://www.)[^/]*(?=/)', url).group()
    console.loading(domain)
    html = urlopen(url)
    bs = BeautifulSoup(html.read(), "lxml")
    return bs


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


def summarizeOneLine(tag: Tag):
    text = []
    for s in tag.text.split('\n'):
        s = s.strip()
        if (s != '') and (not s.isspace()):
            text.append(s)
    return text


def introPage():
    brief = [console.location,
             console.today.strftime('%a, %b %d, %Y, %I:%M %p')]
    aqiIntroTag = webScraping(airNowGov).find(
        'div', attrs={'class': 'container related-announcements-container pull-left'})
    aqiIntro = aqiIntroTag.text.strip()
    console.header('WELCOME to ClearAir for Better Asthma Management')
    console.subHeader([brief])
    console.para(aqiIntro)
    console.loading(f'AirNow API for a quick view of AQI in {console.city}',
                    newLine=True)
    current = airNowAPI.getCurrByZip(console.zip)
    forecasting = airNowAPI.getForecastByZip(console.zip,
                                             console.today + pd.Timedelta(days=1))
    columns = ['Date', 'Data Type', 'Pollutant', 'AQI', 'Level']
    masterTable = pd.concat([current[columns], forecasting[columns]])
    console.checkpoint()
    console.table(masterTable)


def asthmaPage():
    console.para('Air quality is signifcant for asthma management. '
                 "Let's take a look at the asthma trend first. "
                 '\nPlease note that there will be a brief report for plot '
                 'interpration at the bottom of terminal. Check it out...')
    console.loading(f'CDC API for asthma indicators in {console.state}',
                    newLine=True)
    console.checkpoint()
    asthmaAPI.overallTrend()


def triggerPage():
    # Scrap essential info
    triggersListTag = epa.find('article').find('ul')
    triggersList = [s for s in triggersListTag.stripped_strings]
    triggerIntro = ''
    for line in epa.find('article').find_all('p'):
        if (len(line.attrs) == 0):
            triggerIntro = line.string.strip()
            break
    # Output to Console
    console.header('Asthma Triggers © EPA')
    console.para('More than 25 million people in the U.S. have asthma. '
                 'It is a long-term disease that causes your airways to become swollen and inflamed, '
                 'making it hard to breathe. There is no cure for asthma, '
                 'but it can be managed and controlled.')
    console.para(triggerIntro, preIndent=True)
    console.multiChoice(triggersList)
    # Ask for option and output to console
    for inputNum in range(len(triggersList)):
        triggerReport(triggersListTag, triggersList, inputNum)


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


def fastStatsPage():
    cardTag = 'div'
    attr = 'class'
    cardClass = 'card mb-3'
    cardHeaderClass = 'bg-primary'

    console.header('Asthma Faststats © CDC')
    for card in nchc.find_all(cardTag, attrs={attr: cardClass}):
        header = card.find_next('div')
        if (cardHeaderClass in header.get(attr)):
            console.title(header.text.strip())
            for fact in card.find_all('li'):
                console.bullet(fact.text.strip())


if __name__ == "__main__":

    # * Initialize console
    console = Console()
    logging.basicConfig(level=logging.INFO)

    # Web Scraping
    epaURL = 'https://www.epa.gov/asthma/asthma-triggers-gain-control'
    nchcURL = 'https://www.cdc.gov/nchs/fastats/asthma.htm'
    airNowGov = 'https://www.airnow.gov/aqi/'

    epa = webScraping(epaURL)
    nchc = webScraping(nchcURL)
    airNowAPI = AirNow()
    asthmaAPI = cdcAPI(console.state)

    # Deploy
    introPage()
    asthmaPage()
    console.homepage()
    # console.checkpoint
    # triggerPage()
    # console.checkpoint()
    # fastStatsPage()
