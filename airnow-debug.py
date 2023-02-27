import logging
import re
from datetime import datetime, timedelta
from urllib.request import urlopen

# import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, Tag

from airnow import AqiLegend
from console import Console

url = 'https://www.airnow.gov/?city=Pittsburgh&state=PA&country=USA'
path = 'AirNow.gov.html'
html = urlopen(url)
urlBs = BeautifulSoup(html.read(), "lxml")
urlWeather = urlBs.find('div', attrs={'class': 'weather-value'})
print(urlWeather)

# print('-' * 10)

# with open(path) as copy:
#     savedHtml = copy.read()
# localBs = BeautifulSoup(savedHtml, "html.parser")
# localWeather = localBs.find('div', attrs={'class': 'weather-value'})
# print(localWeather)


'''
</div>
      </div>
      <div class="strip-padding">
        <div id="nav-right-side-toolbar" class="nav-right-side-toolbar">
      <div id="nav-weather-tool" class="nav-tool">
    <div class="weather-degrees-value-wrapper" style="display: block;">
      <img class="weather-degrees" alt="weather degrees" src="./AirNow.gov_files/Weather_Degree_F.svg" style="display: inline;">
      <div class="weather-value" style="display: block;">33</div>
    </div>
    <div class="weather-icon" style="display: block;">
      <img alt="weather icon" src="./AirNow.gov_files/weather_icon_fair_day.svg">
    </div>
    <img class="weather-loading" alt="weather loading spinner" src="./AirNow.gov_files/30.svg" style="display: none;">
  </div>
'''
