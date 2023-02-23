import logging
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


def fileWebScraping(url: str):
    html = urlopen(url)
    bs = BeautifulSoup(html.read(), "lxml")
    with open('temp.html', 'w', encoding='utf-8') as text:
        text.write(bs.prettify())


def genLogger(name: str, rank: int,
              level: int = logging.DEBUG, formatting: str = ''):
    if (name == ''):
        raise Exception('invalid logger name')
    logger = logging.getLogger(name)
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    tab = rank * '\t'
    if (formatting == ''):
        formatting = f'{tab}%(levelname)s >> %(message)s'
    formatter = logging.Formatter(formatting, datefmt='%H:%M')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def infoOutput(*args: str):
    for arg in args:
        print(f'\n{arg}')


if __name__ == "__main__":

    # Initialize logging
    logging.basicConfig(filename='processing.log',
                        filemode='w',
                        level=logging.DEBUG)
    logger = genLogger('main', 0)
    ui = genLogger('UI', 0, formatting='\n%(message)s')

    epaURL = 'https://www.epa.gov/asthma/asthma-triggers-gain-control'
    epaWholeBody = webScraping(epaURL)
    epa = Body(epaWholeBody, 'EPA')
    article = epa.extractByTag(tag='article', name='main', flexible=True)
    asthma = article.extractByTag(tag='p', name='intro')
    triggers = article.extractByTag(tag='ul', name='triggers', ul=True)
    container = article.extractByTag(
        tag='div', name='test', startFrom=triggers.end, targetOcc=10)

    intro = 'Welcome to ClearAir!'
    triggerOptions = '''\
EPA provides asthma resources and guidance to improve asthma.
Press [digits] to learn About Triggers and Actions You Can Take...'''

    # print(container.output())
    # print(container.body)

    # infoOutput(intro,
    #            asthma.output(),
    #            triggerOptions,
    #            triggers.output(),
    #            len(triggers.items))
