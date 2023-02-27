

import logging
import re
from datetime import timedelta
from urllib.request import urlopen

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, Tag

from console import Console


def webScraping(url: str) -> BeautifulSoup:

    print('')
    # Format the loading messages
    link = url[re.search('https://', url).end():]
    home = link.split('/')[0]
    domain = home.split('.')[-2]
    processing = f'web scraping from {home}'
    processed = f'{domain} data collected'

    # Start web scraping
    console.loading(processing, '>')
    html = urlopen(url)
    bs = BeautifulSoup(html.read(), "lxml")
    # with open(path) as copy:
    #     html = copy.read()
    # bs = BeautifulSoup(html, "html.parser")
    # Complete web scraping
    console.loading(processed, '<')
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


def prologue():
    '''
    weatherTag = airNowHome.find('div', attrs={'class': 'weather-value'})
    weather = weatherTag.text.strip() + ' °F'
    currAQI = ' '.join(summarizeOneLine(airNowHome.find(
        'div', attrs={'class': 'current-aq-data'})))
    aqiTemplate = "{} Air {}"  # /day /category AQI

    todayAqi = airNowHome.find('div', attrs={'class': 'today-aq-data'}).find_next(
        'div', attrs={'class': 'category'}).text
    tmrAqi = airNowHome.find('div', attrs={'class': 'tomorrow-aq-data'}).find_next(
        'div', attrs={'class': 'category'}).text

    today = aqiTemplate.format(todayAqi.upper(), 'Today')
    forecast = aqiTemplate.format(tmrAqi.upper(), 'Tomorrow')

    aqiBar = ['Current Air Quality', currAQI, weather]
    marquee = [today, forecast]
    '''
    # Prologue paragraph
    brief = [console.location,
             console.today.strftime('%a, %b %d, %Y, %I:%M %p')]
    epaIntro = ''
    for para in epa.find('article').find_all('p'):
        if (len(para.attrs) == 0):
            epaIntro = para.string.strip()
            break
    # Output to Console
    console.header('WELCOME to ClearAir for Better Asthma Management')
    console.subHeader([brief])
    console.para(epaIntro)


'''
def airQualityTable():
    currentList, forecastList = currentAqi(), forecastAqi()
    forecastDf = pd.DataFrame(forecastList, columns=['Day', 'AQI', 'Level',
                                                     'Main Pollutant'])
    forecastDf['Date'] = ['yyyy/mm/dd'] * len(forecastDf)
    masterDf = forecastDf.reindex(columns=['Date', 'Day', 'Main Pollutant',
                                           'AQI', 'Level'])
    masterDf['AQI'][0] = currentList[1]
    masterDf['Level'][0] = currentList[2]
    masterDf['Main Pollutant'][0] = currentList[0]

    print(masterDf)

    # for i in range(len(masterDf)):
    #     currLevel = masterDf['Level'][i]
    #     currRow = aqiLegend.dictionary[currLevel]
    #     currColor = aqiLegend.legend.iloc[currRow, -1]
    #     currDate = datetime.now() + timedelta(days=i)
    #     masterDf['Date'][i] = currDate.strftime(console.fmtDate)
    #     masterDf['AQI'][i] = currColor.format(masterDf['AQI'][i])
    #     masterDf['Level'][i] = currColor.format(currLevel)

    # currReport = f'Current Primary Pollutant ({masterDf.Date[0]})'
    # currDescr = f'{currentList[0]} in {console.city} has highest AQI, {currentList[1]} ({currentList[2]}).'
    # console.title(currReport)
    # console.para(currDescr, True)
    # console.para(currentList[-1])  # instruction
    # print('')
    # console.table(masterDf)
    # aqiCaution(forecastDf.Level, masterDf.Date)


def currentAqi():
    classAttr = 'col-sm-6 pollutant-custom-col'
    primaryTag = airNowHome.find('div', attrs={'class': classAttr}).find_next(
        'div', attrs={'class': classAttr}).find('div')
    primary = summarizeOneLine(primaryTag)
    return primary[-4:]


def forecastAqi():
    forecastTag = airNowHome.find('div', attrs={'class': 'col-xs-12 days'})
    forecastList = []
    for i in range(6):
        dayTag = forecastTag.find_next(
            'div', attrs={'id': f'day-{i}'})
        daySummary = []
        for cell in dayTag.find_all('div'):
            if (cell.text.strip() != ''):
                daySummary.append(cell.text.strip())
        if ('Not Available' in daySummary):
            break
        forecastList.append(daySummary)
    return forecastList

def aqiCaution(levels, dates):
    for i in range(len(levels)):
        level = levels[i]
        rowInLegend = aqiLegend.dictionary[level]
        if (rowInLegend > 0):
            implications = '{}: {}'.format(aqiLegend.legend.columns[-3],
                                           aqiLegend.legend.iloc[rowInLegend, -3])
            statement = '{}: {}'.format(aqiLegend.legend.columns[-2],
                                        aqiLegend.legend.iloc[rowInLegend, -2])
            console.title(
                'Air Quality Forecasting Caution ({})'.format(dates[i]))
            console.para(implications, True)
            console.para(statement)
'''


def triggerPage():
    console.header('Asthma Triggers © EPA')
    # Scrap essential info
    triggersListTag = epa.find('article').find('ul')
    triggersList = [s for s in triggersListTag.stripped_strings]
    # Output to Console
    console.para('More than 25 million people in the U.S. have asthma. '
                 'It is a long-term disease that causes your airways to become swollen and inflamed, '
                 'making it hard to breathe. There is no cure for asthma, '
                 'but it can be managed and controlled.')
    console.multiChoice(triggersList)
    # Ask for option and output to console
    for inputNum in range(len(triggersList)):
        triggerIntro(triggersListTag, triggersList, inputNum)


def triggerIntro(triggersListTag: Tag, triggersList: list, triggerIndex: int):
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
    console.header('Asthma Faststats © CDC')
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


if __name__ == "__main__":

    # * Initialize console
    console = Console()
    logging.basicConfig(level=logging.DEBUG)

    # Web Scraping
    epaURL = 'https://www.epa.gov/asthma/asthma-triggers-gain-control'
    nchcURL = 'https://www.cdc.gov/nchs/fastats/asthma.htm'
    airNowGov = 'https://www.airnow.gov/?city={}&state={}&country=USA'

    epa = webScraping(epaURL)
    nchc = webScraping(nchcURL)
    # airNowHome = webScraping(airNowGov.format(console.city, console.state))

    # Prologue paragraph
    # legendPage = webScraping('https://aqicn.org/scale/')
    # aqiLegend = AqiLegend(legendPage)

    # Deploy
    prologue()
    console.homepage()
    console.checkpoint()
    triggerPage()
    console.checkpoint()
    fastStatsPage()
