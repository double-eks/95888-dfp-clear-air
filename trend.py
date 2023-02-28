import os

import numpy as np

os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"

import matplotlib.pyplot as plt
import pandas as pd
from sodapy import Socrata


class cdcAPI:

    def __init__(self, state: str):
        self.start, self.end = 2011, 2020
        self.titleSuffix = f'in {state} ({self.start}-{self.end})'
        self.xTicks = list(range(self.start, self.end + 1))
        self.state = state
        self.dash = '--'
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
        df = df.astype({'datavalue': float, 'yearstart': int})
        df = df.rename(columns={'yearstart': 'Year',
                                'locationabbr': 'State',
                                'datavaluetype': 'Type',
                                'datavalue': 'Rate',
                                'datavalueunit': 'Unit',
                                'stratificationcategory1': 'Category',
                                'stratification1': 'Subgroup'})
        df['Factor'] = types
        df = df.set_index('Year')
        self.df = df.sort_index()

    # def overallTrend(self):
    #     questionDict = {'Asthma mortality rate': 'Mortality Rate',
    #                     'Current asthma prevalence among '
    #                     'adults aged >= 18 years': 'Prevalence among Adults'}
    #     overallDf = self.df[self.df.Demography == 'Overall']

    #     fig, ax = plt.subplots()
    #     xTicks = overallDf.index.unique()
    #     ax.set_title(
    #         f'Asthma Trend in {self.state} '
    #         f'({xTicks.values.min()}-{xTicks.values.max()})',
    #         fontweight='bold')
    #     ax.set_xlabel('Year', fontweight='bold')
    #     ax.set_ylabel('Z-score Standardization', fontweight='bold')
    #     ax.set_xticks(xTicks)
    #     ax.set_ylim(-2, 2)
    #     ax.grid(True, linestyle=self.dash, alpha=0.5)
    #     self.zScoreAx(ax, xTicks)

    #     for name, group in overallDf.groupby('question'):
    #         data = group.Value
    #         zscore = (data - data.mean(numeric_only=True)) / \
    #             data.std(numeric_only=True)
    #         ax.plot(zscore.index, zscore.values,
    #                 label=questionDict[name], marker='.')
    #     ax.legend(fontsize=10, loc='upper left')
    #     plt.show()

    def demography(self):
        # df = self.df[self.df.Category != 'Overall']
        df = self.df
        factors = df.Factor.unique()
        categoriesArr = df.Category.unique()
        subs = np.delete(categoriesArr,
                         np.where(categoriesArr == 'Overall')[0])
        fig, axs = plt.subplots(nrows=len(factors),
                                ncols=len(subs), figsize=(8, 8))

        for row in range(len(factors)):
            rowName = 'Factor'
            rowDf = filterDf(df, rowName, factors[row])
            yTitle = '{} ({})'.format(rowDf.Type.unique()[0],
                                      rowDf.Unit.unique()[0])
            for col in range(len(subs)):
                colName = 'Category'
                colField = subs[col]
                currAx = axs[row, col]
                currAx.grid(True, axis='y', linestyle=self.dash, alpha=0.5)
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
        overallDf = rowDf.loc[rowDf[colName] == 'Overall', :]
        colDf = rowDf.loc[rowDf[colName] == colField, :]
        subField = 'Subgroup'
        yMax = int(rowDf.Rate.values.max()) + 3
        yTicks = np.linspace(0, yMax, 11).round(1)
        yValues = []
        legendCol = 3 if (len(colDf[subField].unique()) <= 2) else 2

        ax.fill_between(self.xTicks, 0, overallDf.Rate.values,
                        color='lightgray', alpha=0.3)

        ax.plot(overallDf.index, overallDf.Rate, linestyle='dashed',
                label='Average', color='gray', linewidth=1)
        for name, subgroup in colDf.groupby(subField):
            line = ax.plot(subgroup.index, subgroup.Rate,
                           label=name, marker='.')
            yValues.append(subgroup.Rate.values)
            lineColot = line[0].get_color()
            self.annoateAx(ax, subgroup.Rate.values, lineColot)

        if (fill):
            ax.fill_between(self.xTicks, yValues[0], yValues[1],
                            color='gray', alpha=0.2)

        ax.set_xticks(self.xTicks)
        ax.set_xticklabels(self.xTicks, rotation=45, fontsize=7)
        ax.set_yticks(yTicks)
        ax.set_yticklabels(yTicks, fontsize=7)
        ax.legend(title=colField, loc='lower right', ncol=legendCol,
                  title_fontsize=7, fontsize=6)

    def annoateAx(self, ax: plt.Axes, yValues, lineColor):
        xMax = self.xTicks[yValues.argmax()]
        xMin = self.xTicks[yValues.argmin()]
        yMax, yMin = yValues.max(), yValues.min()
        ax.annotate(yMax, xy=(xMax, yMax), xytext=(-6, 6),
                    textcoords='offset points', color=lineColor, fontsize=7)
        ax.annotate(yMin, xy=(xMin, yMin), xytext=(-6, -10),
                    textcoords='offset points', color=lineColor, fontsize=7)

    def zScoreAx(self, ax, xRange):
        ax.fill_between(xRange, -1, 1, alpha=0.1, color='gray')
        ax.axhline(y=-1, linewidth=1, linestyle=self.dash,
                   color='black', alpha=0.5)
        ax.axhline(y=1, linewidth=1, linestyle=self.dash,
                   color='black', alpha=0.5)


def filterDf(df: pd.DataFrame, field: str, target: str):
    selected = df.loc[df[field] == target, :]
    return selected


pa = cdcAPI('CA')
pa.demography()
# pa.overallTrend()
# pa.demography('Race/Ethnicity')
# df = pa.df

# new = df[df.question == 'Asthma mortality rate']
# new2 = new[new.Demography == 'Race/Ethnicity']


# print(new2.to_markdown())
