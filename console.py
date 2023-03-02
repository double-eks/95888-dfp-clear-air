import re
from datetime import datetime

import progressbar
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame


class Console:

    _PLACEHOLDER = 'https://secure.shippingapis.com/ShippingAPI.dll?API=CityStateLookup&XML='
    _API_ID = '134CARNE2141'
    _LINE_LENGTH = 80

    def __init__(self) -> None:
        # # TODO >>> Placeholder
        # print('Hello\tthere are 2 intake questions before a go... Please')
        # self.zip = self.prompt(
        #     question='your 5-digit ZIP Code', answerPattern=r'\d{5}')
        # self.city, self.state = self.lookUpCityState()
        # self.adult = True if (self.adult == 'Y') else False
        self.today = datetime.now()
        self.zip = '15213'
        self.city, self.state = self.lookUpCityState()
        self.city = self.city.capitalize()
        self.state = self.state.upper()
        self.location = ', '.join([self.city, self.state, self.zip])
        # print(f"User from {self.location}, let's have fun with ClearAir!\n")
        # # TODO <<< Placeholder
        self.widget = ['\x1b[3m{} API \x1b[0m',
                       progressbar.Bar(marker='>'),
                       progressbar.ETA(), '  ',
                       progressbar.Percentage()]

    def lookUpCityState(self):
        xml = '<CityStateLookupRequest USERID="{}"><ZipCode ID="0"><Zip5>{}</Zip5></ZipCode></CityStateLookupRequest>'
        url = Console._PLACEHOLDER + xml.format(Console._API_ID, self.zip)
        response = requests.get(url)
        text = BeautifulSoup(response.text, features="xml")
        return text.find('City').text, text.find('State').text

    def prompt(self, question: str = '', answerPattern: str = '',
               answers: list = [], answerRequired: bool = True,
               menuNavOn: bool = False, quitButtonOn: bool = True):
        if (question):
            menuInfo = question
        else:
            optList = [self.formattedOption('number keys',
                                            'to browser Features')]
            if (menuNavOn):
                optList.append(f'{self.formattedChoice("H")} for Home Menu')
            if (quitButtonOn):
                optList.append(f'{self.formattedChoice("Q")} to quit ClearAir')
            menuInfo = ' | '.join(optList) + '  (case insensitive)'
        print(self.formattedChoice('ENTER') + '\t' + menuInfo)
        response = input('\u001B[34m(^_^)\u001B[0m\t')
        if (answerRequired):
            while True:
                if (question != ''):  # Protect short question from home and quit
                    if (re.search(answerPattern, response) != None):
                        break
                else:  # Choose one option
                    checker = [str(i + 1) for i in range(len(answers))]
                    if (menuNavOn) and (response.upper() == 'H'):
                        break
                    if (response.upper() == 'Q'):
                        quit()
                    elif (response.upper() in checker):
                        break
                response = input(
                    '\u001B[31m[>.<]\u001B[0m\tinvalid input...try again ')
        return response

    def checkpoint(self, message: str = ''):
        template = 'Press any keys to continue'
        if (message != ''):
            template = f'{message} {template}'
        self.prompt(question=template, answerRequired=False)

    def formattedChoice(self, s: str):
        return '\u001B[1m\u001B[4m{}\u001B[0m'.format(s)

    def formattedOption(self, option: str, explanation: str):
        result = self.formattedChoice(option) + ' ' + explanation
        return result

    def loading(self, message: str):
        widget = f' requesting from {message} '
        bar = widget.center(Console._LINE_LENGTH, '>')
        fmtBar = '\u001B[3;30m{}\u001B[0m'.format(bar)
        print(fmtBar)

    def requested(self):
        self.checkpoint('Data loaded...')

    def header(self, message: str, sub: bool = False):
        headerFmt = '\u001B[1m{}\u001B[0m'
        separator = ('-' * (len(message) + 12)).center(Console._LINE_LENGTH)
        title = message.center(Console._LINE_LENGTH)
        if (sub):
            print(headerFmt.format(title))
        else:
            print(headerFmt.format('\n' + separator))
            print(headerFmt.format(title))
            print(headerFmt.format(separator + '\n'))

    def separator(self):
        print(f"\n{'.' * Console._LINE_LENGTH}\n")

    def multiChoice(self, choices: list):
        print('')
        for i in range(len(choices)):
            choice = self.formattedOption(i + 1, choices[i])
            print(' ' * 10 + choice)
        print('')

    def title(self, message: str):
        print('\n\u001B[4m{}\u001B[0m'.format(message))

    def bullet(self, message: str):
        print('- {}'.format(message))

    def para(self, message: str,
             preIndent: bool = False, postIndent: bool = False):
        if (preIndent):
            print('')
        print(message)
        if (postIndent):
            print('')

    def table(self, df: DataFrame):
        print('')
        print(df.to_markdown(index=False))
        print('')

    def multiLines(self, message: str, indent: int = 0, bullet: str = '-'):
        words = message.split()
        lines = []
        if (indent == 0):
            prefix = ''
            currLine = ''
        else:
            prefix = ' ' * (indent + 2)
            currLine = f'  {bullet} '

        for word in words:
            if (len(currLine) + len(word) <= Console._LINE_LENGTH):
                currLine += f'{word} '
            else:
                lines.append(currLine)
                currLine = f'{prefix}{word} '
        lines.append(currLine)
        return lines
