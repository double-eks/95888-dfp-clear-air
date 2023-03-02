'''
95-888 Data Focused Python
Spring 2023 Mini 3

Group 9: AirWise 
Xiao Xu
xiaoxu@andrew.cmu.edu

ps: oringal project name: ClearAir
'''

import os

# logging.basicConfig(level=logging.DEBUG)

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
from console import Console, Menu, ZipCityState

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
    for line in epaBS.find('article').find_all('p'):
        if (len(line.attrs) == 0):
            asthmaIntro = line.string.strip()
            break
    # Set fastfacts scraping parameters
    cardTag = 'div'
    attr = 'class'
    cardClass = 'card mb-3'
    cardHeaderClass = 'bg-primary'
    # UI output asthma FastFacts
    print('')
    console.para(asthmaIntro)
    print('')
    console.checkpoint('Some US Asthma FastFacts ©EPA ...')
    for card in nchcBS.find_all(cardTag, attrs={attr: cardClass}):
        header = card.find_next('div')
        if (cardHeaderClass in header.get(attr)):
            console.title(header.text.strip())
            for fact in card.find_all('li'):
                console.bullet(fact.text.strip())
    # Initialize user zip code
    response = console.prompt(question='your 5-digit ZIP Code',
                              answerPattern=r'\d{5}')
    setUser = ZipCityState(response)
    return setUser


# ============================================================================ #
# Feature 1 - Airnow AQI
# ============================================================================ #


def airnowPage(firstBrowser: bool = False):
    if (firstBrowser):
        aqiIntroTag = airnowPortalBS.find(
            'div', attrs={'class': 'container related-announcements-container pull-left'})
        aqiIntro = aqiIntroTag.text.strip()
        print('')
        console.para(aqiIntro)
    airnowMenu.content(firstBrowser)
    response = console.prompt(answers=airnowMenu.features, menuNavOn=True)
    if (response.lower() == 'h'):
        homepage()
    else:
        airnowMenu.checked.add(int(response))
        if (response == '1'):
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
    airstatsMenu.content(firstBrowser)
    response = console.prompt(answers=airstatsMenu.features, menuNavOn=True)
    if (response.lower() == 'h'):
        homepage()
    else:
        airstatsMenu.checked.add(int(response))
        if (response == '1'):
            console.para('\n\n!!!!!\tDEMO LIMITS - please pick up one year '
                         'from 2016-2021 for demo as other 4-digit input may '
                         'raise error')
            response = console.prompt(
                question="yyyy to generate an annual trend plot",
                answerPattern=r'^\d{4}$', quitButtonOn=False)
            yr = response
            i = airYrContainer.index(yr)
            yrDf = airDatabase[i]
            aqiTrackerByYear(yrDf, yr, user.city, user.state,
                             fontweight='bold', fontsize=10)
        elif (response == '2'):
            homepage()
        elif (response == '3'):
            multiGroupBar(user.city, user.state)
        elif (response == '4'):
            homepage()


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
    triggersListTag = epaBS.find('article').find('ul')
    triggersList = [s for s in triggersListTag.stripped_strings]
    if (triggerMenu.features == []):
        triggerMenu.features = triggersList
    triggerMenu.content(firstBrowser)
    response = console.prompt(answers=triggersList, menuNavOn=True)
    if (response.lower() == 'h'):
        homepage()
    else:
        triggerMenu.checked.add(int(response))
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
    if (firstBrowser):
        console.chapter(
            'WELCOME to AirWise',
            console.today.strftime('%a, %b %d, %Y, %I:%M %p'),
            user.location,
        )
    else:
        console.title(message='', split=True)
    homeMenu.content(firstBrowser)
    response = console.prompt(answers=homeMenu.features)
    homeMenu.checked.add(int(response))
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
        console.chapter('Asthma Triggers ©EPA')
        triggerPage(firstBrowser=True)


def initMenuFeatures():
    mainFeatures = [
        "Is air quality good today? Know what you're breathing in real-time",
        'How about the past and the future? Dig into air quality data',
        'Who does asthma really affect? Unlock the demographic insights',
        'Stay informed about your asthma triggers and learn how to avoid them'
    ]
    airnowFeatures = [
        "Current AQI Brief of My City",
        "Past AQI Record of My City\n",
        'Current AQI brief of Another City',
        'Past AQI Record of Another City',
    ]
    aqsFeatures = [
        "Annual Air Quality Tracker",
        'Time Series Air Quality Plot',
        "Multiscale Grouped Bar Chat",
        'AQI Calendar Heat Map',
    ]
    return mainFeatures, airnowFeatures, aqsFeatures


if __name__ == "__main__":

    # Initialize API
    console = Console()
    airnowAPI = AirNow()
    aqsAPI = AirQualitySys()
    airDatabase = []
    airYrContainer = []
    aqiPalette = aqsAPI.palette

    # Initialize UI
    mainFeatures, airnowFeatures, aqsFeatures = initMenuFeatures()
    homeMenu = Menu(name='AirWise for Better Asthma Management',
                    features=mainFeatures)
    airnowMenu = Menu(name='Local Air Quality Information',
                      features=airnowFeatures, menuLevel=2)
    airstatsMenu = Menu(name='Air Quality Analysis Suite',
                        features=aqsFeatures, menuLevel=2)
    triggerMenu = Menu(name='Most Common Triggers',
                       features=[], menuLevel=2)
    # Request web scraping
    epaURL = 'https://www.epa.gov/asthma/asthma-triggers-gain-control'
    nchcURL = 'https://www.cdc.gov/nchs/fastats/asthma.htm'
    airNowGov = 'https://www.airnow.gov/aqi/'
    epaBS = webScraping(epaURL)
    nchcBS = webScraping(nchcURL)
    airnowPortalBS = webScraping(airNowGov)

    # Deploy
    # user = prologue()
    user = ZipCityState('15213')
    # airstatsPage(True)
    homepage(firstBrowser=True)

    plt.close('all')
