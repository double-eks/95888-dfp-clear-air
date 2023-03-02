import re
from datetime import datetime

import progressbar
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame


class ZipCityState:
    def __init__(self, zipcode: str) -> None:
        self.setUser(zipcode)
        print(
            f"\nHello! User from {self.location}, have a blast!\n")
        pass

    def setUser(self, zipcode: str):
        self.zip = zipcode
        self.city, self.state = self.lookUpCityState()
        self.city = self.city.capitalize()
        self.state = self.state.upper()
        self.location = ', '.join([self.city, self.state, self.zip])
        return self.location

    def lookUpCityState(self):
        xml = '<CityStateLookupRequest USERID="{}"><ZipCode ID="0"><Zip5>{}</Zip5></ZipCode></CityStateLookupRequest>'
        url = Console._PLACEHOLDER + xml.format(Console._API_ID, self.zip)
        response = requests.get(url)
        text = BeautifulSoup(response.text, features="xml")
        return text.find('City').text, text.find('State').text


class Console:

    _PLACEHOLDER = 'https://secure.shippingapis.com/ShippingAPI.dll?API=CityStateLookup&XML='
    _API_ID = '134CARNE2141'
    _LINE_LENGTH = 80

    def __init__(self) -> None:
        self.today = datetime.now()
        self.widget = ['\x1b[3m{} API \x1b[0m',
                       progressbar.Bar(marker='>'),
                       progressbar.ETA(), '  ',
                       progressbar.Percentage()]
        pass

    def prompt(self, question: str = '', answerPattern: str = '',
               answers: list = [], answerRequired: bool = True,
               menuNavOn: bool = False, quitButtonOn: bool = True):
        if (question):
            optList = [question]
        else:
            optList = [
                f'{self.formattedChoice("number keys")} to browser Features']
        if (menuNavOn):
            optList.append(f'{self.formattedChoice("H")} for Home Menu')
        if (quitButtonOn):
            optList.append(f'{self.formattedChoice("Q")} to quit ClearAir')
        menuInfo = ' | '.join(optList)
        if (not question):
            menuInfo += '  (case insensitive)'
        print(self.formattedChoice('ENTER') + '\t' + menuInfo)
        response = input('\u001B[34m(^_^)\u001B[0m\t')
        if (answerRequired):
            while True:
                if (answerPattern != ''):  # Protect short question from home and quit
                    if (re.search(answerPattern, response) != None):
                        return response
                checker = [str(i + 1) for i in range(len(answers))]
                if (menuNavOn) and (response.upper() == 'H'):
                    return response
                if (quitButtonOn) and (response.upper() == 'Q'):
                    quit()
                elif (response in checker):
                    return response
                response = input(
                    '\u001B[31m[>.<]\u001B[0m\tinvalid input...try again ')

    def formattedChoice(self, s: str):
        return '\u001B[1m\u001B[4m{}\u001B[0m'.format(s)

    def checkpoint(self, message: str = ''):
        template = 'Press any keys to continue'
        if (message != ''):
            template = f'{message} {template}'
        self.prompt(question=template, answerRequired=False,
                    menuNavOn=False, quitButtonOn=False)

    def loading(self, message: str):
        widget = f' requesting from {message} '
        bar = widget.center(Console._LINE_LENGTH, '>')
        fmtBar = '\u001B[3;30m{}\u001B[0m'.format(bar)
        print(fmtBar)

    def requested(self):
        self.checkpoint('Data retrieved...')

    def chapter(self, message: str, *args):
        headerFmt = '\u001B[1m{}\u001B[0m'
        separator = '-' * Console._LINE_LENGTH
        title = message.center(Console._LINE_LENGTH)
        print(headerFmt.format('\n' + separator))
        print(headerFmt.format(title))
        print(headerFmt.format(separator))
        for arg in args:
            print(arg)
        print('')

    def title(self, message: str, split: bool = False):
        if (split):
            print(f"\n{'.' * Console._LINE_LENGTH}\n")
        else:
            print('')
        if (message != ''):
            print('\u001B[1m\u001B[4m{}\u001B[0m'.format(message))

    def bullet(self, message: str):
        print('- {}'.format(message))

    def para(self, message: str):
        print(message)

    def table(self, df: DataFrame):
        print('')
        print(df.to_markdown(index=False))


class Menu():
    def __init__(self, name: str, features: list, menuLevel: int = 1) -> None:
        self.name = name
        self.features = features
        self.checked = set()
        self.level = menuLevel
        self.prefix = (' ' * 5 + '\t') * menuLevel
        pass

    def content(self, firstBrowser: bool = False):
        if (not firstBrowser):
            print('')
        print('{}:\n'.format(self.name))
        for i in range(len(self.features)):
            checked = '\u001B[4m{}\u001B[0m  {}'
            unchecked = '\u001B[1m\u001B[4;34m{}\u001B[0m  \u001B[1;34m{}\u001B[0m'
            feature = self.features[i]
            no = i + 1
            if (no in self.checked):
                template = checked
            else:
                template = unchecked
            result = template.format(i + 1, feature)
            print(self.prefix + result)
        print('')
