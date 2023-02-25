import re

import requests
from bs4 import BeautifulSoup


class Console:

    fmtLoading = '\u001B[3m{}\u001B[0m'
    fmtHeader = '\u001B[1m{}\u001B[0m'
    fmtTitle = '\n\u001B[4m{}\u001B[0m'
    fmtChoice = '\u001B[1m\u001B[4m{}\u001B[0m'
    fmtBullet = '  - {}'
    fmtDate = '%a, %b %d, %Y'
    fmtTime = '%I:%M %p'
    limitHeader = 80

    menuKey = f'{fmtChoice.format("H")} for Home Menu'
    quitKey = f'{fmtChoice.format("Q")} to quit ClearAir'
    separator = ' | '
    PROMPT = '\u001B[34m(^_^)\u001B[0m\t'
    ERROR = '\u001B[31m[>.<]\u001B[0m\tinvalid input...try again '

    PLACEHOLDER = 'https://secure.shippingapis.com/ShippingAPI.dll?API=CityStateLookup&XML='
    API_ID = '134CARNE2141'

    def __init__(self) -> None:
        # print('Hello\tthere are 2 intake questions before a go... Please')
        # self.zip = self.prompt(
        #     question='your 5-digit ZIP Code', answerPattern=r'\d{5}')
        # self.adult = self.prompt(
        #     options=['Y', 'N'],
        #     answers=['for adult services', 'for child service'],
        #     menuNavOn=False, quitButtonOn=False)
        # self.city, self.state = self.lookUpCityState()
        # self.adult = True if (self.adult == 'Y') else False
        # print(f"User from {self.city.capitalize()}, {self.state.upper()}, "
        #       "let's have fun with ClearAir!")
        # # TODO >>> Placeholder
        self.adult = True
        self.zip = '15213'
        self.city, self.state = self.lookUpCityState()
        self.adult = self.prompt(
            options=['Y', 'N'],
            answers=['for adult services', 'for child service'],
        )
        # # TODO <<< Placeholder

    def lookUpCityState(self):
        xml = '<CityStateLookupRequest USERID="{}"><ZipCode ID="0"><Zip5>{}</Zip5></ZipCode></CityStateLookupRequest>'
        url = Console.PLACEHOLDER + xml.format(Console.API_ID, self.zip)
        response = requests.get(url)
        text = BeautifulSoup(response.text, features="xml")
        return text.find('City').text, text.find('State').text

    def prompt(self,
               question: str = '', answerPattern: str = '',
               answers: list = [], options: list = [],
               menuNavOn: bool = True, quitButtonOn: bool = True):
        if (question):
            menuInfo = question
        else:
            if (answers):  # Generate option description
                optList = [self.formattedOption(options[i], answers[i])
                           for i in range(len(options))]
            else:  # Use simplified option template
                template = self.formattedOption("\u001B[3moption number")
                optList = [f'{template} for Browser Options']
            if (menuNavOn):
                optList.append(Console.menuKey)
            if (quitButtonOn):
                optList.append(Console.quitKey)
            menuInfo = Console.separator.join(optList) + '  (case insensitive)'
        print(self.formattedChoice('ENTER') + '\t' + menuInfo)
        response = input(Console.PROMPT)
        while True:
            if (question != ''):  # Protect short question from home and quit
                if (re.search(answerPattern, response) != None):
                    break
            else:  # Choose one option
                if (options):
                    checker = options
                else:
                    checker = [str(i + 1) for i in range(len(answers))]
                if (response.upper() == 'Q'):
                    quit()
                elif (response.upper() == 'H'):
                    return self.homepage()
                elif (response.upper() in checker):
                    break
            response = input(Console.ERROR)
        return response

    def formattedChoice(self, s: str):
        return Console.fmtChoice.format(s)

    def formattedOption(self, option: str, explanation: str):
        result = self.formattedChoice(option) + ' ' + explanation
        return result

    def loading(self, message: str, symbol: str):
        load = message.center(len(message) + 10).center(
            Console.limitHeader, symbol)
        print(Console.fmtLoading.format(load))

    def header(self, message: str):
        separator = ('-' * (len(message) + 5)).center(Console.limitHeader)
        title = message.center(Console.limitHeader)
        print('')
        print(Console.fmtHeader.format(separator))
        print(Console.fmtHeader.format(title))
        print(Console.fmtHeader.format(separator))
        print('')

    def subHeader(self, message: str):
        print(message.center(Console.limitHeader), '\n')

    def multiChoice(self, choices: list):
        print('')
        for i in range(len(choices)):
            choice = self.formattedOption(i + 1, choices[i])
            print('\t' + choice)
        print('')

    def title(self, message: str):
        print(self.fmtTitle.format(message))

    def bullet(self, message: str):
        print(self.fmtBullet.format(message))

    def para(self, message: str):
        print(message)

    def homepage(self):
        features = [
            'Environmental Asthma Triggers',
            'NCHC Asthma FastStats'
        ]
        self.multiChoice(features)
