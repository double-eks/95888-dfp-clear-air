import os

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


def genFieldQuery():
    responses = ['yearstart', 'locationabbr', 'question',
                 'datavalueunit', 'datavaluetype', 'datavalue',
                 'stratificationcategory1', 'stratification1']
    fields = ', '.join(responses)
    return fields


def genClauseQuery(state: str):
    location = f'(locationabbr = "{state.upper()}")'
    value = '(datavalue IS NOT NULL)'
    # typeClause = genTextWhereClause(
    #     'datavaluetype', 'OR', 'Age-adjusted Rate', 'Age-adjusted Prevalence')
    typeClause = '(datavaluetype = "Number")'
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
        print(len(self.df))

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
                    label=questionDict[name], marker='.')
        ax.legend(fontsize=10, loc='upper left')
        plt.show()

    def demography(self):
        questionDict = {
            'Asthma mortality rate': 'Asthma Mortality Rate',
            'Current asthma prevalence among adults aged >= '
            '18 years': 'Prevalence of Adults with Current Asthma (%)'}
        groupsDf = self.df[self.df.Demography != 'Overall']
        questions = groupsDf.question.unique()
        groups = groupsDf.Demography.unique()
        xTicks = groupsDf.index.unique()
        yTicks = np.linspace(0, 35, 11)

        fig, axs = plt.subplots(nrows=len(questions),
                                ncols=len(groups), figsize=(8, 8))

        for row in range(len(questions)):
            rawQuestion = questions[row]
            questionDf = groupsDf.loc[groupsDf.question == rawQuestion, :]
            for col in range(len(groups)):
                currAx = axs[row, col]
                currGroup = groups[col]
                subDf = questionDf.loc[questionDf.Demography == currGroup, :]
                currQuestion = questionDict[rawQuestion]
                currAx.grid(True, linestyle=self.dash, alpha=0.5)
                print(currQuestion, currGroup)
                print(subDf.Group.unique())
                print('\n\n')
                for name, group in subDf.groupby('Group'):
                    currAx.plot(group.index, group.Value,
                                label=name, marker='.')
                currAx.legend(title=currGroup, loc='upper left', fontsize=7)
                currAx.set_xticks(xTicks)
                currAx.set_xticklabels(xTicks, rotation=45, fontsize=9)
                currAx.set_yticks(yTicks)
                currAx.set_yticklabels(yTicks, fontsize=9)
                if (col == 0):
                    currAx.set_ylabel(currQuestion, fontweight='bold')
                if (row == 1):
                    currAx.set_xlabel(subDf.index.name,
                                      fontweight='bold')

        fig.suptitle('Demographic Patterns of Adults with Current Asthma '
                     f'({xTicks[0]}-{xTicks[-1]})',
                     fontweight='bold')
        fig.tight_layout()
        # plt.show()

    def zScoreAx(self, ax, xRange):
        ax.fill_between(xRange, -1, 1, alpha=0.1, color='gray')
        ax.axhline(y=-1, linewidth=1, linestyle=self.dash,
                   color='black', alpha=0.5)
        ax.axhline(y=1, linewidth=1, linestyle=self.dash,
                   color='black', alpha=0.5)


pa = cdcAPI('PA')
# pa.overallTrend()
pa.demography()
# pa.demography('Race/Ethnicity')
# df = pa.df

# new = df[df.question == 'Asthma mortality rate']
# new2 = new[new.Demography == 'Race/Ethnicity']


# print(new2.to_markdown())
