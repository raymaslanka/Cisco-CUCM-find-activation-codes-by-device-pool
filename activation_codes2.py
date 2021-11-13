# -*- coding: utf-8 -*-
 
# using Zeep as a SOAP client to simplify vs using requests
from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.exceptions import Fault
from zeep.plugins import HistoryPlugin
# using requests for communication to CUCM
from requests import Session
from requests.auth import HTTPBasicAuth
# using urllib3 to avoid SSL checking against CUCM
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
# using lxml to pretty print error messages
from lxml import etree
# using datetime to make epoch time readable
import datetime
 
username = 'administrator'
password = 'ciscopsdt'
host = '10.10.20.1'
devicepool = "Default"

disable_warnings(InsecureRequestWarning)

# Zeep 4.1.0 and Python 3.9.1 doesn't like file:// prefix on wsdl path
#wsdl = 'file://C:/Users/Administrator/Documents/Cisco/CUCM/axlsqltoolkit/schema/125/AXLAPI.wsdl'
wsdl = 'C:/Users/Administrator/Documents/Cisco/CUCM/axlsqltoolkit/schema/125/AXLAPI.wsdl'
location = 'https://{host}:8443/axl/'.format(host=host)
binding = "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding"
 
# skip checking CUCM SSL certificates (bad idea in production)
session = Session()
session.verify = False
session.auth = HTTPBasicAuth(username, password)

# Zeep used for SOAP communications
transport = Transport(cache=SqliteCache(), session=session, timeout=20)
history = HistoryPlugin()
client = Client(wsdl=wsdl, transport=transport, plugins=[history])
service = client.create_service(binding, location)
 
# pretty print things when they blow up
def show_history():
    for item in [history.last_sent, history.last_received]:
        print(etree.tostring(item["envelope"], encoding="unicode", pretty_print=True))

# find all activation codes in CUCM 
def list_activation_codes():
    try:
        resp = service.listPhoneActivationCode(searchCriteria={'phoneName': '%'}, 
                                returnedTags={'activationCode': '', 'activationCodeExpiry': '', 'phoneName': '', 'phoneDescription': '', 'phoneModel': '', 'enableActivationId': '', 'userId': ''})
        return resp
    except Fault:
        show_history()

# find phones in CUCM by name and return the device pool 
def list_phones(name):
    try:
        resp = service.listPhone(searchCriteria={'name': name}, 
                                returnedTags={'name': '','devicePoolName': ''})
        return resp
    except Fault:
        show_history()

# find all the activation codes
# then for each code, find the phone's device pool 
# then if the device pool is the one we are looking for, print to screen comma delimited
code_list = list_activation_codes()['return'].phoneActivationCode
print('Name, Device Pool, Description, Model, Activation Code, Code Expiry')
for phoneActivationCode in code_list:
    phone_list = list_phones(phoneActivationCode.phoneName)['return'].phone
    for phone in phone_list:
        if phone.devicePoolName._value_1 == devicepool:
            print(phone.name, phone.devicePoolName._value_1, phoneActivationCode.phoneDescription, phoneActivationCode.phoneModel, phoneActivationCode.activationCode, datetime.datetime.fromtimestamp(phoneActivationCode.activationCodeExpiry), sep=', ')

