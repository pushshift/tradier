#!/usr/bin/env python3

import requests
from requests.adapters import HTTPAdapter
import datetime
import time
import logging
import ujson as json
import sys
import os

def getOptionExpirations(symbol):
    url = 'https://api.tradier.com/v1/markets/options/expirations'
    params = {'symbol':symbol}
    r = s.get(url, params=params)
    j = json.loads(r.text)
    expirations = []
    for expiration in j['expirations']['date']:
        expirations.append(expiration)
    return expirations

def getOptionChain(symbol,expiration):
    url = 'https://api.tradier.com/v1/markets/options/chains'
    params = {'symbol':symbol,'expiration':expiration}
    r = s.get(url, params=params)
    j = json.loads(r.text)
    symbols = []
    for option in j['options']['option']:
        symbols.append(option['symbol'])
    return symbols

def getSessionID():
    url = 'https://api.tradier.com/v1/markets/events/session'
    r = s.post(url)
    j = json.loads(r.text)
    sessionid = j['stream']['sessionid']
    return sessionid

def events(sessionid,symbols):
    url = 'https://stream.tradier.com/v1/markets/events'
    params = {'sessionid':sessionid,'linebreak':'true','symbols':','.join(symbols)}
    r = s.post(url,data=params,stream=True)
    for line in r.iter_lines():
        if line: # filter out keep-alive new lines
            data = json.loads(line)
            print(data,flush=True)

TRADIER_API_KEY = os.environ['TRADIER_API_KEY']
LOG = False

if LOG:
    logging.basicConfig(level=logging.DEBUG)

s = requests.Session()
s.mount('https://', HTTPAdapter(max_retries=1))
s.headers.update({'Authorization':'Bearer ' + TRADIER_API_KEY, 'Accept':'application/json'})
ticker = 'AMD'
expirations = getOptionExpirations(ticker)
option_chains = []

for expiration in expirations:
    symbols = getOptionChain(ticker,expiration)
    for symbol in symbols:
        option_chains.append(symbol)

option_chains.append(ticker)  # Add ticker to the options we want to stream
sessionid = getSessionID()
events(sessionid,option_chains)
