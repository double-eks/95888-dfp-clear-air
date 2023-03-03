'''
Group 9: AirWise
Xiao Xu
xiaoxu@andrew.cmu.edu

Filename: main.py

First group of import (line 16-22): python built-in modules
Second group of import (line 24-30): modules requiring additional installaztion 
Third Group of import (line 32-35): other submitted py files that should be kept in the same dictionary

95-888 Data Focused Python
Spring 2023 Mini 3
'''

import os

os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"

import copy
import re
from urllib.request import urlopen

import numpy as np
import pandas as pd
import progressbar
from bs4 import BeautifulSoup, Tag
from matplotlib import gridspec
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

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
        elif (response == '3'):
            currentAQI(anotherCity=True)
        elif (response == '4'):
            historicAQI(anotherCity=True)
        airnowPage()


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


# ============================================================================ #
# Feature 2 - Air Quality Stats
# ============================================================================ #

def airstatsPage(firstBrowser: bool = False):
    if (not user.databaseSet):
        user.database = requestAQS()
        user.databaseSet = True
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
            yrDf = singleYrDf(response)
            fig1 = aqiTrackerByYear(yrDf, fontweight='bold', fontsize=10)
            fig1.suptitle('Air Quality Time Series Analysis of Air Quality '
                          f'in {user.city}, {user.state} ({yr})',
                          fontsize=13, fontweight='bold')
            plt.show()
        elif (response == '2'):
            console.para('\n\n!!!!!\tDEMO LIMITS - please pick up one year '
                         'from 2016-2021 for demo as other 4-digit input may '
                         'raise error')
            response = console.prompt(
                question="yyyy to generate a monthly breakdown",
                answerPattern=r'^\d{4}$', quitButtonOn=False)
            cumDayBreakdown(response)
        elif (response == '3'):
            calendarHeatMap()
        airstatsPage()


def singleYrDf(yrResponse: str):
    yearIndex = user.database.index.year
    yearSelected = yearIndex == int(yrResponse)
    yearDf = user.database.loc[yearSelected, :]
    return yearDf


def cumDayBreakdown(yrResponse: str):
    fig = plt.figure(tight_layout=True)
    fig.set_size_inches(8, 6)
    gs = gridspec.GridSpec(2, 1)

    singYrAx = fig.add_subplot(gs[:1, :])
    yrsAx = fig.add_subplot(gs[1:, :])

    monthlyCumDays(ax=singYrAx, yr=yrResponse)
    yearlyCumDays(ax=yrsAx)
    fig.suptitle('Cumulative Day Breakdown over Time by Category',
                 fontsize=13, fontweight='bold')
    plt.show()


def monthlyCumDays(ax: Axes, yr: str):
    yLabelTemplate = '{:>3s}d'
    yTicks = [i for i in range(0, 31, 5)]
    ax.grid(True, linestyle='dotted')
    ax.set_ylim(0, 30)
    ax.set_yticks(yTicks)
    ax.set_yticklabels([yLabelTemplate.format(str(i)) if (i > 0) else '0'
                        for i in yTicks])
    ax.set_ylabel('Cumulative Days Over Time', fontweight='bold')

    xTickLabels = [date.strftime('%b') for date in
                   pd.date_range(start='20220101', end='20221231', freq='M')]
    ax.set_xlim(-0.5, 12.5)
    ax.set_xticks([i for i in range(12)])
    ax.set_xticklabels(xTickLabels, ha='left')
    ax.set_xlabel('Monthly Cumulative Days of Air Quality Index Categories '
                  f'in {user.city}, {yr}', fontweight='bold')
    ax.tick_params(labelsize=8)
    df = singleYrDf(yr)
    groupedBar(ax=ax, df=df, width=0.2,
               groupField=df.index.month, subGroupField='Level')
    ax.legend(title='Air Quality Index Categories', title_fontsize=8,
              fontsize=8, ncol=6, loc='upper right')


def yearlyCumDays(ax: Axes):
    yLabelTemplate = '{:>3s}d'
    yTicks = [i for i in range(0, 365, 30)]
    yTicks[-1] = 365
    ax.grid(True, linestyle='dotted')
    ax.set_ylim(0, 365)
    ax.set_yticks(yTicks)
    ax.set_yticklabels([yLabelTemplate.format(str(i)) if (i > 0) else '0'
                        for i in yTicks])
    ax.set_ylabel('Cumulative Days Over Time', fontweight='bold')

    xTickLabels = user.database.index.year.unique()
    xTicks = [i for i in range(len(xTickLabels))]
    ax.set_xticks(xTicks)
    ax.set_xticklabels(xTickLabels, ha='left')
    ax.set_xlim(xTicks[0] - 0.5, xTicks[-1] + 1.5)
    ax.set_xlabel('Annual Cumulative Days of Air Quality Index Categories '
                  f'from {xTickLabels[0]}-{xTickLabels[-1]}', fontweight='bold')
    ax.tick_params(labelsize=8)
    df = user.database
    groupedBar(ax=ax, df=df, width=0.2,
               groupField=df.index.year, subGroupField='Level')
    ax.legend(title='Air Quality Index Categories', title_fontsize=8,
              fontsize=8, ncol=6, loc='upper right')


def groupedBar(ax: Axes, df: pd.DataFrame, width: int,
               groupField: str, subGroupField: str):
    reconstruct = df.groupby(groupField)[subGroupField].value_counts()
    groupedDf = reconstruct.unstack()
    multiplier = 0
    x = np.arange(len(groupedDf.index))
    for col in groupedDf.columns:
        offset = width * multiplier
        aqiScale = aqiPalette.Category[col]
        aqiColor = aqiPalette.Color[col]
        rect = ax.bar(x + offset, groupedDf[col], width, align='edge',
                      label=aqiScale, color=aqiColor)
        ax.bar_label(rect, padding=3, fontsize=6.5)
        multiplier += 1


def calendarHeatMap():
    years = user.database.index.year.unique()
    meanDf = user.database.pivot_table(index=user.database.index.month,
                                       columns=user.database.index.day,
                                       values='AQI')

    fig, ax = plt.subplots(tight_layout=True, figsize=(8, 4))
    fig.suptitle(f'AQI Calendar Heat Map of {user.city}'
                 f'\nMean of Daily AQI from {years[0]}-{years[-1]}',
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Find today and check out next')
    ax.tick_params(labelsize=8, length=0)
    ax.set_yticks([i for i in range(12)])
    ax.set_yticklabels(
        [date.strftime('%b') for date
         in pd.date_range(start='20220101', end='20221231', freq='M')]
    )
    ax.set_xticks([d for d in range(0, 31)])
    ax.set_xticklabels([d for d in range(1, 32)], ha='left')
    heatmap = ax.imshow(meanDf, cmap='RdYlGn_r')
    fig.colorbar(heatmap, shrink=0.7, label='Daily AQI mean over years')
    plt.show()
    return


def requestAQS(start: int = 2010, end: int = 2021):
    widget = copy.copy(console.widget)
    widget[0] = widget[0].format('EPA AQS')
    dfList = []
    for yr in progressbar.progressbar(range(start, end + 1),
                                      widgets=widget, redirect_stdout=True):
        df = aqsAPI.requestSingleYr(yr, user.city, user.state)
        dfList.append(df)
    return pd.concat(dfList)


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
        "Multiscale Grouped Bar Chat",
        'AQI Calendar Heat Map',
    ]
    return mainFeatures, airnowFeatures, aqsFeatures


if __name__ == "__main__":

    # Initialize API
    console = Console()
    airnowAPI = AirNow()
    aqsAPI = AirQualitySys()
    aqiPalette = aqsAPI.palette

    # Initialize UI
    mainFeatures, airnowFeatures, aqsFeatures = initMenuFeatures()
    homeMenu = Menu(name='AirWise for Better Asthma Management',
                    features=mainFeatures)
    airnowMenu = Menu(name='Local Air Quality Information',
                      features=airnowFeatures, menuLevel=2)
    airstatsMenu = Menu(name='Air Quality Time Series Analysis Suite',
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
    user = prologue()
    homepage(firstBrowser=True)
    plt.close('all')
