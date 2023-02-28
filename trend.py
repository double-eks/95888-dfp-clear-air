import os

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


def genFieldQuery():
    responses = ['yearstart', 'locationabbr', 'question',
                 'datavalueunit', 'datavaluetype', 'datavalue',
                 'stratificationcategory1', 'stratification1']
    fields = ', '.join(responses)
    return fields


def genClauseQuery(state: str):
    location = f'(locationabbr = "{state.upper()}")'
    value = '(datavalue IS NOT NULL)'
    typeClause = genTextWhereClause(
        'datavaluetype', 'OR', 'Age-adjusted Rate', 'Age-adjusted Prevalence')
    questionClause = genTextWhereClause(
        'question', 'OR', 'Asthma mortality rate',
        'Current asthma prevalence among adults aged >= 18 years')
    clause = ' AND '.join([location, value, typeClause, questionClause])
    return clause


def genTextWhereClause(field: str, operator: str, *args):
    conditions = []
    for arg in args:
        currCondition = '{} = "{}"'.format(field, arg)
        conditions.append(currCondition)
    mergedClause = f' {operator} '.join(conditions)
    mergedClause = f'({mergedClause})'
    return mergedClause


def convertResponse(response):
    df = pd.DataFrame.from_records(response)
    df = df.rename(columns={'yearstart': 'Year',
                            'locationabbr': 'State',
                            'datavaluetype': 'Type',
                            'datavalue': 'Value',
                            'datavalueunit': 'Unit',
                            'stratificationcategory1': 'Demography',
                            'stratification1': 'Group'})
    factor = ['Mortality Rate' if 'mortality' in df.question[i] else
              'Adult Prevalence' for i in range(len(df.question))]
    df.loc[:, 'question'] = factor
    df = df.astype({'Value': float, 'Year': int})
    df = df.set_index('Year')
    df = df.sort_index()
    return df


class cdcAPI:

    def __init__(self, state: str):
        client = Socrata(domain='chronicdata.cdc.gov',
                         app_token='S1j1YaUvwuS3NZh6FDtLeDDFs',
                         username='xiaoxu@andrew.cmu.edu',
                         password='mqanS3iXwPfR2!E')
        datasetID = 'us8e-ubyj'
        clause = genClauseQuery(state)
        fields = genFieldQuery()
        response = client.get(datasetID, where=clause, select=fields)
        self.df = convertResponse(response)
        self.start, self.end = 2010, 2020
        self.state = state
        self.dash = '--'
        self.titleSuffix = f'in {self.state} ({self.start}-{self.end})'

    def overallTrend(self):
        ax = self.plotTemplate(title='Asthma Trend', zscore=True,
                               xLabel='Year', yLabel='Z-score Standardization',
                               xLim=(self.start, self.end), yLim=(-2, 2),
                               xTicks=list(range(self.start, self.end + 1)))
        overallDf = self.df[self.df.Demography == 'Overall']
        for name, group in overallDf.groupby('question'):
            data = group.Value
            zscore = (data - data.mean(numeric_only=True)) / \
                data.std(numeric_only=True)
            ax.plot(zscore.index, zscore.values, label=name, marker='o')
        ax.legend(fontsize=10, ncol=2, loc='upper left')
        plt.show()

    def plotTemplate(self, title: str, xLabel: str, yLabel: str,
                     xLim, yLim, xTicks, grid: bool = True, zscore: bool = False):
        fig, ax = plt.subplots()
        ax.set_title(f'{title} {self.titleSuffix}', fontweight='bold')
        ax.set_xlabel(xLabel, fontweight='bold')
        ax.set_ylabel(yLabel, fontweight='bold')
        ax.set_xlim(xLim)
        ax.set_ylim(yLim)
        ax.set_xticks(xTicks)
        if (grid):
            ax.grid(True, linestyle=self.dash, alpha=0.5)
        if (zscore):
            self.zScoreAx(ax, xTicks)
        return ax

    def zScoreAx(self, ax, xRange):
        ax.fill_between(xRange, -1, 1, alpha=0.1, color='gray')
        ax.axhline(y=-1, linewidth=1, linestyle=self.dash, alpha=0.5)
        ax.axhline(y=1, linewidth=1, linestyle=self.dash, alpha=0.5)
