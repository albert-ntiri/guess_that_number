# -*- coding: utf-8 -*-
"""
Created on Wed May 26 17:47:11 2021

@author: alber
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import pandas as pd



# Query the database to get list of hint types.

conn = sqlite3.connect("sqlite_guess_that_number.db")
c = conn.cursor()

hint_types = c.execute("SELECT code FROM hint_type").fetchall()

conn.commit()
conn.close()

hint_types = [x[0] for x in hint_types]
# hint_types = ['factor', 'multiple', 'prime', 'even_odd', 'perfect_square', 'digit_sum', 'digit_length', 'greater_less']



# Define list of key words that correspond to hint types.

keywords = [
    "Factor of an Integer",
    "Prime Number",
    "Even Number",
    "Odd Number",
    "Perfect Square",
    "Digit",
    "Sum"
]



# Scrape the web for definitions of key words.

# Download main site.
base_url = "http://mathwords.com/"
response = requests.get(base_url)
site = BeautifulSoup(response.content, 'html.parser')

# Download relevant section of site.
url2 = site.find_all(string="numbers & symbols")[0].parent['href']
response2 = requests.get(url2)
site2 = BeautifulSoup(response2.content, 'html.parser')

# Get urls for specific key words.
def_urls = []
for keyword in keywords:
    url = site2.find_all(string=keyword)[0].parent['href']
    def_urls.append(base_url + url)

# Get specific site for key words.
def_sites = []
for link in def_urls:
    response3 = requests.get(link)
    def_site = BeautifulSoup(response3.content, features='lxml')
    def_sites.append(def_site)

# Filter sites for key word definitions.
defs = [list(x.find_all('strong'))[2].parent.parent.next_sibling.next_sibling.get_text() for x in def_sites]



# Get remaining 2 definitions from alternative sit3.

# Get multiple definition
multiple_url = "https://www.mathsisfun.com/definitions/multiple.html"
response4 = requests.get(multiple_url)
multiple_site = BeautifulSoup(response4.content, 'html.parser')

multiple_def = multiple_site.find_all(attrs={'itemprop': "articleBody"})[0].get_text()
match = re.search(re.compile(".*"), multiple_def)
multiple_def = match.group(0)


# Get divisible definition
divisible_url = "https://www.mathsisfun.com/definitions/divisible.html"
response5 = requests.get(divisible_url)
divisible_site = BeautifulSoup(response5.content, 'html.parser')

divisible_def = divisible_site.find_all(attrs={'itemprop': "articleBody"})[0].get_text()
match2 = re.search(re.compile(".*"), divisible_def)
divisible_def = match2.group(0)



# Create a function to clean strings.
def clean_string(string):
    string = string.replace('\n', ' ').replace('Â', '').replace('â€“', '-')
    string = string.split(' ')
    string = [s for s in string if s]
    string = ' '.join(string)
    return string

# Create variables for definitions.
factor_def = defs[0]
factor_def = clean_string(factor_def)
factor_def = "Factor: " + factor_def + "\nDivisible: " + divisible_def

multiple_def = "Multiple: " + multiple_def
multiple_def = clean_string(multiple_def)

prime_def = defs[1]
prime_def = clean_string(prime_def)
prime_def = "Prime: " + prime_def

even_def = defs[2]
even_def = clean_string(even_def)
odd_def = defs[3]
odd_def = clean_string(odd_def)
even_odd_def = "Even: " + even_def + "\nOdd: " + odd_def

perfect_square_def = defs[4]
perfect_square_def = clean_string(perfect_square_def)
perfect_square_def = "Perfect Square: " + perfect_square_def

digit_length_def = defs[5]
digit_length_def = clean_string(digit_length_def)
digit_length_def = "Digit: " + digit_length_def

sum_def = defs[6]
sum_def = clean_string(sum_def)
digit_sum_def = digit_length_def + "\nSum: " + sum_def



# Create list of definition variables.
hint_descriptions = [
    factor_def,
    multiple_def,
    prime_def,
    even_odd_def,
    perfect_square_def,
    digit_sum_def,
    digit_length_def
]

# Put hint types and definitions into a dataframe and save it to a CSV file.
hint_type_data = pd.DataFrame({'hint_type': hint_types[:-1], 'hint_description': hint_descriptions})
hint_type_data.to_csv("hint_descriptions.csv", index=False)