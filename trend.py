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


class Asthma_Indicator_CDC_API:
    def __init__(self, datasetID: str = 'us8e-ubyj') -> None:
        self.client = Socrata(domain='chronicdata.cdc.gov',
                              app_token='S1j1YaUvwuS3NZh6FDtLeDDFs',
                              username='xiaoxu@andrew.cmu.edu',
                              password='mqanS3iXwPfR2!E')
        self.dataset = datasetID

    def request(self, state: str):
        location = f'(locationabbr = "{state.upper()}")'
        value = '(datavalue IS NOT NULL)'
        typeTemplate = 'datavaluetype = "{}"'
        typeOptions = ['Number', 'Age-adjusted Rate',
                       'Age-adjusted Prevalence']
        types = [typeTemplate.format(s) for s in typeOptions]
        typeClause = f"({' OR '.join(types)})"
        clause = ' AND '.join([location, value, typeClause])
        print('\t\t', clause)
        responses = ['yearstart', 'locationabbr', 'locationdesc', 'topic',
                     'question', 'datavalueunit', 'datavaluetype', 'datavalue',
                     'stratificationcategory1', 'stratification1']
        fields = ', '.join(responses)

        response = self.client.get(self.dataset, where=clause, select=fields)
        df = pd.DataFrame.from_records(response)
        df = df.rename(columns={'yearstart': 'Year', 'locationdesc': 'State',
                                'question': 'Indicator', 'datavalue': 'Value',
                                'datavalueunit': 'Unit',
                                'datavaluetype': 'Date Type',
                                'stratificationcategory1': 'Demography',
                                'stratification1': 'Group'})
        return df


indicatorAPI = Asthma_Indicator_CDC_API()
test = indicatorAPI.request('PA')
print(test.to_markdown())
# print(test.loc[0])
# print(test.Value.isnull())

'''
Index(['yearstart', 'yearend', 'locationabbr', 'locationdesc', 'topic',
       'question', 'datavaluetype', 'stratificationcategory1',
       'stratification1', 'datavalueunit', 'datavalue'],
      dtype='object')
      
      '''

# Convert to pandas DataFrame

# url = 'https://chronicdata.cdc.gov/resource/ypj5-qvn4.json?yearstart=2017'
# url = 'https://chronicdata.cdc.gov/resource/us8e-ubyj.json?yearstart=2017'

# response = requests.get(url)
# raw = response.json()
# print(raw)


# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
# client = Socrata("chronicdata.cdc.gov", None)

# Example authenticated client (needed for non-public datasets):

# First 2000 results, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
