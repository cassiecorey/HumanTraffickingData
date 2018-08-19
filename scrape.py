#!/usr/bin/env python3

"""
This file scrapes http://www.humantraffickingdata.org/
for Human Trafficking case and defendant data.

It stores the data as .json files in raw_json/

Author: Cassie Corey, cassianjanay@gmail.com
"""

import bs4,os,urllib,json,time
import pandas as pd
import numpy as np

base_url = "http://www.humantraffickingdata.org"

# Make sure folder exists for the json files
data_dir = "raw_json/"
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

# These are the URL identifiers the site uses
# Pretty convenient if you ask me...
print('Loading case numbers...')

if os.path.exists(data_dir+'case_numbers.txt'):
    with open(data_dir+'case_numbers.txt','r') as f:
        case_numbers = [l.strip() for l in f.readlines()]
else:
    case_numbers = []
    for i in range(1,37):
        base_page = urllib.request.urlopen(base_url+'/search?page={}'.format(i))
        base_soup = bs4.BeautifulSoup(base_page,'lxml')
        table = base_soup.table
        rows = table.find_all('tr')[1:]
        for row in rows:
            hrefs = row.find_all('a',href=True)
            if len(hrefs)<2:
                href = hrefs[0]['href']
            else:
                href = hrefs[1]['href']
            num = href.split('/')[-1]
            case_numbers.append(num)
    with open(data_dir+'case_numbers.txt','w+') as f:
        for num in case_numbers:
            f.write('{}\n'.format(num))

print('Found {} case(s).'.format(len(case_numbers)))
case_range = case_numbers

case_data = {}

def parse_table(soup_table):
    """Parses table, returns dict
    """
    keys = [th.string for th in soup_table.find_all('th')]
    rows = soup_table.find_all('tr')
    if len(rows) == 0 or len(rows)==1: # Assume table only has one row
        col_data = soup_table.find_all('td')
        if len(col_data)==0:
            values = [None for k in keys]
        else:
            values = [col.string for col in col_data]
        return dict(zip(keys,values))
    else: # Table has several rows
        col_data = [row.find_all('td') for row in rows]
        result = {}
        for i in range(len(keys)):
            result[keys[i]] = [row[i].string for row in col_data]
        return result

print('Downloading data...')
for case_num in case_numbers:
    case_file = data_dir+'case{}.json'.format(case_num)
    if os.path.exists(case_file):
        with open(case_file,'r') as f:
            case = json.load(f)
            case_data[case_num] = case
    else:
        try:
            case = {}

            case_url = base_url + "/search/" + case_num
            html_page = urllib.request.urlopen(case_url).read()
            case_soup = bs4.BeautifulSoup(html_page,'lxml')

            case_summary = case_soup.p.string
            tables = case_soup.find_all('table')

            summary_table = tables[0]
            related_table = tables[1]
            victim_table = tables[2]
            judge_table = tables[3]
            defendant_table = tables[4]

            case['Case Summary'] = case_summary
            case['Summary'] = parse_table(summary_table)
            case['Victim Details'] = parse_table(victim_table)
            case['Judges'] = parse_table(judge_table)

            case['Defendant Details'] = {}
            defendant_refs = [a['href'] for a in defendant_table.find_all('a',href=True)]

            for ref in defendant_refs:
                defendant = {}
                defendant_num = ref.split('/')[-1]
                defendant_url = base_url + ref
                defendant_page = urllib.request.urlopen(defendant_url).read()
                defendant_soup = bs4.BeautifulSoup(defendant_page,'lxml')

                defendant_tables = defendant_soup.find_all('table')

                summary_table = defendant_tables[0]
                arrest_table = defendant_tables[1]
                judge_table = defendant_tables[2]
                statute_table = defendant_tables[3]
                sentencing_table = defendant_tables[4]

                defendant['Summary'] = parse_table(summary_table)
                defendant['Arrest Details'] = parse_table(arrest_table)
                defendant['Judge Info'] = parse_table(judge_table)
                defendant['Statute Sentencing'] = parse_table(statute_table)
                defendant['Total Sentencing'] = parse_table(sentencing_table)

                case['Defendant Details'][defendant_num] = defendant

            with open(case_file,'w+') as f:
                json.dump(case,f)

            case_data[case_num] = case

        except:
            print("Case number {} does not exist.".format(case_num))

with open(data_dir+'case_data.json','w+') as f:
    json.dump(case_data,f)
