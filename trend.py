import os
from operator import index

import numpy as np

os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"

import matplotlib.pyplot as plt
import pandas as pd
from sodapy import Socrata

'''
Asthma Indictor Question Dictionary
    Hospitalizations for asthma
    Asthma mortality rate
    Emergency department visit rate for asthma
    Asthma prevalence among women aged 18-44 years
    Current asthma prevalence among adults aged >= 18 years
    Influenza vaccination among noninstitutionalized adults aged >= 65 years with asthma
    Influenza vaccination among noninstitutionalized adults aged 18-64 years with asthma
    Pneumococcal vaccination among noninstitutionalized adults aged 18-64 years with asthma
    Pneumococcal vaccination among noninstitutionalized adults aged >= 65 years with asthma
'''


class cdcAPI:

    def __init__(self, state: str):
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
                ['Age-adjusted Rate', 'Asthma Mortality Rate'],
            'Current asthma prevalence among adults aged >= 18 years':
                ['Age-adjusted Prevalence', 'Prevalence of Adults with Current Asthma'],
            'Emergency department visit rate for asthma':
                ['Age-adjusted Rate', 'Asthma ED Visit Rate'],
            'Hospitalizations for asthma':
                ['Age-adjusted Rate', 'Asthma Hospitalizations Rate']}
        questionDf = pd.DataFrame(questionDict,
                                  index=['datavaluetype', 'rename'])
        self.qDict = questionDf

    def initClauseQuery(self):
        location = f'(locationabbr = "{self.state.upper()}") '
        data = '(datavalue IS NOT NULL)'
        quesstions = ['(question = "{}")'.format(factor)
                      for factor in list(self.qDict.columns)]
        questionClause = ' OR '.join(quesstions)
        questionClause = '({})'.format(questionClause)
        self.clause = ' AND '.join([location, data, questionClause])

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
                                'stratificationcategory1': 'Demography',
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
        df = self.df[self.df.Demography != 'Overall']
        factors = df.Factor.unique()
        demos = df.Demography.unique()
        yMax = int(df.Rate.values.max()) + 1
        xTicks = df.index.unique()
        yTicks = np.linspace(0, yMax, 11).round(1)
        fig, axs = plt.subplots(nrows=len(factors),
                                ncols=len(demos), figsize=(8, 8))

        for row in range(len(factors)):
            currFactor = factors[row]
            factorDf = df.loc[df.Factor == currFactor, :]
            for col in range(len(demos)):
                currAx = axs[row, col]
                currDemo = demos[col]
                demoDf = factorDf.loc[factorDf.Demography == currDemo, :]
                currAx.grid(True, linestyle=self.dash, alpha=0.5)
                for name, subgroup in demoDf.groupby('Subgroup'):
                    currAx.plot(subgroup.index, subgroup.Rate,
                                label=name, marker='.')
                currAx.legend(title=currDemo, loc='lower right',
                              title_fontsize=7.5, fontsize=6, ncol=2)
                currAx.set_xticks(xTicks)
                currAx.set_xticklabels(xTicks, rotation=45, fontsize=8)
                currAx.set_yticks(yTicks)
                currAx.set_yticklabels(yTicks, fontsize=8)
                if (col == 0):
                    currAx.set_ylabel(currFactor, fontweight='bold')
                if (row == 1):
                    currAx.set_xlabel(demoDf.index.name,
                                      fontweight='bold')

        fig.suptitle('Demographic Patterns of Adults with Current Asthma '
                     f'({xTicks[0]}-{xTicks[-1]})',
                     fontweight='bold')
        fig.tight_layout()
        plt.show()

    def zScoreAx(self, ax, xRange):
        ax.fill_between(xRange, -1, 1, alpha=0.1, color='gray')
        ax.axhline(y=-1, linewidth=1, linestyle=self.dash,
                   color='black', alpha=0.5)
        ax.axhline(y=1, linewidth=1, linestyle=self.dash,
                   color='black', alpha=0.5)


pa = cdcAPI('PA')
pa.demography()
# pa.overallTrend()
# pa.demography('Race/Ethnicity')
# df = pa.df

# new = df[df.question == 'Asthma mortality rate']
# new2 = new[new.Demography == 'Race/Ethnicity']


# print(new2.to_markdown())
