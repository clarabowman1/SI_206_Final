
# Your name: Clara Bowman; Camille Zuidema
# Your student id: 36800347; 14358962
# Your email: clar@umich.edu; czuidema@umich.edu

import unittest
import sqlite3
from bs4 import BeautifulSoup
import re
import csv
import requests
import json
import os
import locale
import numpy as np
import matplotlib.pyplot as plt

def open_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def get_rating(soup_url):
    '''
        returns average rating of soup from that url
    '''
    r = requests.get(soup_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    rating_tag = soup.find(class_ = "comp type--squirrel-bold mntl-recipe-review-bar__rating mntl-text-block")
    return float(rating_tag.text)

def get_soup_links(query, cur, conn):
    ''' 
        adds soup links + ratings to database
        returns number of soup links added to db
    '''
    soup_links = {}
    url = "https://www.allrecipes.com/search?q=" + query
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
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
    for soup in soup_links:
        cur.execute("SELECT COUNT() FROM Links")
        i = cur.fetchone()[0]
        rating = get_rating(soup_links[soup])
        cur.execute("INSERT OR IGNORE INTO Links (id, name, link, rating) VALUES (?,?, ?, ?)",(i, soup, soup_links[soup], rating))
    conn.commit()
    return len(soup_links)

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

def get_soup_dict(curr, conn, num_soup_links, api_key):
    ''' 
    parameter is dict of soup names and links
    returns nested dictionary
    outer key is soup name, inner keys are 'Dietary Status', 'gluten free', 'cost per serving', 'Preparation Time'
    '''
    cur.execute("SELECT COUNT() FROM Links")
    first_index = cur.fetchone()[0]- num_soup_links
    last_index = first_index + num_soup_links
    soup_dict = {}
    for i in range(first_index, last_index):
        soup_link = cur.execute("SELECT link FROM Links WHERE id = ?", (i, ))
        soup_info = {}
        url = "https://api.spoonacular.com/recipes/extract?apiKey=" + api_key + "&url=" + cur.fetchone()[0] + "&analyze=true&includeNutrition=true"
        response = requests.get(url)
        data = response.text
        in_dict = json.loads(data)
        write_json(filename, in_dict)
        gluten_free = in_dict["glutenFree"]
        soup_info["Gluten Free"] = in_dict["glutenFree"]
        soup_info["Cost per Serving"] = in_dict["pricePerServing"]
        soup_info["Preparation Time"] = in_dict["readyInMinutes"]
        if in_dict["vegan"] == True:
            soup_info["Dietary Status"] = "vegan"
        elif in_dict["vegetarian"] == True:
            soup_info["Dietary Status"] = "vegetarian"
        else:
            soup_info["Dietary Status"] = "none"
        soup = cur.execute("SELECT name FROM Links WHERE id = ?", (i, ))
        soup_dict[cur.fetchone()[0]] = soup_info
    write_json(filename, soup_dict)

def create_tables(cur, conn):
    diets = ["vegan", "vegetarian", "none"]
    cur.execute("CREATE TABLE IF NOT EXISTS Diets (id INTEGER PRIMARY KEY, diet TEXT UNIQUE)")
    cur.execute("CREATE TABLE IF NOT EXISTS Links (id INTEGER PRIMARY KEY, name TEXT UNIQUE, link TEXT UNIQUE, rating FLOAT)")
    cur.execute("CREATE TABLE IF NOT EXISTS Soups (id INTEGER UNIQUE PRIMARY KEY, diet_id INTEGER, gluten_free BOOLEAN, cost_per_serving FLOAT, preparation_time INTEGER)")
    for i in range(len(diets)):
        cur.execute("INSERT OR IGNORE INTO Diets (id, diet) VALUES (?,?)",(i, diets[i]))
    conn.commit()

def add_soup(cur, conn, filename):
    soup_dict = load_json(filename)
    for soup in soup_dict: 
        cur.execute('SELECT id FROM Diets WHERE diet = ?', (soup_dict[soup]["Dietary Status"], ))
        diet_id = int(cur.fetchone()[0])
        cur.execute('SELECT id FROM Links WHERE name = ?', (soup, ))
        soup_id = int(cur.fetchone()[0])
        cur.execute("INSERT OR IGNORE INTO Soups (id, diet_id, gluten_free, cost_per_serving, preparation_time) VALUES (?,?,?,?,?)",(soup_id, diet_id, soup_dict[soup]["Gluten Free"], soup_dict[soup]["Cost per Serving"], soup_dict[soup]["Preparation Time"]))
    conn.commit()

def make_hist(cur, conn):
    cur.execute('SELECT Soups.preparation_time FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Diets.diet = "vegan"')
    max_time = 0
    vegan_times = cur.fetchall()
    vegan = []
    for time in vegan_times:
        if (time[0] > 0):
            vegan.append(time[0])
        if (time[0] > max_time):
            max_time = time[0]
    cur.execute('SELECT Soups.preparation_time FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Diets.diet = "vegetarian"')
    vegetarian_times = cur.fetchall()
    vegetarian = []
    for time in vegetarian_times:
        if (time[0] > 0):
            vegetarian.append(time[0])
        if (time[0] > max_time):
            max_time = time[0]
    cur.execute('SELECT Soups.preparation_time FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Diets.diet = "none"')
    none_times = cur.fetchall()
    none = []
    for time in none_times:
        if (time[0] > 0):
            none.append(time[0])
        if (time[0] > max_time):
            max_time = time[0]
    num_bars = max_time // 15
    bins = []
    for i in range(num_bars):
        bins.append(15 * i)
    bins.append(max_time)
    colors=['red', 'blue', 'green']
    plt.figure()
    plt.hist([none, vegetarian, vegan], bins, color = colors, stacked=True, label = ["None", "Vegetarian", "Vegan"])
    plt.xlabel('Preparation Time (min)')
    plt.ylabel('Number of Recipes')
    plt.title('Preparation Times of Recipes of Different Diets')
    plt.legend()
    plt.show()

def make_scatter_gf(cur, conn):
    cur.execute("SELECT preparation_time, cost_per_serving FROM Soups WHERE preparation_time > 0 AND gluten_free = True AND cost_per_serving < 500")
    gf_list = cur.fetchall()
    cur.execute("SELECT preparation_time, cost_per_serving FROM Soups WHERE preparation_time > 0 AND gluten_free = False AND cost_per_serving < 500")
    non_gf_list = cur.fetchall()
    gf_x = []
    gf_y = []
    ngf_x = []
    ngf_y = []
    for recipe in gf_list:
        gf_x.append(recipe[0])
        gf_y.append(recipe[1])
    for recipe in non_gf_list:
        ngf_x.append(recipe[0])
        ngf_y.append(recipe[1])
    plt.xlabel('Preparation Time (min)')
    plt.ylabel('Cost per Serving (cents)')
    plt.title('Preparation Time vs Cost per Serving of Gluten Free and Non-Gluten Free Recipes')
    plt.scatter(gf_x, gf_y)
    plt.scatter(ngf_x, ngf_y)
    plt.show()

def make_scatter_diet(cur, conn):
    cur.execute('SELECT Soups.preparation_time, Soups.cost_per_serving FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Soups.preparation_time > 0 AND Soups.cost_per_serving < 500 AND Diets.diet = "vegan"')
    vegan_list = cur.fetchall()
    cur.execute('SELECT Soups.preparation_time, Soups.cost_per_serving FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Soups.preparation_time > 0 AND Soups.cost_per_serving < 500 AND Diets.diet = "vegetarian"')
    vegetarian_list = cur.fetchall()
    cur.execute('SELECT Soups.preparation_time, Soups.cost_per_serving FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Soups.preparation_time > 0 AND Soups.cost_per_serving < 500 AND Diets.diet = "none"')
    none_list = cur.fetchall()
    vv_x = []
    vv_y = []
    veg_x = []
    veg_y = []
    n_x = []
    n_y = []
    for recipe in vegan_list:
        vv_x.append(recipe[0])
        vv_y.append(recipe[1])
    for recipe in vegetarian_list:
        veg_x.append(recipe[0])
        veg_y.append(recipe[1])
    for recipe in none_list:
        n_x.append(recipe[0])
        n_y.append(recipe[1]) 
    plt.scatter(n_x, n_y, c = 'red')
    plt.scatter(veg_x, veg_y, c = 'blue')
    plt.scatter(vv_x, vv_y, c = 'green')
    plt.xlabel('Preparation Time (min)')
    plt.ylabel('Cost per Serving (cents)')
    plt.title('Preparation Time vs Cost per Serving of Different Diets')
    plt.show()


if __name__ == '__main__':
    cur, conn = open_database('soup.db')
    create_tables(cur, conn)
    #query = "slow cooker soup"
    #api_key = "7566718381f04a4aa1c907595917725e"
    #num_soup_links = get_soup_links(query, cur, conn)
    #dir_path = os.path.dirname(os.path.realpath(__file__))
    #filename = dir_path + '/' + "soup.json"
    #cache = load_json(filename)
    #get_soup_dict(cur, conn, num_soup_links, api_key)
    #add_soup(cur, conn, filename)
    #make_hist(cur, conn)
    make_scatter_diet(cur, conn)
    unittest.main(verbosity=2)