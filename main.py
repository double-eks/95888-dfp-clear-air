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

import copy
import re
from urllib.request import urlopen

import matplotlib.pyplot as plt
import pandas as pd
import progressbar
from bs4 import BeautifulSoup, Tag

from airnow import AirNow
from airqualitysys import AirQualitySys, aqiTrackerByYear
from asthmaindicator import AsthmaIndicator
from console import Console, ZipCityState

# ============================================================================ #
# Home
# ============================================================================ #


def webScraping(url: str) -> BeautifulSoup:
    domain = re.search(r'(?<=https://www.)[^/]*(?=/)', url).group()
    console.loading(domain)
    html = urlopen(url)
    return BeautifulSoup(html.read(), "lxml")


def prologue():
    # Scraping message
    asthmaIntro = ''
    for line in epa.find('article').find_all('p'):
        if (len(line.attrs) == 0):
            asthmaIntro = line.string.strip()
            break
    # Set fastfacts scraping parameters
    cardTag = 'div'
    attr = 'class'
    cardClass = 'card mb-3'
    cardHeaderClass = 'bg-primary'
    # UI output
    console.para(asthmaIntro, preIndent=True)
    console.chapter('US Asthma FastFacts')
    # Asthma FastFacts
    for card in nchc.find_all(cardTag, attrs={attr: cardClass}):
        header = card.find_next('div')
        if (cardHeaderClass in header.get(attr)):
            console.title(header.text.strip())
            for fact in card.find_all('li'):
                console.bullet(fact.text.strip())
    print('')
    response = console.prompt(question='your 5-digit ZIP Code',
                              answerPattern=r'\d{5}')
    setUser = ZipCityState(response)
    return setUser


# ============================================================================ #
# Feature 1 - Airnow AQI
# ============================================================================ #


def airnowPage(firstBrowser: bool = False):
    if (firstBrowser):
        aqiIntroTag = airnowPortal.find(
            'div', attrs={'class': 'container related-announcements-container pull-left'})
        aqiIntro = aqiIntroTag.text.strip()
        console.para(aqiIntro, postIndent=True)
    else:
        console.divider()
    features = [
        "Current AQI Brief of My City",
        "Past AQI Record of My City\n",
        'Current AQI brief of Another City',
        'Past AQI Record of Another City',
    ]
    # UI output
    console.menuChoices('Local Air Quality Information',
                        features, menuLevel=2)
    response = console.prompt(answers=features, menuNavOn=True)
    if (response.lower() == 'h'):
        homepage()
    elif (response == '1'):
        currentAQI()
    elif (response == '2'):
        historicAQI()
        return
    elif (response == '3'):
        currentAQI(anotherCity=True)
    elif (response == '4'):
        historicAQI(anotherCity=True)


def currentAQI(anotherCity: bool = False):
    if (anotherCity):
        response = console.prompt(question='your 5-digit ZIP Code',
                                  answerPattern=r'\d{5}')
        locator = ZipCityState(response)
    else:
        locator = user
    console.loading(f'AirNow for AQI Brief of {locator.city}')
    current = airnowAPI.getCurrByZip(locator.zip)
    forecasting = airnowAPI.getForecastByZip(locator.zip,
                                             console.today + pd.Timedelta(days=1))
    console.requested()
    console.title(locator.location, split=True)
    if (isinstance(current, pd.DataFrame)) and \
       (isinstance(forecasting, pd.DataFrame)):
        columns = ['Date', 'Data Type', 'Pollutant', 'AQI', 'Level']
        masterTable = pd.concat([current[columns], forecasting[columns]])
        console.table(masterTable)
    airnowPage()


def historicAQI(anotherCity: bool = False):
    if (anotherCity):
        response = console.prompt(question='your 5-digit ZIP Code',
                                  answerPattern=r'\d{5}')
        locator = ZipCityState(response)
    else:
        locator = user
    response = console.prompt(
        question="yyyy-mm-dd (don't forget dash line) to check historical AQI of a specific day",
        answerPattern=r'^\d{4}-\d{2}-\d{2}$', menuNavOn=True, quitButtonOn=False)
    if (response.lower() == 'h'):
        homepage()
    else:
        console.loading(
            f"AirNow for {locator.city} AQI on {response}")
        requestedDay = airnowAPI.getHistByZip(locator.zip, response)
        if (isinstance(requestedDay, pd.DataFrame)):
            infoColumns = ['Date', 'Data Type', 'Pollutant', 'AQI', 'Level']
            console.title(locator.location, split=True)
            console.table(requestedDay.loc[:, infoColumns])
        airnowPage()


# ============================================================================ #
# Feature 2 - Air Quality Stats
# ============================================================================ #

def airstatsPage(firstBrowser: bool = False):
    if (firstBrowser):
        requestAQS()
    else:
        console.divider()
    features = [
        "Annual Air Quality Tracker",
        'Time Series Air Quality Plot',
        "Multiscale Grouped Bar Chat",
        'AQI Calendar Heat Map',
    ]
    # UI output
    console.menuChoices('Air Quality Analysis Suite',
                        features, menuLevel=2)
    response = console.prompt(answers=features, menuNavOn=True)
    if (response.lower() == 'h'):
        homepage()
    elif (response == '1'):
        console.para('\n\n!!!!!\tDEMO LIMITS - please pick up one year from 2016-2021 '
                     'for demo as other 4-digit input may raise error')
        response = console.prompt(
            question="yyyy to generate an annual trend plot",
            answerPattern=r'^\d{4}$', quitButtonOn=False)
        yr = response
        i = airYrContainer.index(yr)
        yrDf = airDatabase[i]
        aqiTrackerByYear(yrDf, yr, user.city, user.state,
                         fontweight='bold', fontsize=10)
    # elif (response == '2'):
    #     historicAQI()
    #     return
    elif (response == '3'):
        multiGroupBar(user.city, user.state)
    # elif (response == '4'):
    #     historicAQI(anotherCity=True)


def multiGroupBar(city: str, state: str):

    return


def requestAQS(start: int = 2010, end: int = 2021):
    if (len(airDatabase) == 0):
        widget = copy.copy(console.widget)
        widget[0] = widget[0].format('EPA AQS')
        for yr in progressbar.progressbar(range(start, end + 1),
                                          widgets=widget, redirect_stdout=True):
            df = aqsAPI.requestSingleYr(yr, user.city, user.state)
            airDatabase.append(df)
            airYrContainer.append(str(yr))


# ============================================================================ #
# Feature 3 & 4 - Asthma Stats & Triggers
# ============================================================================ #


def asthmaStatsPage():
    console.loading(f'CDC API for asthma indicators in {user.state}')
    asthmaAPI = AsthmaIndicator(user.state)
    console.requested()
    asthmaAPI.trend()
    console.checkpoint('More demographic statistics...')
    asthmaAPI.demography()
    homepage()


def triggerPage(firstBrowser: bool = False):
    if (not firstBrowser):
        console.divider()
    triggersListTag = epa.find('article').find('ul')
    triggersList = [s for s in triggersListTag.stripped_strings]

    console.menuChoices('Most Common Triggers',
                        triggersList, menuLevel=2)
    response = console.prompt(answers=triggersList, menuNavOn=True)
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
    header = ''
    for subTag in triggersListTag.find_all_next('h2'):
        if (subTag.text.strip().lower() == triggersList[triggerIndex].lower()):
            header = subTag
            break
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
    triggerPage()


def isValidText(text: str):
    text = text.strip()
    if (len(text) <= 1) or (not text[0].isalnum()):
        return False
    else:
        return True

# ============================================================================ #
# Main
# ============================================================================ #


def homepage(firstBrowser: bool = False):
    # Feature menu
    features = [
        "Is air quality good today? Know what you're breathing in real-time",
        'How about the past and the future? Dig into air quality data',
        'Who does asthma really affect? Unlock the demographic insights',
        'Stay informed about your asthma triggers and learn how to avoid them'
    ]
    # UI output
    if (firstBrowser):
        console.chapter(
            'WELCOME to AirWise Asthma',
            console.today.strftime('%a, %b %d, %Y, %I:%M %p'),
            user.location,
        )
    else:
        console.divider()
    console.menuChoices('For Better Asthma Management', features)
    response = console.prompt(answers=features)
    if (response == '1'):
        console.chapter('Air Quality Index (AQI) Powered by CDC AirNow')
        airnowPage(firstBrowser=True)
    elif (response == '2'):
        console.chapter('Air Quality Analysis & Statistics')
        airstatsPage(firstBrowser=True)
        return
    elif (response == '3'):
        console.chapter('Significant Asthma Statistics')
        asthmaStatsPage()
    elif (response == '4'):
        console.chapter('Asthma Triggers © EPA')
        triggerPage(firstBrowser=True)


if __name__ == "__main__":

    # Initialize objects
    console = Console()
    airnowAPI = AirNow()
    aqsAPI = AirQualitySys()
    airDatabase = []
    airYrContainer = []
    aqiPalette = aqsAPI.palette

    # Request web scraping
    epaURL = 'https://www.epa.gov/asthma/asthma-triggers-gain-control'
    nchcURL = 'https://www.cdc.gov/nchs/fastats/asthma.htm'
    airNowGov = 'https://www.airnow.gov/aqi/'
    epa = webScraping(epaURL)
    nchc = webScraping(nchcURL)
    airnowPortal = webScraping(airNowGov)

    # Deploy
    # user = prologue()
    user = ZipCityState('15213')
    airstatsPage(True)
    # homepage(firstBrowser=True)
    plt.close('all')
