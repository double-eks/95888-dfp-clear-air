'''
Group 9: AirWise
Xiao Xu
xiaoxu@andrew.cmu.edu

Filename: asthmaindicator.py

Module: AsthmaIndicator specifically uses sodapy.Socrata to request data from CDC API (username / password embedded)

95-888 Data Focused Python
Spring 2023 Mini 3
'''

import os

os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sodapy import Socrata


class AsthmaIndicator:

    def __init__(self, state: str):
        self.start, self.end = 2011, 2020
        self.titleSuffix = f'in {state} ({self.start}-{self.end})'
        self.xTicks = list(range(self.start, self.end + 1))
        self.xLim = (self.start - 0.5, self.end + 0.5)
        self.state = state
        self.initQuestionDict()
        self.initClauseQuery()
        client = Socrata(domain='chronicdata.cdc.gov',
                         app_token='S1j1YaUvwuS3NZh6FDtLeDDFs',
                         username='xiaoxu@andrew.cmu.edu',
                         password='mqanS3iXwPfR2!E')
        datasetID = 'us8e-ubyj'
        fields = ['yearstart', 'locationabbr', 'question',
                  'datavalueunit', 'datavaluetype', 'datavalue',
                  'stratificationcategory1', 'stratification1']
        fields = ', '.join(fields)
        self.response = client.get(datasetID, where=self.clause, select=fields)
        self.convertResponse()

    def initQuestionDict(self):
        questionDict = {
            'Asthma mortality rate':
                ['Age-adjusted Rate',
                 'Asthma Mortality Rate'],
            'Current asthma prevalence among adults aged >= 18 years':
                ['Age-adjusted Prevalence',
                 'Prevalence of Adults with Current Asthma']}
        questionDf = pd.DataFrame(questionDict,
                                  index=['datavaluetype', 'rename'])
        self.qDict = questionDf

    def initClauseQuery(self):
        time = f'((yearstart >= {self.start}) AND (yearstart <= {self.end}))'
        location = f'(locationabbr = "{self.state.upper()}") '
        data = '(datavalue IS NOT NULL)'
        quesstions = ['(question = "{}")'.format(factor)
                      for factor in list(self.qDict.columns)]
        questionClause = ' OR '.join(quesstions)
        questionClause = '({})'.format(questionClause)
        self.clause = ' AND '.join([time, location, data, questionClause])

    def convertResponse(self):
        df = pd.DataFrame.from_records(self.response)
        typeRowFilter = []
        types = []
        for row in df.index:
            currQuestion = df.loc[row, 'question']
            currDataType = df.loc[row, 'datavaluetype']
            if (currDataType == self.qDict[currQuestion]['datavaluetype']):
                typeRowFilter.append(True)
                types.append(self.qDict[currQuestion]['rename'])
            else:
                typeRowFilter.append(False)
        df = df.loc[typeRowFilter, :]
        df['Factor'] = types
        df = df.astype({'datavalue': float, 'yearstart': int})
        df = df.rename(columns={'yearstart': 'Year',
                                'locationabbr': 'State',
                                'datavaluetype': 'Type',
                                'datavalue': 'Rate',
                                'datavalueunit': 'Unit',
                                'stratificationcategory1': 'Category',
                                'stratification1': 'Subgroup'})
        df = df.set_index('Year')
        self.df = df.sort_index()

    def trend(self):
        df = filterDf(self.df, 'Category', 'Overall')
        fig, ax = plt.subplots()
        ax.grid(True, axis='y', linestyle='dotted')
        ax.axhline(y=-1, linewidth=1, alpha=0.5,
                   linestyle='dashed', color='black')
        ax.axhline(y=1, linewidth=1, alpha=0.5,
                   linestyle='dashed', color='black', )
        ax.set_xlabel('Year', fontweight='bold')
        ax.set_ylabel('Z-score Standardization', fontweight='bold')
        ax.set_xlim(self.xLim)
        ax.set_xticks(self.xTicks)
        ax.fill_between(x=self.xLim, y1=-1, y2=1, alpha=0.1, color='gray')
        for name, group in df.groupby('Factor'):
            data = group.Rate
            zscore = (data - data.mean(numeric_only=True)) / \
                data.std(numeric_only=True)
            ax.plot(zscore.index, zscore.values,
                    label=name, linewidth=2, marker='o')
        ax.legend(title='Standardalized Asthma Indicator', loc='upper center',
                  title_fontsize=8, fontsize=8, ncol=2)
        ax.set_title(f'Asthma Trend {self.titleSuffix}', fontweight='bold')
        plt.show()

    def demography(self):
        df = self.df
        factors = df.Factor.unique()
        categoriesArr = df.Category.unique()
        subs = np.delete(categoriesArr,
                         np.where(categoriesArr == 'Overall')[0])
        fig, axs = plt.subplots(nrows=len(factors),
                                ncols=len(subs), figsize=(8, 8))

        for row in range(len(factors)):
            rowDf = filterDf(df, 'Factor', factors[row])
            yTitle = '{} ({})'.format(rowDf.Type.unique()[0],
                                      rowDf.Unit.unique()[0])
            for col in range(len(subs)):
                colName = 'Category'
                colField = subs[col]
                currAx = axs[row, col]
                currAx.grid(True, axis='y', linestyle='dotted')
                fill = True if (colField == 'Gender') else False
                self.drawGroupLines(currAx, colName, colField, rowDf, fill)
                if (row == 0):
                    xTitle = 'Asthma Indicators by {}'.format(colField)
                    currAx.set_title(xTitle, fontsize=9, fontweight='bold')
                if (col == 0):
                    currAx.set_ylabel(yTitle, fontsize=9)

        fig.suptitle('Demographic Patterns of Adults with Current Asthma '
                     f'{self.titleSuffix}', fontweight='bold')
        fig.tight_layout()
        plt.show()

    def drawGroupLines(self, ax: plt.Axes, colName: str, colField: str,
                       rowDf: pd.DataFrame, fill: bool = False):
        overallDf = filterDf(rowDf, colName, 'Overall')
        colDf = filterDf(rowDf, colName, colField)

        subField = 'Subgroup'
        yMax = int(rowDf.Rate.values.max()) + 3
        yTicks = np.linspace(0, yMax, 11).round(1)
        yValues = []
        legendCol = 3 if (len(colDf[subField].unique()) <= 2) else 2

        ax.fill_between(self.xTicks, 0, overallDf.Rate.values,
                        color='lightgray', alpha=0.3)

        ax.plot(overallDf.index, overallDf.Rate,
                label='Average', color='gray', linewidth=4, alpha=0.3)
        for name, subgroup in colDf.groupby(subField):
            line = ax.plot(subgroup.index, subgroup.Rate,
                           label=name, marker='.')
            yValues.append(subgroup.Rate.values)
            lineColot = line[0].get_color()
            self.annoateAx(ax, subgroup.Rate.values, fontsize=7,
                           color=lineColot, textcoords='offset points')

        if (fill):
            ax.fill_between(self.xTicks, yValues[0], yValues[1],
                            color='gray', alpha=0.2)
        ax.set_xlim(self.xLim)
        ax.set_xticks(self.xTicks)
        ax.set_ylim((0, yMax))
        ax.set_yticks(yTicks)
        ax.tick_params(axis='both', labelsize=7)
        ax.legend(title=colField, loc='lower right', ncol=legendCol,
                  title_fontsize=7, fontsize=6)

    def annoateAx(self, ax: plt.Axes, yValues, **kwargs):
        xMax = self.xTicks[yValues.argmax()]
        xMin = self.xTicks[yValues.argmin()]
        yMax, yMin = yValues.max(), yValues.min()
        ax.annotate(yMax, xy=(xMax, yMax), xytext=(-6, 6), **kwargs)
        ax.annotate(yMin, xy=(xMin, yMin), xytext=(-6, -10), **kwargs)


def filterDf(df: pd.DataFrame, field: str, target: str):
    return df.loc[df[field] == target, :]
