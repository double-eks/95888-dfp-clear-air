import logging
import re
from datetime import datetime
from urllib.request import urlopen

import numpy as np
import pandas as pd
import progressbar
from bs4 import BeautifulSoup, Tag


class WebList:
    def __init__(self, tag: Tag):
        self.elements = tag
        self.bullets = [s for s in tag.stripped_strings]

    def logBullets(self):
        logLine()
        for i in range(len(self.bullets)):
            s = f'[{i}] {self.bullets[i]}'
            logList.info(s)
        logLine()


def webScraping(url: str):
    domain, home = findDomian(url)
    processing = f'web scraping from {home}'
    processed = f'{domain} data collected'
    length = max(len(processing), len(processed)) + 10
    processing = processing.center(length)
    processed = processed.center(length)
    lineLength = max(fmtHead, length)

    logLoading.info(processing.center(lineLength, '>'))
    html = urlopen(url)
    bs = BeautifulSoup(html.read(), "lxml")
    logLoading.info(processed.center(lineLength, '<'))
    logLine()
    return bs


def findDomian(url: str):
    link = url[re.search('https://', url).end():]
    home = link.split('/')[0]
    domain = home.split('.')[1]
    return domain, home


def genLogger(name: str, formatting: str,
              level: int = logging.DEBUG, handler: bool = True):
    if (name == ''):
        raise Exception('invalid logger name')
    logger = logging.getLogger(name)
    logger.setLevel(level)
    ch = logging.StreamHandler() if (handler) else logging.NullHandler()
    ch.setLevel(level)
    formatter = logging.Formatter(formatting, datefmt='%H:%M')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def logLine():
    logPara.info(' ')


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
    logTitle.info(clearAir.center(fmtHead))
    logPara.info(('-' * len(clearAir)).center(fmtHead))
    logPara.info(brief.center(fmtHead))
    logLine()
    logPara.info(epaIntro)
    logLine()


def sectionTrigger():
    # Scrap essential info
    triggerListTag = epa.find('article').find('ul')
    triggers = WebList(triggerListTag)
    # Output to Console
    logPara.info('More than 25 million people in the U.S. have asthma. '
                 'It is a long-term disease that causes your airways to become '
                 'swollen and inflamed, making it hard to breathe. '
                 'There is no cure for asthma, but it can be managed and controlled.')
    triggers.logBullets()


if __name__ == "__main__":

    # Initialize loggers
    logging.basicConfig(
        filename='processing.log', filemode='w', level=logging.DEBUG)
    logTitle = genLogger(
        name='title', formatting='\u001B[1;37m%(message)s\u001B[0m')
    logHeader = genLogger(
        name='main', formatting='\u001B[47m%(message)s\u001B[0m')
    logLoading = genLogger(
        name='loading', formatting='\u001B[3m%(message)s\u001B[0m')
    logPara = genLogger(
        name='para', formatting='%(message)s')
    logList = genLogger(
        name='list', formatting='\t - %(message)s')
    checker = genLogger(
        name='checker', formatting='\u001B[1;37m%(levelname)s\u001B[0m %(message)s',
        handler=True)

    # Format string templates
    fmtDate = '%a, %b %d, %Y'
    fmtTime = '%I:%M %p'
    fmtHead = 80

    # Scrape website sources
    epaURL = 'https://www.epa.gov/asthma/asthma-triggers-gain-control'
    epa = webScraping(epaURL)

    prologue()
    sectionTrigger()


"""
    epaMain = epa.extractLines(tag='article', name='main', flexible=True)[0]

    # Prologue % Content
    # prologue()
    introAsthma = epaMain.extractLines(tag='p', name='intro')[0]
    introAsthma.outputPara(outPara, prefix='According to EPA, ')

    triggerList = epaMain.extractLines(tag='ul', name='triggers')[0]
    container = epaMain.extractLines(tag='div', name='test', flexible=True,
                                         startFrom=triggerList.end,
                                         targetOcc=-1)
    # checker.debug(len(container))
    for c in container:
        c.check(checker)
    # checker.debug(epaMain.body[-10:])

    # with open('no.text', 'w', encoding='utf-8') as text:
    #     for line in epaMain.body:
    #         text.write(line)
    #         text.write('\n')

        #     outPara.info('''\
        # EPA provides asthma resources and guidance to improve asthma.
        # Press [NUM] to learn About Triggers and Actions You Can Take...''')
        # triggerList.outputBullets(outList)
        # print(container.output())
        # print(container.body)

        # infoOutput(intro,
        #            asthma.output(),
        #            triggerOptions,
        #            triggers.output(),
        #            len(triggers.items))
"""
