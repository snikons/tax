#!/usr/bin/env python3
# author: snikons


import csv
import json
import sys

help_msg = '''Calculates tax on capital gains from shares for the year 2024.
Supported Python version: 3.12.5 or later
Syntax: python3 ltcapgains.py <txn_file> <state>

txn_file must be a CSV file with the following columns
num,cb,fmv,perf
num: Number of shares to sell
cb: Cost basis per share
fmv: Fair market value
perf: Expected annual performance percentage to calculate potential growth

state can be one of the following
ca'''

txn_schema = {
    'num': int,
    'cb': float,
    'fmv': float,
    'perf': float
}

def calc_fed_tax(gain):
    if gain < 0: return 0
    if gain <= 94050: return 0
    if gain <= 583750: return gain * 15 / 100
    return gain * 20 / 100

def calc_ca_tax(gain):
    if gain < 0: return 0
    if gain <= 17864: return gain * 1 / 100
    if gain <= 42350: return gain * 2 / 100
    if gain <= 66842: return gain * 4 / 100
    if gain <= 92788: return gain * 6 / 100
    if gain <= 117268: return gain * 8 / 100
    if gain <= 599016: return gain * 9.3 / 100
    if gain <= 718814: return gain * 10.3 / 100
    if gain <= 1198024:
        return (gain * 11.3 / 100) + max(0, gain - 1000000) * 1 / 100
    return (gain * 12.3 / 100) + max(0, gain - 1000000) * 1 / 100

state_calc = {
    'ca': calc_ca_tax
}

def calc_tax(txn, state):
    tax = {
        'income': 0.0,
        'gain': 0.0,
        'state_tax': 0.0,
        'fed_tax': 0.0,
        'total_tax': 0.0
    }
    tax['income'] = txn['fmv'] * txn['num']
    tax['gain'] = round((txn['fmv'] - txn['cb']) * txn['num'], 2)
    if tax['gain'] >= 0:
        tax['fed_tax'] = round(calc_fed_tax(tax['gain']), 2)
        tax['state_tax'] = round(state_calc[state](tax['gain']), 2)
        tax['total_tax'] = round(tax['fed_tax'] + tax['state_tax'], 2)
    txn |= tax
    return txn['total_tax']

def normalize_txn(txn):
    for key in txn:
        if key in txn_schema:
            txn[key] = txn_schema[key](txn[key])

def main():
    global help_msg
    if sys.argv[1] in { '-h', '-help', '--help', 'help' }:
        print(help_msg)
        return

    filename = sys.argv[1]
    state = sys.argv[2]
    report = {
        'year': 2024,
        'filing': 'married filing jointly',
        'state': state,
        'gain': 0.0,
        'state_tax': 0.0,
        'fed_tax': 0.0,
        'total_tax': 0.0,
        'tax_percentage': 0.0,
        'income': 0.0,
        'net_income': 0.0,
        'potential_growth': 0.0,
        'txn': [],
    }
    gain = 0
    state_tax = 0
    fed_tax = 0
    income = 0
    potential_growth = 0

    with open(filename) as infile:
        reader = csv.DictReader(infile)
        for txn in reader:
            normalize_txn(txn)
            calc_tax(txn, state)
            state_tax += txn['state_tax']
            fed_tax += txn['fed_tax']
            income += txn['income']
            gain += txn['gain']
            report['txn'].append(txn)
            txn['potential_growth'] = round(txn['income'] * txn['perf'] / 100, 2)
            potential_growth += txn['potential_growth']

    report['gain'] = gain
    report['state_tax'] = state_tax
    report['fed_tax'] = fed_tax
    report['total_tax'] = state_tax + fed_tax
    report['income'] = income
    report['net_income'] = income - report['total_tax']
    report['tax_percentage'] = round(report['total_tax'] * 100 / gain, 2)
    report['potential_growth'] = potential_growth
    print(json.dumps(report, indent=4))

if __name__ == "__main__":
    main()

