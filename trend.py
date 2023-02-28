import os

from numpy import tile

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

    def overallTrend(self):
        questionDict = {'Asthma mortality rate': 'Mortality Rate',
                        'Current asthma prevalence among '
                        'adults aged >= 18 years': 'Prevalence among Adults'}
        overallDf = self.df[self.df.Demography == 'Overall']

        fig, ax = plt.subplots()
        xTicks = overallDf.index.unique()
        ax.set_title(
            f'Asthma Trend in {self.state} '
            f'({xTicks.values.min()}-{xTicks.values.max()})',
            fontweight='bold')
        ax.set_xlabel('Year', fontweight='bold')
        ax.set_ylabel('Z-score Standardization', fontweight='bold')
        ax.set_xticks(xTicks)
        ax.set_ylim(-2, 2)
        ax.grid(True, linestyle=self.dash, alpha=0.5)
        self.zScoreAx(ax, xTicks)

        for name, group in overallDf.groupby('question'):
            data = group.Value
            zscore = (data - data.mean(numeric_only=True)) / \
                data.std(numeric_only=True)
            ax.plot(zscore.index, zscore.values,
                    label=questionDict[name], marker='o')
        ax.legend(fontsize=10, loc='upper left')
        plt.show()

    def demography(self, identity: str):
        questionDict = {
            'Asthma mortality rate': 'Asthma Mortality Rate',
            'Current asthma prevalence among adults aged >= '
            '18 years': 'Prevalence of Adults with Current Asthma'}
        subGroup = self.df[self.df.Demography == identity]
        subDf = subGroup[subGroup.question != 'Asthma mortality rate']
        xTicks = subDf.index.unique()

        fig, ax = plt.subplots()
        ax.set_title(f'Trend of Adult Asthma in {self.state}\n'
                     f'by {identity} '
                     f'({xTicks.values.min()}-{xTicks.values.max()})',
                     fontweight='bold')
        ax.set_xlabel('Year',
                      fontweight='bold')
        ax.set_ylabel('Prevalence of Adults with Current Asthma (%)',
                      fontweight='bold')
        ax.set_xticks(xTicks)
        ax.grid(True, linestyle=self.dash, alpha=0.5)

        for name, group in subDf.groupby('Group'):
            ax.plot(group.index, group.Value, label=name, marker='o')
            ax.legend(title=identity, fontsize=8, loc='upper left')
        plt.show()

    def zScoreAx(self, ax, xRange):
        ax.fill_between(xRange, -1, 1, alpha=0.1, color='gray')
        ax.axhline(y=-1, linewidth=1, linestyle=self.dash,
                   color='black', alpha=0.5)
        ax.axhline(y=1, linewidth=1, linestyle=self.dash,
                   color='black', alpha=0.5)


pa = cdcAPI('PA')
pa.overallTrend()
pa.demography('Gender')
pa.demography('Race/Ethnicity')
