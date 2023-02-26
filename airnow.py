from unicodedata import category

import pandas as pd
import requests


class AqiLegend:
    def __init__(self, bs) -> None:
        self.legend = self.genLegendDf(bs)
        self.dictionary = self.genDict()

    def genLegendDf(self, bs):
        table = bs.find('table', attrs={'class': 'infoaqitable cautionary'})
        headerTag = table.find('thead')
        headers = []
        for td in headerTag.find_all('td'):
            headers.append(td.text.strip())
        # Extract the table rows and data
        bodyTag = table.find('tbody')
        body = []
        for tr in bodyTag.find_all('tr'):
            row = []
            for td in tr.find_all('td'):
                row.append(td.text.strip())
            if (len(row) > 0):
                body.append(row)
        legend = pd.DataFrame(body, columns=headers)
        legend.iloc[2, 1] = 'Sensitive Caution'
        palette = ['\u001B[0;32m{}\u001B[0m',
                   '\u001B[0;33m{}\u001B[0m',
                   '\u001B[0;31m{}\u001B[0m',
                   '\u001B[1;31m{}\u001B[0m',
                   '\u001B[4m\u001B[1;35m{}\u001B[0m',
                   '\u001B[4m\u001B[1;30m{}\u001B[0m']
        legend['ansi'] = palette
        return legend

    def genDict(self):
        category = dict()
        levels = self.legend.iloc[:, 1]
        for i in range(len(levels)):
            category[levels[i]] = i
        return category
