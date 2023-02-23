
import re
from urllib.request import urlopen

from bs4 import BeautifulSoup


class WebSource:

    def __init__(self, url: str):
        html = urlopen(url)
        bs = BeautifulSoup(html.read(), "lxml")
        self.page = bs.prettify().splitlines()
        self.sections = dict()

    def extractByTag(self, text: list[str], tag: str, name: str, targetOcc: int = 1):
        start = f'<{tag}'
        if (' ' in tag):
            tagPrefix = tag[:tag.find(' ')]
            end = f'</{tagPrefix}'
        else:
            end = f'</{tag}'
        result = []
        found = False
        occ = 0
        for line in text:
            line = line.strip()
            if (line.startswith(start)):
                occ += 1
                if (occ == targetOcc):
                    found = True
            if (found):
                result.append(line)
                if (line.startswith(end)):
                    break
        self.sections[name] = result

    def formatSection(self, sectionID: str):
        content = []
        for line in self.sections[sectionID]:
            if ('<' not in line) and ('>' not in line):
                content.append(line)
        return '\n'.join(content)


def fileWebScraping(url: str):
    html = urlopen(url)
    bs = BeautifulSoup(html.read(), "lxml")
    with open('temp.html', 'w', encoding='utf-8') as text:
        text.write(bs.prettify())


def formatPara(text: list[str]):
    content = []
    for line in text:
        if ('<' not in line) and ('>' not in line):
            content.append(line)
    return '\n'.join(content)


# def asthmaTriggers():
#     aafa = 'https://aafa.org/asthma/asthma-triggers-causes/'
#     epa = 'https://www.epa.gov/asthma/asthma-triggers-gain-control'
#     text = webScraping(epa)

def infoOutput(*args: str):
    for arg in args:
        print(f'\n{arg}')


def welcome():
    epaURL = 'https://www.epa.gov/asthma/asthma-triggers-gain-control'
    epa = WebSource(epaURL)
    epa.extractByTag(epa.page,
                     tag='article class="article"', name='body')
    epa.extractByTag(epa.sections['body'],
                     tag='p>', name='asthma')
    epa.extractByTag(epa.sections['body'],
                     tag='ul>', name='triggers')

    print(epa.sections['triggers'])

    intro = 'Welcome to ClearAir!'
    asthma = epa.formatSection('asthma')

    infoOutput(intro, asthma)


if __name__ == "__main__":
    welcome()
