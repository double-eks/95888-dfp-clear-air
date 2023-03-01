# %%
import os

os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# %%
# fig, ax = plt.subplots()
# background = 0.3
# ax.axhspan(0, 50, facecolor='#00e400', alpha=background)
# ax.axhspan(50, 100, facecolor='#ffff00', alpha=background)
# ax.axhspan(100, 150, facecolor='#ff7e00', alpha=background)
# ax.axhspan(150, 200, facecolor='#ff0000', alpha=background)
# ax.axhspan(200, 300, facecolor='#8f3f97', alpha=background)
# ax.axhspan(300, 500, facecolor='#7e0023', alpha=background)

# %%


def aqiColorDf():
    aqidict = {
        'color': ['#00e400', '#ffff00', '#ff7e00', '#ff0000', '#8f3f97', '#7e0023'],
        'aqi': [(0, 50), (50, 100), (100, 150), (150, 200), (200, 300), (300, 500)],
        'category': ['Good', 'Moderate', 'Unhealthy for Sensitive Groups',
                     'Unhealthy', 'Very Unhealthy', 'Hazardous'],
        'number': [i for i in range(1, 7)]
    }
    df = pd.DataFrame(aqidict)
    return df


# %%
import requests

url = 'https://aqs.epa.gov/data/api/dailyData/byCBSA?'
start = 20190101
end = 20191231
cityCode = 38300
pollutant = 88502
paraDict = {
    'email': 'xiaoxu@andrew.cmu.edu',
    'key': 'carmelgazelle91',
    'param': pollutant,
    'bdate': start,
    'edate': end,
    'cbsa': cityCode
}

response = requests.get(url, params=paraDict)
raw = response.json()

# %%
df = pd.DataFrame(raw['Data'])
df = df.dropna(subset='aqi')
# df = df.sort_values(['date_local', 'date_of_last_change'])
df = df.drop_duplicates(subset='date_local', keep='last')

# %%
dates = pd.to_datetime(df['date_local'])

df.to_csv('export/1.csv')

'''


# %%
worst = df.aqi.values.max()
best = df.aqi.values.min()
yStart = best // 10 * 10
yEnd = (worst//10+1)*10
yLim = (yStart, yEnd)

# %%

aqiLevelDf = aqiColorDf()
worstRange = tuple()
for row in aqiLevelDf.index:
    currAqiRange = aqiLevelDf.loc[row, 'aqi']
    currLevel = range(currAqiRange[0], currAqiRange[1])
    if (int(worst) in currLevel):
        worstRange = currAqiRange

# %%
fig, ax = plt.subplots()
ax.set_xlim(dates.min(), dates.max())
ax.set_ylim(0, 200)
ax.plot(dates, df.aqi.values)
plt.xticks(rotation=45)
plt.show




'''
