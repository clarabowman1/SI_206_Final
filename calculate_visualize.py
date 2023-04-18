
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

def write_calculations(list, filename):
    f = open(filename, 'w')
    for dict in list:
        for entry in dict:
            f.write(entry + ": " + str(dict[entry]) + "\n")
        f.write("\n")
    f.close()

def open_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def make_stackedbarchart(cur, conn):
    x = ["Vegan", "Vegetarian", "None"]
    gluten_free = []
    contains_gluten = []
    diet_counts = {}
    diet_counts["Type"] = "Number of Recipes"
    cur.execute("SELECT COUNT() FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Soups.gluten_free = True AND Diets.diet = 'vegan'")
    gluten_free_vegan = cur.fetchall()[0][0]
    diet_counts["Vegan and Gluten Free"] = gluten_free_vegan
    gluten_free.append(gluten_free_vegan)
    cur.execute("SELECT COUNT() FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Soups.gluten_free = True AND Diets.diet = 'vegetarian'")
    gluten_free_vegetarian = cur.fetchall()[0][0]
    diet_counts["Vegetarian and Gluten Free"] = gluten_free_vegetarian
    gluten_free.append(gluten_free_vegetarian)
    cur.execute("SELECT COUNT() FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Soups.gluten_free = True AND Diets.diet = 'none'")
    gluten_free_none = cur.fetchall()[0][0]
    diet_counts["None and Gluten Free"] = gluten_free_none
    gluten_free.append(gluten_free_none)
    diet_counts["Total Gluten Free"] = (gluten_free_vegan + gluten_free_vegetarian + gluten_free_none)
    cur.execute("SELECT COUNT() FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Soups.gluten_free = False AND Diets.diet = 'vegan'")
    gluten_vegan = cur.fetchall()[0][0]
    diet_counts["Vegan and Contains Gluten"] = gluten_vegan
    contains_gluten.append(gluten_vegan)
    cur.execute("SELECT COUNT() FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Soups.gluten_free = False AND Diets.diet = 'vegetarian'")
    gluten_vegetarian = cur.fetchall()[0][0]
    diet_counts["Vegetarian and Contains Gluten"] = gluten_vegetarian
    contains_gluten.append(gluten_vegetarian)
    cur.execute("SELECT COUNT() FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Soups.gluten_free = False AND Diets.diet = 'none'")
    gluten_none = cur.fetchall()[0][0]
    diet_counts["None and Contains Gluten"] = gluten_none
    contains_gluten.append(gluten_none)
    diet_counts["Total Contains Gluten"] = (gluten_vegan + gluten_vegetarian + gluten_none)
    diet_counts["Total Vegan"] = (gluten_free_vegan + gluten_vegan)
    diet_counts["Total Vegetarian"] = (gluten_free_vegetarian + gluten_vegetarian)
    diet_counts["Total None"] = (gluten_free_none + gluten_none)
    diet_counts["Total"] = (gluten_free_vegan + gluten_free_vegetarian + gluten_free_none + gluten_vegan + gluten_vegetarian + gluten_none)

    plt.bar(x, contains_gluten, color="orange")
    plt.bar(x, gluten_free, bottom=contains_gluten, color="purple")
    plt.legend(("Contains Gluten", "Gluten Free"))
    plt.title("Distribution of Receipes into Diet Categories and their Gluten Statuses")
    plt.ylabel("Number of Recipes")
    plt.xlabel("Diets")
    plt.show()
    return diet_counts

def make_barchart(cur, conn):
    names = ['Vegan', 'Vegetarian', 'None', 'Gluten Free', 'Contains Gluten']
    ratings = []
    ratings_dict = {}
    ratings_dict["Type"] = "Average Rating (out of 5)"
    cur.execute('SELECT Links.rating FROM Links JOIN Soups ON Links.id = Soups.id JOIN Diets ON Soups.diet_id = Diets.id WHERE Diets.diet = "vegan"')
    vegan_ratings = cur.fetchall()
    avg = 0
    for rating in vegan_ratings:
        avg += rating[0]
    avg /= len(vegan_ratings)
    ratings_dict["Average Vegan Rating"] = round(avg, 2)
    ratings.append(avg)
    
    cur.execute('SELECT Links.rating FROM Links JOIN Soups ON Links.id = Soups.id JOIN Diets ON Soups.diet_id = Diets.id WHERE Diets.diet = "vegetarian"')
    vegetarian_ratings = cur.fetchall()
    avg = 0
    for rating in vegetarian_ratings:
        avg += rating[0]
    avg /= len(vegetarian_ratings)
    ratings_dict["Average Vegetarian Ratings"] = round(avg, 2)
    ratings.append(avg)
    
    cur.execute('SELECT Links.rating FROM Links JOIN Soups ON Links.id = Soups.id JOIN Diets ON Soups.diet_id = Diets.id WHERE Diets.diet = "none"')
    none_ratings = cur.fetchall()
    avg = 0
    for rating in none_ratings:
        avg += rating[0]
    avg /= len(none_ratings)
    ratings_dict["Average None Ratings"] = round(avg, 2)
    ratings.append(avg)
    
    cur.execute('SELECT Links.rating FROM Links JOIN Soups ON Links.id = Soups.id WHERE Soups.gluten_free = True')
    gluten_free_ratings = cur.fetchall()
    avg = 0
    for rating in gluten_free_ratings:
        avg += rating[0]
    avg /= len(gluten_free_ratings)
    ratings_dict["Average Gluten Free Ratings"] = round(avg, 2)
    ratings.append(avg)
    
    cur.execute('SELECT Links.rating FROM Links JOIN Soups ON Links.id = Soups.id WHERE Soups.gluten_free = False')
    containsgluten_ratings = cur.fetchall()
    avg = 0
    for rating in containsgluten_ratings:
        avg += rating[0]
    avg /= len(containsgluten_ratings)
    ratings_dict["Average Contains Gluten Ratings"] = round(avg, 2)
    ratings.append(avg)
    colors = ["green", "blue", "red", "orange", "purple"]
    plt.ylim(4,5)
    plt.bar(names, ratings, color=colors)
    plt.title("Average Rating by Dietary Category")
    plt.ylabel("Ranking")
    plt.xlabel("Dietary Category")
    plt.show()
    return ratings_dict

def make_hist(cur, conn):
    '''
    makes histogram of preparation times w/ stack by diet type
    also calculates and writes to outfile avg prep times by category.overall
    '''
    cur.execute('SELECT Soups.preparation_time FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Diets.diet = "vegan" AND Soups.preparation_time > 0')
    max_time = 0
    vegan_times = cur.fetchall()
    vegan = []
    avg_vegan_time = 0
    avg_time = 0
    for time in vegan_times:
        avg_vegan_time += time[0]
        avg_time += time[0]
        vegan.append(time[0])
        if (time[0] > max_time):
            max_time = time[0]
    avg_vegan_time /= len(vegan_times)
    cur.execute('SELECT Soups.preparation_time FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Diets.diet = "vegetarian" AND Soups.preparation_time > 0')
    vegetarian_times = cur.fetchall()
    vegetarian = []
    avg_vegetarian_time = 0
    for time in vegetarian_times:
        vegetarian.append(time[0])
        avg_vegetarian_time += time[0]
        avg_time += time[0]
        if (time[0] > max_time):
            max_time = time[0]
    avg_vegetarian_time /= len(vegetarian_times)
    cur.execute('SELECT Soups.preparation_time FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Diets.diet = "none" AND Soups.preparation_time > 0')
    none_times = cur.fetchall()
    none = []
    avg_none_time = 0
    for time in none_times:
        none.append(time[0])
        avg_none_time += time[0]
        avg_time += time[0]
        if (time[0] > max_time):
            max_time = time[0]
    avg_none_time /= len(none_times)
    avg_time /= (len(vegan_times) + len(vegetarian_times) + len(none_times))
    times_dict = {"Average Preparation Time": "minutes",
                  "Vegan": round(avg_vegan_time,2),
                  "Vegetarian": round(avg_vegetarian_time, 2),
                  "None": round(avg_none_time,2),
                  "Aggregate": round(avg_time,2)}
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
    return times_dict

def make_scatter(cur, conn):
    cur.execute("SELECT preparation_time, cost_per_serving FROM Soups WHERE preparation_time > 0 AND gluten_free = True AND Soups.preparation_time < 600 AND Soups.cost_per_serving < 600")
    gf_list = cur.fetchall()
    cur.execute("SELECT preparation_time, cost_per_serving FROM Soups WHERE preparation_time > 0  AND gluten_free = False AND Soups.preparation_time < 600 AND Soups.cost_per_serving < 600")
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
    fig = plt.figure(figsize =(10,6))
    ax1 = fig.add_subplot(121)
    gf = plt.scatter(gf_x, gf_y, c = "purple")
    ngf = plt.scatter(ngf_x, ngf_y, c = "orange")
    plt.xlabel('Preparation Time (min)')
    plt.ylabel('Cost per Serving (cents)')
    plt.title('Gluten Free and Non-Gluten Free Recipes')
    plt.legend((gf, ngf),("Gluten Free", "Not Gluten Free"))
    cur.execute('SELECT Soups.preparation_time, Soups.cost_per_serving FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Soups.preparation_time > 0 AND Diets.diet = "vegan" AND Soups.preparation_time < 600 AND Soups.cost_per_serving < 600')
    vegan_list = cur.fetchall()
    cur.execute('SELECT Soups.preparation_time, Soups.cost_per_serving FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Soups.preparation_time > 0 AND Diets.diet = "vegetarian" AND Soups.preparation_time < 600 AND Soups.cost_per_serving < 600')
    vegetarian_list = cur.fetchall()
    cur.execute('SELECT Soups.preparation_time, Soups.cost_per_serving FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Soups.preparation_time > 0 AND Diets.diet = "none" AND Soups.preparation_time < 600 AND Soups.cost_per_serving < 600')
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
    ax2 = fig.add_subplot(122)
    none = plt.scatter(n_x, n_y, c = 'red')
    vegetarian = plt.scatter(veg_x, veg_y, c = 'blue')
    vegan = plt.scatter(vv_x, vv_y, c = 'green')
    plt.xlabel('Preparation Time (min)')
    plt.ylabel('Cost per Serving (cents)')
    plt.title('Different Diets')
    plt.legend((none, vegetarian, vegan),("None", "Vegetarian", "Vegan"))
    plt.suptitle('Preparation Time vs Cost Per Serving\nCosts and Times above 600 omitted')
    plt.show()

def calc_cost(cur,conn):
    cur.execute('SELECT Soups.cost_per_serving FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Diets.diet = "vegan"')
    vegan_list = cur.fetchall()
    cur.execute('SELECT Soups.cost_per_serving FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Diets.diet = "vegetarian"')
    vegetarian_list = cur.fetchall()
    cur.execute('SELECT Soups.cost_per_serving FROM Soups JOIN Diets ON Soups.diet_id = Diets.id WHERE Diets.diet = "none"')
    none_list = cur.fetchall()
    vegan_cost = 0
    vegetarian_cost = 0
    none_cost = 0
    total_cost = 0
    for cost in vegan_list:
        vegan_cost += cost[0]
    total_cost += vegan_cost
    vegan_cost /= len(vegan_list)
    for cost in vegetarian_list:
        vegetarian_cost += cost[0]
    total_cost += vegetarian_cost    
    vegetarian_cost /= len(vegetarian_list)
    for cost in none_list:
        none_cost += cost[0]
    total_cost += none_cost
    none_cost /= len(none_list)
    total_cost /= (len(vegan_list) + len(vegetarian_list) + len(none_list))
    cost_dict = {"Average Cost Per Serving": "cents",
                  "Vegan": round(vegan_cost,2),
                  "Vegetarian": round(vegetarian_cost,2),
                  "None": round(none_cost,2),
                  "Aggregate": round(total_cost,2)}
    return cost_dict

if __name__ == '__main__':
    cur, conn = open_database('soup.db')
    outfile = "calculations.txt"
    calculations_list = []
    calculations_list.append(make_stackedbarchart(cur, conn))
    calculations_list.append(make_barchart(cur, conn))
    calculations_list.append(make_hist(cur, conn))
    make_scatter(cur, conn)
    calculations_list.append(calc_cost(cur, conn))
    write_calculations(calculations_list, outfile)
    unittest.main(verbosity=2)