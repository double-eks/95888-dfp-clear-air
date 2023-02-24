import logging
import re
from datetime import datetime
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


def logOptions(options: list):
    logLine()
    for i in range(len(options)):
        s = f'[{i}] {options[i]}'
        logOpt.info(s)
    logLine()


def logLine():
    logPara.info(' ')


def selTrigger(triggersListTag: Tag, triggersList: list, triggerIndex: int):
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
    logTitle.info(about.text)
    for tag in about.find_all_next():
        if ('h' in tag.name):
            break
        if (('p' or 'li') in tag.name):
            if (isValidText(tag.text)):
                logPara.info(tag.text.strip())
    # Report the Action You Can Take part
    logTitle.info(action.text)
    for detail in (actionDetail.stripped_strings):
        if (isValidText(detail)):
            logBullet.info(detail)


def prologue():
    # Scrap essential info
    clearAir = 'Welcome to ClearAir'
    date = datetime.now().strftime(fmtDate)
    time = datetime.now().strftime(fmtTime)
    brief = '\t'.join([date, time])
    epaIntro = ''
    for para in epa.find('article').find_all('p'):
        if (len(para.attrs) == 0):
            epaIntro = para.string.strip()
            break
    # Output to Console
    logWelcome.info(clearAir.center(fmtHead))
    logPara.info(('-' * len(clearAir)).center(fmtHead))
    logPara.info(brief.center(fmtHead))
    logLine()
    logPara.info(epaIntro)
    logLine()


def sectionTrigger():
    # Scrap essential info
    triggersListTag = epa.find('article').find('ul')
    triggersList = [s for s in triggersListTag.stripped_strings]
    # Output to Console
    logPara.info('More than 25 million people in the U.S. have asthma. '
                 'It is a long-term disease that causes your airways to become '
                 'swollen and inflamed, making it hard to breathe. '
                 'There is no cure for asthma, but it can be managed and controlled.')
    logOptions(triggersList)
    # Ask for option and output to console
    for inputNum in range(len(triggersList)):
        selTrigger(triggersListTag, triggersList, inputNum)


if __name__ == "__main__":

    # Initialize loggers
    logging.basicConfig(
        filename='processing.log', filemode='w', level=logging.DEBUG)
    logWelcome = genLogger(
        name='clearair', formatting='\u001B[1;37m%(message)s\u001B[0m')
    logLoading = genLogger(
        name='loading', formatting='\u001B[3m%(message)s\u001B[0m')
    logSection = genLogger(
        name='header', formatting='\u001B[47m%(message)s\u001B[0m')
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

    # EPA
    path = '/Volumes/Workaholic/Workspace/Processing/Asthma Triggers_ Gain Control _ US EPA.html'
    epaURL = 'https://www.epa.gov/asthma/asthma-triggers-gain-control'
    epa = webScraping(epaURL)
    prologue()
    sectionTrigger()
