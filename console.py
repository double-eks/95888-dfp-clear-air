import re

import requests
from bs4 import BeautifulSoup

# def ui(question: str, options: dict = dict()):
#     logOpt.info(f'>>> {question} case-insensitive)\n')
#     if (len(options) > 0):
#         for key in options:
#             logOpt.info(f'[{key}] {options[key]}')
#     inputPlaceholder = '\t>'
#     answer = input(fmtInput)
#     if (len(options) > 0):
#         while True:
#             if (answer.isalpha()):
#                 answer = answer.upper()
#             if (answer in options):
#                 break
#             hint = f'\t<<< please press {" / ".join(options)}\n{inputPlaceholder}'
#             answer = input(hint)
#     return answer


class Console:

    PREFIX = '\u001B[1m\u001B[4mENTER\u001B[0m\t'
    menuKey, quitKey = '[M] for Menu', '[Q] to quit ClearAir'
    PROMPT = '\u001B[34m(^_^)\u001B[0m\t:'
    ERROR = '\u001B[31m[>.<]\u001B[0m\tinvalid answers...try again: '

    PLACEHOLDER = 'https://secure.shippingapis.com/ShippingAPI.dll?API=CityStateLookup&XML='
    API_ID = '134CARNE2141'

    def __init__(self) -> None:
        print('Hello\tthere are 2 intake questions before a go... Please')
        self.zip = self.prompt(
            question='your 5-digit ZIP Code', answerPattern=r'\d{5}')
        self.adult = self.prompt(
            options={'Y': 'for adult services', 'N': 'for child service'},
            optHint=True, menuNavOn=False, quitButtonOn=False)
        self.adult = self.prompt(
            options={'Y': 'for adult services', 'N': 'for child service'})
        self.city, self.state = self.lookUpCityState()
        self.adult = True if (self.adult == 'Y') else False
        print(f"\nUser from {self.city.capitalize()}, {self.state.upper()}, "
              "let's have fun with ClearAir!")

    def lookUpCityState(self):
        xml = '<CityStateLookupRequest USERID="{}"><ZipCode ID="0"><Zip5>{}</Zip5></ZipCode></CityStateLookupRequest>'
        url = Console.PLACEHOLDER + xml.format(Console.API_ID, self.zip)
        response = requests.get(url)
        text = BeautifulSoup(response.text, features="xml")
        return text.find('City').text, text.find('State').text

    def prompt(self,
               question: str = '', answerPattern: str = '',
               options: dict = {}, optHint: bool = False,
               menuNavOn: bool = True, quitButtonOn: bool = True):
        if (question != ''):
            menuInfo = question
        else:
            if (optHint):  # Generate option description
                optList = [f'[{key}] {options[key]}' for key in options]
            else:  # Use simplified option template
                optList = ['[\u001B[3moption above\u001B[0m] '
                           'for Browser Options']
            if (menuNavOn):
                optList.append(Console.menuKey)
            if (quitButtonOn):
                optList.append(Console.quitKey)
            menuInfo = ' / '.join(optList) + '  (case insensitive)'
        print(Console.PREFIX + menuInfo)
        answer = input(Console.PROMPT)
        while True:
            if (question != ''):  # Protect short question from home and quit
                if (re.search(answerPattern, answer) != None):
                    break
            else:  # Choose one option
                if (answer.upper() == 'Q'):
                    quit()
                if (answer.upper() in list(options.keys())):
                    break
            answer = input(Console.ERROR)
        return answer


console = Console()
