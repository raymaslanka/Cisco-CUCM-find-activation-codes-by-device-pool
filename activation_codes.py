# -*- coding: utf-8 -*-

# Zeep serves as the SOAP client for the CUCM AXL communication
# we could do everything with requests but Zeep simplifies it drastically
from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.exceptions import Fault
from zeep.plugins import HistoryPlugin
# requests is used for basic communication needs with CUCM
from requests import Session
from requests.auth import HTTPBasicAuth
# urllib3 is dealing with SSL checks when commincating with CUCM
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
# lxml helps with pretty printing during error handling
from lxml import etree
# datetime makes epoch time readable
import datetime


disable_warnings(InsecureRequestWarning)


# user specific input
username = 'administrator'
password = 'ciscopsdt'
host = '10.10.20.1'
device_pool = 'Default'


# note: Zeep 4.1.0 and python 3.9.1 does not like the "file://" prefix when identifying the wsdl path (?)
# wsdl = 'file://C:/Users/Administrator/Documents/Cisco/CUCM/axlsqltoolkit/schema/125/AXLAPI.wsdl'
wsdl = 'C:/Users/Administrator/Documents/Cisco/CUCM/axlsqltoolkit/schema/125/AXLAPI.wsdl'
location = 'https://{host}:8443/axl/'.format(host=host)
binding = "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding"


# The session disables certificate validation
# this is a bad idea in production
session = Session()
session.verify = False
session.auth = HTTPBasicAuth(username, password)


# Zeep being used as SOAP client to simplify everything
transport = Transport(cache=SqliteCache(), session=session, timeout=20)
history = HistoryPlugin()
client = Client(wsdl=wsdl, transport=transport, plugins=[history])
service = client.create_service(binding, location)


# pretty print communication history when things go bad
def show_history():
    for item in [history.last_sent, history.last_received]:
        print(etree.tostring(item["envelope"], encoding="unicode", pretty_print=True))


# find activation codes in CUCM 
# we find all the codes since the list should be realtively short
def list_activation_codes():
    try:
        resp = service.listPhoneActivationCode(searchCriteria={'phoneName': '%'}, 
                                returnedTags={'activationCode': '', 'activationCodeExpiry': '', 'phoneName': '', 'phoneDescription': '', 'phoneModel': '', 'enableActivationId': '', 'userId': ''})
        return resp
    except Fault:
        show_history()


# find phones in CUCM
# we list only the phone with the name provided
def list_phones(name):
    try:
        resp = service.listPhone(searchCriteria={'name': name}, 
                                returnedTags={'name': '','devicePoolName': ''})
        return resp
    except Fault:
        show_history()


# get the list of activation codes
# then for each activation code, find the device pool name of the phone with that code
# if the device pool is the one we are interested in, print the code and phone info in a nice list
print('Name, Device Pool, Description, Model, Activation Code, Code Expiry')
code_list = list_activation_codes()['return'].phoneActivationCode
for phoneActivationCode in code_list:
    phone_list = list_phones(phoneActivationCode.phoneName)['return'].phone
    for phone in phone_list:
        if phone.devicePoolName._value_1 == device_pool:
            print(phone.name, phone.devicePoolName._value_1, phoneActivationCode.phoneDescription, phoneActivationCode.phoneModel, phoneActivationCode.activationCode[:4] + '-' + phoneActivationCode.activationCode[4:8] + '-' + phoneActivationCode.activationCode[8:12] + '-' + phoneActivationCode.activationCode[12:16], datetime.datetime.fromtimestamp(phoneActivationCode.activationCodeExpiry), sep=', ')

