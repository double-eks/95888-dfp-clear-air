"""
This is the main structure of web scraping
"""


import logging
import re
from datetime import datetime
from unicodedata import category
from urllib.request import urlopen

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, Tag


def webScraping(url: str) -> BeautifulSoup:
    # Format the loading messages
    domain, home = findDomian(url)
    processing = f'web scraping from {home}'
    processed = f'{domain} data collected'
    length = max(len(processing), len(processed)) + 10
    processing = processing.center(length)
    processed = processed.center(length)
    lineLength = max(fmtHead, length)

    # Start web scraping
    logLoading.info(processing.center(lineLength, '>'))
    html = urlopen(url)
    # bs = BeautifulSoup(html.read(), "lxml")
    with open(path) as copy:
        html = copy.read()
    bs = BeautifulSoup(html, "html.parser")

    # Complete web scraping
    logLoading.info(processed.center(lineLength, '<'))
    logLine()
    return bs


def findDomian(url: str):
    """
    Return the domain and home page link of the given url
    """
    link = url[re.search('https://', url).end():]
    home = link.split('/')[0]
    domain = home.split('.')[1]
    return domain, home


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


def genLogger(name: str, formatting: str, level: int = logging.DEBUG):
    if (name == ''):
        raise Exception('invalid logger name')
    logger = logging.getLogger(name)
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter(formatting, datefmt='%H:%M')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def logSectionTitle(titleName: str):
    separator = ('-' * (len(titleName) + 5)).center(fmtHead)
    title = titleName.upper().center(fmtHead)
    logSection.info(separator)
    logSection.info(title)
    logSection.info(separator)


def logOptions(options: list):
    logLine()
    for i in range(len(options)):
        s = f'[{i}] {options[i]}'
        logOpt.info(s)
    logLine()


def logLine():
    logPara.info(' ')


def sectionFastStats():
    logSectionTitle('asthma faststats © CDC')

    cardTag = 'div'
    attr = 'class'
    cardClass = 'card mb-3'
    cardHeaderClass = 'bg-primary'

    for card in nchc.find_all(cardTag, attrs={attr: cardClass}):
        header = card.find_next('div')
        if (cardHeaderClass in header.get(attr)):
            logTitle.info(header.text.strip())
            for fact in card.find_all('li'):
                logBullet.info(fact.text.strip())


if __name__ == "__main__":
    # TODO placeholder
    path = 'placeholder'

    # Initialize loggers
    logging.basicConfig(
        filename='processing.log', filemode='w', level=logging.DEBUG)
    logWelcome = genLogger(
        name='clearair', formatting='\u001B[1;37m%(message)s\u001B[0m')
    logLoading = genLogger(
        name='loading', formatting='\u001B[3m%(message)s\u001B[0m')
    logSection = genLogger(
        name='header', formatting='\u001B[1m%(message)s\u001B[0m')
    logTitle = genLogger(
        name='title', formatting='\n\u001B[4m%(message)s\u001B[0m')
    logOpt = genLogger(
        name='options', formatting='\t%(message)s')
    logPara = genLogger(
        name='para', formatting='%(message)s')
    logBullet = genLogger(
        name='list', formatting='- %(message)s')
    checker = genLogger(
        name='checker', formatting='\u001B[1;35m%(levelname)s\u001B[0m %(message)s')

    # Format string templates
    fmtDate = '%a, %b %d, %Y'
    fmtTime = '%I:%M %p'
    fmtHead = 80

    path = '/Volumes/Workaholic/Workspace/Processing/FastStats - Asthma.html'
    nchcURL = 'https://www.cdc.gov/nchs/fastats/asthma.htm'
    nchc = webScraping(nchcURL)

    sectionFastStats()
