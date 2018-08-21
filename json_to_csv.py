"""
This file converts the scraped json data into CSVs.

It expects that you've already run scrape.py and have
a json file, case_data.json in the raw_json folder.

Author: Cassie Corey, cassianjanay@gmail.com
"""

import os,json
import pandas as pd
import numpy as np

from re import sub
from collections import defaultdict

data_dir = 'data/'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

with open('raw_json/case_data.json','r') as f:
    json_data = json.load(f)

case_dict = defaultdict(list)
defendant_dict = defaultdict(list)
judge_dict = defaultdict(list)

# Creating ids for the judges ourselves since
# they weren't given ids in the original data
judge_id = 0

def parse_money():
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

for case_id in json_data:
    case_data = json_data[case_id]
    summary_details = case_data['Summary']
    victim_details = case_data['Victim Details']
    judge_details = case_data['Judges']
    defendant_details = case_data['Defendant Details']

    # Build case rows
    case_data = json_data[case_id]
    case_dict['id'].append(case_id)
    case_dict['summary'].append(case_data['Case Summary'])
    case_dict['name'].append(summary_details['Case Name'])
    case_dict['number'].append(summary_details['Case Number'])
    case_dict['n_defendants'].append(summary_details['# Defendants'])
    case_dict['state'].append(summary_details['State'])
    case_dict['federal_district'].append(summary_details['Federal District'])
    case_dict['year'].append(summary_details['Year'])

    case_dict['n_victims'].append(victim_details['Total Victims'])
    case_dict['n_minors'].append(victim_details['Total Minors'])
    case_dict['n_foreigners'].append(victim_details['Total Foreigners'])
    case_dict['n_females'].append(victim_details['Total Females'])
    case_dict['n_males'].append(victim_details['Total Males'])

    # Build judge rows
    if type(judge_details['Name'])==list:
        for j in range(len(judge_details['Name'])):
            judge_dict['id'].append(judge_id)
            judge_dict['name'].append(judge_details['Name'][j])
            judge_dict['race'].append(judge_details['Race'][j])
            judge_dict['gender'].append(judge_details['Gender'][j])
            judge_dict['tenure'].append(judge_details['Tenure'][j])
            judge_dict['appointed_by'].append(judge_details['Appointed By'][j])
            judge_dict['case_id'].append(case_id)
            judge_id += 1
    else:
        judge_dict['id'].append(judge_id)
        judge_dict['name'].append(judge_details['Name'])
        judge_dict['race'].append(judge_details['Race'])
        judge_dict['gender'].append(judge_details['Gender'])
        judge_dict['tenure'].append(judge_details['Tenure'])
        judge_dict['appointed_by'].append(judge_details['Appointed By'])
        judge_dict['case_id'].append(case_id)


    # Build defendant rows
    for defendant_id in defendant_details:
        defendant_data = defendant_details[defendant_id]

        defendant_dict['id'].append(defendant_id)
        defendant_dict['case_id'].append(case_id)

        summary_data = defendant_data['Summary']
        defendant_dict['name'].append(summary_data['Name'])
        defendant_dict['gender'].append(summary_data['Gender'])
        defendant_dict['arrest_age'].append(summary_data['Arrest Age'])
        defendant_dict['race'].append(summary_data['Race'])

        arrest_details = defendant_data['Arrest Details']
        defendant_dict['arrest_date'].append(arrest_details['Arrest Date'])
        defendant_dict['charge_date'].append(arrest_details['Charge Date'])
        defendant_dict['bail_type'].append(arrest_details['Bail Type'])
        defendant_dict['bail_amount'].append(sub("[^\d\.]", "", str(arrest_details['Bail Amount']))) #scrub '$' and ',' from data

        statute_details = defendant_data['Statute Sentencing']
        defendant_dict['statute_sentence'].append(statute_details['Statute'])
        defendant_dict['statute_counts'].append(statute_details['Counts'])
        defendant_dict['statute_counts_np'].append(statute_details['Counts NP'])
        defendant_dict['statute_plea_dismissed'].append(statute_details['Plea Dismissed'])
        defendant_dict['statute_plea_guilty'].append(statute_details['Plea Guilty'])
        defendant_dict['statute_trial_guilty'].append(statute_details['Trial Guilty'])
        defendant_dict['statute_trial_ng'].append(statute_details['Trial NG'])
        defendant_dict['statute_fines'].append(sub("[$,]", "", str(statute_details['Fines']))) #scrub '$' and ',' from data. This is not a list object.
        defendant_dict['statute_months_sentenced'].append(statute_details['Months Sentenced'])
        defendant_dict['statute_months_probation'].append(statute_details['Months Probation'])

        sentence_details = defendant_data['Total Sentencing']
        defendant_dict['n_charges'].append(sentence_details['Total Charges'])
        defendant_dict['n_sentences'].append(sentence_details['Total Sentences'])
        defendant_dict['year_terminated'].append(sentence_details['Year Terminated'])
        defendant_dict['total_months_sentenced'].append(sentence_details['Months Sentenced'])
        defendant_dict['total_months_probation'].append(sentence_details['Months Probation'])
        defendant_dict['restitution'].append(sub("[^\d\.]", "", str(sentence_details['Restitution']))) #scrub '$' and ',' from data
        defendant_dict['forfeiture_charge'].append(sentence_details['Charged with Forfeiture'])
        defendant_dict['forfeiture_sentence'].append(sentence_details['Sentenced with Forfeiture'])

    judge_id += 1

# Convert to DataFrames
case_df = pd.DataFrame(case_dict)
defendant_df = pd.DataFrame(defendant_dict)
judge_df = pd.DataFrame(judge_dict)

# Write to CSVs
case_df.to_csv('data/case_data.csv',index=False)
defendant_df.to_csv('data/defendant_data.csv',index=False)
judge_df.to_csv('data/judge_data.csv',index=False)
