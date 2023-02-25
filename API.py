import json

import requests
from numpy import int0


def loopUpCityState(zipCode: int):
    response = requestByZip(zipCode)
    return response


def requestByZip(zipCode: int):
    SCHEME = 'https://'
    HOST = 'secure.shippingapis.com'
    PATH = '/ShippingAPI.dll?'
    API = 'api'
    USERID = '134CARNE2141'
    xml = '''\
&XML=<CityStateLookupRequest USERID="{}">\
<ZipCode ID="0"><Zip5>{}</Zip5></ZipCode></CityStateLookupRequest>'''
    url = SCHEME + HOST + PATH + API + xml.format(USERID, zipCode)
    return requests.get(url)


# a = (loopUpCityState(15213))


# #  <CityStateLookupRequest USERID="XXXXXXXXXXXX">

# #  <ZipCode ID='0'>

# #  <Zip5>20024</Zip5>

# #  </ZipCode>

# #  </CityStateLookupRequest>
