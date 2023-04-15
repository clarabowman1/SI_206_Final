
# Your name: Clara Bowman; Camille Zuidema
# Your student id: 36800347; 14358962
# Your email: clar@umich.edu; czuidema@umich.edu
# List who you have worked with on this project: N/A

import unittest
import sqlite3
from bs4 import BeautifulSoup
import re
import csv
import requests
import json
import os
import locale

def get_soup_links(html_file):
    ''' 
    returns dict of soups with ratings on the page
    key = soup name, value  = soup link
    '''
    soup_links = {}
    with open (html_file, 'r') as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'html.parser')
        #get first soup
        first = soup.find(id = "mntl-card-list-items_1-0")
        first_text = first.text
        first_ratings_text = re.findall("Ratings", first_text)
        if len(first_ratings_text) > 0:
            first_link = first.get('href')
            first_title_tag = first.find(class_ = "card__title-text")
            first_title_text = first_title_tag.text
            soup_links[first_title_text] = first_link
        for i in range(1, 24):
           id_name = "mntl-card-list-items_1-0-" + str(i)
           tag = first = soup.find(id = id_name)
           ratings_text = re.findall("Ratings", tag.text)
           if len(ratings_text) > 0:
               link = tag.get('href')
               title_tag = tag.find(class_ = "card__title-text")
               soup_links[title_tag.text] = link
    return soup_links

def load_json(filename):
    try:
        with open(filename, 'r') as fp:
            data = json.load(fp)
    except:
        data = {}
    return data

def write_json(filename, dict):
    with open(filename, 'w') as outfile:
        json.dump(dict, outfile, indent=4)

def get_soup_dict(soup_links):
    ''' 
    parameter is dict of soup names and links
    returns nested dictionary
    outer key is soup name, inner keys are 'dietary restriction' and 'cost'
    '''
    for soup in soup_links:
        response = requests.get('https://api.spoonacular.com/recipes/extract')
        data = response.text
        in_dict = json.loads(data)

if __name__ == '__main__':
    soup_links = get_soup_links('soup_search_results1.html')
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = dir_path + '/' + "soup.json"
    cache = load_json(filename)
    get_soup_dict(soup_links)
    write_json(filename, cache)
    unittest.main(verbosity=2)