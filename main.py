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
from console import Console

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
    console.para(asthmaIntro, preIndent=True, postIndent=True)
    console.checkpoint('Here are some asthma FastFacts...')
    # Asthma FastFacts
    for card in nchc.find_all(cardTag, attrs={attr: cardClass}):
        header = card.find_next('div')
        if (cardHeaderClass in header.get(attr)):
            console.title(header.text.strip())
            for fact in card.find_all('li'):
                console.bullet(fact.text.strip())
    print('')
    console.checkpoint()


# ============================================================================ #
# Feature 1 - Airnow AQI
# ============================================================================ #


def airnowPage():
    # Intro para
    aqiIntroTag = airnowPortal.find(
        'div', attrs={'class': 'container related-announcements-container pull-left'})
    aqiIntro = aqiIntroTag.text.strip()
    console.para(aqiIntro, postIndent=True)
    # Current and Forecasting AQI
    console.loading(f'AirNow for a quick view of AQI in {console.city}')
    current = airnowAPI.getCurrByZip(console.zip)
    forecasting = airnowAPI.getForecastByZip(console.zip,
                                             console.today + pd.Timedelta(days=1))
    if (isinstance(current, pd.DataFrame)) and \
       (isinstance(forecasting, pd.DataFrame)):
        columns = ['Date', 'Data Type', 'Pollutant', 'AQI', 'Level']
        masterTable = pd.concat([current[columns], forecasting[columns]])
        console.requested()
        console.table(masterTable)
    # Ask for historical data
    historicAQI()


def historicAQI():
    response = console.prompt(
        question="yyyy-mm-dd (don't forget dash line) to check historical AQI of a specific day",
        answerPattern=r'^\d{4}-\d{2}-\d{2}$', menuNavOn=True, quitButtonOn=False)
    if (response.lower() == 'h'):
        homepage()
    else:
        console.loading(
            f"AirNow for {console.city} AQI on {response}")
        requestedDay = airnowAPI.getHistByZip(console.zip, response)
        if (isinstance(requestedDay, pd.DataFrame)):
            infoColumns = ['Date', 'Data Type', 'Pollutant', 'AQI', 'Level']
            console.table(requestedDay.loc[:, infoColumns])
        historicAQI()


# ============================================================================ #
# Feature 2 - Air Quality Stats
# ============================================================================ #


def requestAQS(start: int = 2010, end: int = 2021):
    widget = copy.copy(console.widget)
    widget[0] = widget[0].format('EPA AQS')
    dfList = []
    for yr in progressbar.progressbar(range(start, end + 1),
                                      widgets=widget, redirect_stdout=True):
        df = aqsAPI.requestSingleYr(yr, console.city, console.state)
        dfList.append(df)
    return pd.concat(dfList)


def aqiStatsPage():
    dfs = requestAQS(start=2021)
    yrDf = dfs.loc[(dfs.index.year == 2021), :]
    yr = 2021
    aqiTrackerByYear(yrDf, yr, console.city, console.state,
                     fontweight='bold', fontsize=10)
    return


# ============================================================================ #
# Feature 3 - Asthma Stats & Triggers
# ============================================================================ #


def asthmaStatsPage():
    asthmaAPI.trend()
    console.checkpoint('More demographic statistics...')
    asthmaAPI.demography()
    homepage()


# ============================================================================ #
# Feature 4 - Trigger Introduction
# ============================================================================ #


def navTrigger():
    # UI output
    triggersListTag = epa.find('article').find('ul')
    triggersList = [s for s in triggersListTag.stripped_strings]
    console.para('Most common triggers:')
    console.multiChoice(triggersList)
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
    console.separator()
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


def isValidText(text: str):
    text = text.strip()
    if (len(text) <= 1) or (not text[0].isalnum()):
        return False
    else:
        return True

# ============================================================================ #
# Main
# ============================================================================ #


def homepage(new: bool = False):
    # Feature menu
    features = [
        "Is air quality today good? Know what you're breathing in real-time",
        'How about the past and the future? Dig into the AQI data',
        'Who does asthma really affect? Unlock the demographic insights',
        'Stay informed about your asthma triggers and learn how to avoid them'
    ]
    brief = '{}\t{}'.format(console.location,
                            console.today.strftime('%a, %b %d, %Y, %I:%M %p'))
    # UI output
    if (new):
        console.header('WELCOME to AirWise Asthma')
    else:
        console.separator()
    console.header(brief, sub=True)
    console.multiChoice(features)
    response = console.prompt(answers=features)
    # Menu
    if (response == '1'):
        console.header('Air Quality Index from CDC AirNow')
        airnowPage()
    elif (response == '2'):
        console.header('AQI Time Series Analysis')
        aqiStatsPage()
        return
    elif (response == '3'):
        console.header('Significant Asthma Statistics')
        asthmaStatsPage()
    elif (response == '4'):
        console.header('Asthma Triggers © EPA')
        navTrigger()


if __name__ == "__main__":
    console = Console()

    # Web scraping url
    epaURL = 'https://www.epa.gov/asthma/asthma-triggers-gain-control'
    nchcURL = 'https://www.cdc.gov/nchs/fastats/asthma.htm'
    airNowGov = 'https://www.airnow.gov/aqi/'
    epa = webScraping(epaURL)
    nchc = webScraping(nchcURL)
    airnowPortal = webScraping(airNowGov)

    # API requesting
    console.loading(f'CDC API for asthma indicators in {console.state}')
    asthmaAPI = AsthmaIndicator(console.state)
    airnowAPI = AirNow()
    aqsAPI = AirQualitySys()
    aqiPalette = aqsAPI.palette

    # Deploy
    # prologue()
    homepage(True)
    plt.close('all')
