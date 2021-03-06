
"""
Sorting Google Scholar

Usage:
    google_scholar_sort.py <keywords>
    google_scholar_sort.py <keywords> [--results=<numberOfResults>] [--output=<path>]
    google_scholar_sort.py <keywords> [--results=<numberOfResults>]
    google_scholar_sort.py <keywords> [--output=<path>]
    google_scholar_sort.py <keywords> [--output=<path>] [--results=<numberOfResults>]

Options:
    <keywords>                   This is the search term that will be used as a keyword for search
                                 Ex... "Machine Learning In Financial Engineer"
    --results=<numberOfResults>  Specify number of results to look for on Google Scholar [default: 100]
    --output=<path>              Output file path (default: same directory of the .py file)
                                 NOTE: don't include path between quotes

"""

from docopt import docopt
import os
from time import sleep

if __name__ == '__main__':
    args = docopt(__doc__, help=True)
    print (args)

keyword = args['<keywords>']# the double quote will look for the exact keyword,
                                            # the simple quote will also look for similar keywords
number_of_results = int(args['--results']) # number of results to look for on Google Scholar
save_database = 'false' # choose if you would like to save the database to .csv (recommended to correctly visualize the URLs)

if args['--output'] is None:
    path = args['<keywords>'] + '.csv' # path to save the data if no path was included (same directory)
else:
    path = os.path.join(args['--output'], (args['<keywords>'] + '.csv')) # saving output to specified path with keywords as file name

import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd


def get_citations(content):
    out = 0
    for char in range(0,len(content)):
        if content[char:char+9] == 'Cited by ':
            init = char+9
            for end in range(init+1,init+6):
                if content[end] == '<':
                    break
            out = content[init:end]
    return int(out)

def get_year(content):
    for char in range(0,len(content)):
        if content[char] == '-':
            out = content[char-5:char-1]
    if not out.isdigit():
        out = 0
    return int(out)

def get_author(content):
    for char in range(0,len(content)):
        if content[char] == '-':
            out = content[2:char-1]
            break
    return out

def get_publication(content):
    for char in range(0,len(content)):
        temp = content.split("-")
        try:
            out = temp[2]
        except: # catch *all* exceptions
            out = "Couldn't retrieve publication"
    return out

# Start new session
session = requests.Session()

# Variables
links = list()
title = list()
citations = list()
year = list()
rank = list()
author = list()
rank.append(0) # initialization necessary for incremental purposes
publication = list()
abstract = list()

# Get content
for n in range(0, number_of_results, 10):
    url = 'https://scholar.google.com/scholar?start='+str(n)+'&q='+keyword.replace(' ','+')
    page = session.get(url)
    c = page.content
#     print(c)
    # Create parser
    soup = BeautifulSoup(c, 'html.parser')

    # Get stuff
    mydivs = soup.findAll("div", { "class" : "gs_r" })
    for div in mydivs:
        try:
            links.append(div.find('h3').find('a').get('href'))
        except: # catch *all* exceptions
            links.append('Look manually at: https://scholar.google.com/scholar?start='\
                         +str(n)+'&q'+keyword.replace(' ','+'))

        try:
            title.append(div.find('h3').find('a').text)
        except:
            title.append('Could not catch title')

        try:
            abstract.append(div.find('div',{'class' : 'gs_rs'}).text)
        except:
            abstract.append('Could not catch abstract')

        citations.append(get_citations(str(div.format_string)))
        year.append(get_year(div.find('div',{'class' : 'gs_a'}).text))
        author.append(get_author(div.find('div',{'class' : 'gs_a'}).text))
        rank.append(rank[-1]+1)
        publication.append(get_publication(div.find('div',{'class' : 'gs_a'}).text))
        sleep(0.5)



save_database=True
# Create a dataset and sort by the number of citations
data = pd.DataFrame(list(zip(author, title, citations, year, links,publication, abstract)), index = rank[1:], columns=['Author', 'Title', 'Citations', 'Year', 'Source', 'Publication', 'Abstract'])
data = data.rename_axis('Rank', axis="columns")

data_ranked = data.sort_values('Citations', ascending=False)

# Save results
if save_database:
    data_ranked.to_csv(path, encoding='utf-8')

print('Done!')

# Printing saved results path
if args['--output'] is None:
    print('File saved at: ' + '"' + os.getcwd() + '"')
else:
    print('File saved at: ' +  '"'+ path+ '"')
