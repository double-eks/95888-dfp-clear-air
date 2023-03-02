import os

os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"

import copy
import logging
import re
from urllib.request import urlopen

import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import progressbar
from bs4 import BeautifulSoup, Tag
from matplotlib.axes import Axes

from airnow import AirNow, EpaAQS
from console import Console


def webScraping(url: str) -> BeautifulSoup:
    domain = re.search(r'(?<=https://www.)[^/]*(?=/)', url).group()
    console.loading(domain)
    html = urlopen(url)
    return BeautifulSoup(html.read(), "lxml")


def requestAQS(start: int = 2010, end: int = 2021):
    widget = copy.copy(console.widget)
    widget[0] = widget[0].format('EPA AQS')
    dfList = []
    for yr in progressbar.progressbar(range(start, end + 1),
                                      widgets=widget, redirect_stdout=True):
        df = apiAQS.requestSingleYr(yr, console.city, console.state)
        dfList.append(df)
    return pd.concat(dfList)


def aqiVizPage():
    dfs = requestAQS(start=2021)
    singleYr = dfs.loc[(dfs.index.year == 2021), :]

    # aqiTrackerByYear(singleYr, 2021, fontweight='bold', fontsize=10)
    aqiDistribution(singleYr, 2021, fontweight='bold', fontsize=10)
    return
    # ax.set_xlabel('Dates')
    # aqsAPI.drawTrendPlot(ax, yrDf)
    # homepage()


def aqiTrackerByYear(singleYrDf: pd.DataFrame, singleYr: int, **kwargs):
    fig = plt.figure(tight_layout=True)
    fig.set_size_inches(8, 6)
    gs = gridspec.GridSpec(2, 2)

    dailyAqiAx = fig.add_subplot(gs[:1, :])
    cumDayAx = fig.add_subplot(gs[1:, :])

    dailyAqiPlot(dailyAqiAx, singleYrDf['AQI'], singleYr)
    cumGoodDayPlot(cumDayAx, singleYrDf['Cum Days'])

    dailyAqiAx.legend(ncol=2, fontsize=8, loc='upper left')
    cumDayAx.legend(fontsize=8, loc='upper left')
    dailyAqiAx.set_ylabel('Daily AQI', **kwargs)
    cumDayAx.set_ylabel('Cumulative Days', **kwargs)
    dailyAqiAx.set_xlabel(f'Air Quality Annual Trend', **kwargs)
    cumDayAx.set_xlabel(f'Cumulative Good AQI Days (AQI<50)', **kwargs)

    fig.suptitle('Air Quality Time Series Analysis of Air Quality '
                 f'in {console.city}, {console.state} ({singleYr})',
                 fontsize=13, fontweight='bold')


def dailyAqiPlot(ax: Axes, sAQI: pd.Series, yr: int):
    moving = 7
    lagging = 14
    movingAvg = sAQI.rolling(window=moving).mean()
    laggingAvg = sAQI.rolling(window=lagging).mean()
    avgMax = (movingAvg.max() // 50 + 1) * 50

    ax.grid(True, linestyle='dotted')
    ax.plot(sAQI.index, laggingAvg, linewidth=10, alpha=0.3,
            label=f'{lagging}-lagging-day moving average', color='gray')
    ax.plot(sAQI.index, movingAvg, linewidth=3, alpha=0.8,
            label=f'{moving}-day moving average', color='deepskyblue')
    ax.axhline(avgMax, 0, 1, linestyle='dashed',
               label='Worst cap of moving average', color='#ff7e00')
    ax.plot(sAQI, linewidth=1.2, label=str(yr), color='steelblue')

    apiAQS.yAxisByAQI(ax, sAQI)
    fmtDateAxis(ax, sAQI)
    return


def cumGoodDayPlot(ax: Axes, sCumDay: pd.Series):
    interval = 50
    sumDay = sCumDay.max()
    breakPoint = sumDay // interval * interval
    goodDays = [day for day in range(0, breakPoint, interval)]
    badDays = [day for day in range(breakPoint, 365, interval)]
    dayTicks = copy.copy(goodDays)
    dayTicks.extend(badDays[1:])
    dayTicks.extend([sumDay, 365])

    ax.grid(True, linestyle='dotted')
    ax.fill_between(sCumDay.index, sumDay, 365, alpha=0.1,
                    color='#ff7e00')
    ax.axhline(sumDay, 0, 1, color='#ff7e00')
    ax.plot(sCumDay, linewidth=3,
            label='Cumulative Good Days (AQI<50)', color='steelblue')

    ax.set_ylim((0, 365))
    ax.set_yticks(dayTicks)
    fmtDateAxis(ax, sCumDay)
    return


def fmtDateAxis(ax: Axes, s: pd.Series):
    dateLim = (s.index[0], s.index[-1])
    ax.set_xlim(dateLim)
    ax.tick_params(axis='both', labelsize=8)
    ax.tick_params(axis='x', rotation=15)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))


def aqiDistribution(singleYrDf: pd.DataFrame, singleYr: int, **kwargs):
    fig = plt.figure(tight_layout=True)
    fig.set_size_inches(6.4, 6.4)
    gs = gridspec.GridSpec(2, 3)

    heatMapAx = fig.add_subplot(gs[:, :1])
    # pollutantAx = fig.add_subplot(gs[3:6, :1])
    # scaleAx = fig.add_subplot(gs[6:, :])
    calendarHeatMap(heatMapAx, singleYrDf,
                    singleYrDf.index.month, singleYrDf.index.day, 'Level')

    return
    categorizedBar(monthTileAx, singleYrDf, 'Month', 'Level', 7)
    categorizedBar(monthTileAx, singleYrDf,
                   'Defining Parameter', 'Level', 20)
    # aqiLegend(scaleAx)

    monthTileAx.set_xticklabels(singleYrDf.index.unique().strftime('%b'))
    # pollutantAx.set_ylabel('Day Count of AQI Level', **kwargs)

    title = 'AQI Cumulative Days by {}'
    monthTileAx.set_xlabel(title.format('Month'), **kwargs)
    pollutantAx.set_xlabel(title.format(
        'Primary Pollutant'), **kwargs)
    scaleAx.set_xlabel('Air Quality Index (AQI) Categorization', **kwargs)

    fig.suptitle('Air Quality Time Series Analysis of Air Quality '
                 f'in {console.city}, {console.state} ({singleYr})',
                 fontsize=13, fontweight='bold')


def calendarHeatMap(ax: Axes, df: pd.DataFrame,
                    xField: str, yField: str, vField: str):
    # print(df.to_markdown())
    dataDf = df.pivot_table(index=yField, columns=xField, values=vField)
    width = 1
    setFrame(ax, 'none')
    xLim = (0, len(dataDf.columns))
    yLim = (0, len(dataDf.index))
    ax.set_xlim(xLim)
    ax.set_ylim(yLim)
    ax.tick_params(labelsize=8, length=0)
    for x in range(len(dataDf.columns)):
        for y in range(len(dataDf.index)):
            level = dataDf.iloc[y, x]
            if (level > 0):
                level = int(level)
                fill = aqiPalette.Monochrome[level]
            else:
                fill = 'lightgray'
            ax.bar(x=x, bottom=y, height=width, width=width, align='edge',
                   color=fill, edgecolor='white', linewidth=0.4)
    # matrix = [[(x + width, y + width) for x in range(len(data.columns))]
    #           for y in range(len(data.index))]

    # print(matrix)
    return
    matrix = [[(1 + row, 1 + col) for col in range(len(calendar.index))]
              for row in range(len(calendar.columns))]
    width = 1
    xLim = (0, (matrix[0][-1][1]))
    yLim = (0, (matrix[-1][0][0]))
    for row in range(len(matrix)):
        for col in range(len(matrix[0])):
            x, y = matrix[row][col]
            level = (calendar.loc[y, x])
            if (level > 0):
                level = int(level)
                color = aqiPalette.Color[level]
            else:
                color = 'gray'
            ax.bar(x=y - width, bottom=x - width,
                   height=width, width=width, color=color, edgecolor='white', align='edge')
    # print(xLim)
    # print(yLim)
    # return
    # print(matrix)


def setFrame(ax: Axes, *args):
    ax.spines['top'].set_color(*args)
    ax.spines['bottom'].set_color(*args)
    ax.spines['left'].set_color(*args)
    ax.spines['right'].set_color(*args)


def categorizedBar(ax: Axes, df: pd.DataFrame, xField: str, yField: str,
                   labelLimit: int):
    # np.arange(len(df[xField].unique()))
    # width = 0.3
    days = df.groupby(xField)[yField].value_counts()
    df = days.unstack()
    print(df.to_markdown())
    width = 0.25  # the width of the bars
    multiplier = 0

    x = np.arange(len(df.index))
    for col in df.columns:
        offset = width * multiplier
        rects = ax.bar(x + offset, df[col], width, label=col)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    ax.legend()

    # df.fillna(0)
    # print(df.to_markdown())
    # print(days.index.shape)
    # print(df.values.shape)

    return
    print(pd.DataFrame(df.index, columns=df.columns).to_markdown())
    for col in df.columns:
        ax.bar(df.index, df[col])
        print(df[col].to_markdown())
        # return
    ax.bar(np.ones((3, 4)), df.values)
    # ax.legend()
    # test.plot(kind='bar')
    # for xName, xBarDf in df.groupby(xField):
    # subBarDf = df.groupby(xField)[yField].value_counts()
    # subBarDf.plot(kind='bar')
    # ax.legend()

    print(days.index)
    df = df.copy()
    df = df.pivot(index=yField, columns=xField, values='Date')
    print(df.to_markdown())

    xBarDf.groupby(yField)[yField].plot()

    return
    bottom = 0
    color = aqiPalette.Color[yName]
    v = len(subgroup.index)
    b = ax.bar(xName, v, width,
               label=yName, color=color, bottom=bottom)

    bottom += v
    if (v > labelLimit):
        ax.bar_label(b, label_type='center', fontsize=8)
    ax.set_xticks(df[xField].values)
    ax.tick_params(labelsize=8)


def aqiLegend(ax: Axes):
    xTicks = [0]
    ax.set_yticks([])
    ax.set_ylim((0, 3))
    for i in aqiPalette.index:
        color = aqiPalette.Color[i]
        x1 = aqiPalette.Bottom[i]
        x2 = aqiPalette.Cap[i]
        scale = aqiPalette.Category[i]
        xTicks.append(x2)
        ax.fill_betweenx(np.linspace(0, 1), x1, x2, color=color)
        if (scale == 'Unhealthy for Sensitive Groups'):
            scale = 'Sensitive'
        ax.text(x1, 1.5, scale, fontsize=8)
    # levelCap.append(aqiPalette.Cap.iloc[-1])
    ax.set_xticks(xTicks)
    ax.set_xlim((xTicks[0], xTicks[-1]))
    ax.tick_params(labelsize=8)
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    # Rectangle((bottom, 0), cap, 10, color=color, fill=True)


def homepage(new: bool = False):
    return


if __name__ == "__main__":

    console = Console()

    apiAQS = EpaAQS()
    aqiPalette = apiAQS.palette
    aqiVizPage()

    plt.show()
    # plt.close('all')
