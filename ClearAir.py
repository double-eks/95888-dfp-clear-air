import logging
import os
from datetime import datetime
from urllib.request import urlopen

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

from WebSource import Body


def webScraping(url: str):
    html = urlopen(url)
    bs = BeautifulSoup(html.read(), "lxml")
    return bs.prettify().splitlines()


def fileWebScraping(url: str, path):
    if (path not in os.listdir()):
        html = urlopen(url)
        bs = BeautifulSoup(html.read(), "lxml")
        with open(path + '.html', 'w', encoding='utf-8') as text:
            text.write(bs.prettify())
        with open(path, 'w', encoding='utf-8') as text:
            text.write(bs.prettify())
    with open(path, 'r') as text:
        lines = text.read()
    return lines.splitlines()


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


def prologue():
    outTitle.info('Welcome to ClearAir!')
    outPara.info('''\
More than 25 million people in the U.S. have asthma. \
It is a long-term disease that causes your airways to become swollen and inflamed, \
making it hard to breathe. There is no cure for asthma, \
but it can be managed and controlled.''')


if __name__ == "__main__":

    # Initialize loggers
    logging.basicConfig(filename='processing.log',
                        filemode='w',
                        level=logging.DEBUG)
    outTitle = genLogger('main', formatting='\n%(message)s\n')
    outPara = genLogger('para', formatting='%(message)s\n')
    outList = genLogger('list', formatting='\t - %(message)s')
    checker = genLogger(
        'checker', formatting='\u001B[4;35m%(levelname)s\u001B[0m %(message)s', handler=True)

    # Scrape website sources
    epaURL = 'https://www.epa.gov/asthma/asthma-triggers-gain-control'
    epaWholeBody = fileWebScraping(epaURL, 'temp-epa.txt')
    epa = Body(epaWholeBody, 'EPA')
    epaMain = epa.extractLines(tag='article', name='main', flexible=True)[0]

    # Prologue % Content
    prologue()
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
