import bs4 as BeautifulSoup
import csv
from selenium import webdriver
import numpy as np
import pandas as pd
from os import path
from sqlalchemy import *
import time
import urllib.request
import requests


SCROLL_PAUSE_TIME = 5
url = 'https://www.pokemon.com/us/pokedex/'




browser = webdriver.Firefox()
browser.get(url)

time.sleep(5)

cookies = browser.find_element_by_class_name('gus-close-button')
cookies.click()

browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")

time.sleep(SCROLL_PAUSE_TIME)

button = browser.find_elements_by_class_name('button-lightblue')[1]
button.click()

last_height = browser.execute_script("return document.body.scrollHeight")



while True:

    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(SCROLL_PAUSE_TIME)

    new_height = browser.execute_script("return document.body.scrollHeight")

    if new_height == last_height:
        break
    last_height = new_height
    
resultSet = browser.find_element_by_xpath("/html/body/div[4]/section[5]/ul")
pokemons = resultSet.find_elements_by_tag_name("li")




for pokemon in pokemons:
    
    name_pkg = pokemon.find_element_by_tag_name("a")
    name = name_pkg.get_attribute("href").replace('https://www.pokemon.com/us/pokedex/','')
 
    location_pkg = pokemon.find_element_by_tag_name("img")
    location = location_pkg.get_attribute("src")
    
    urllib.request.urlretrieve(location,"Pictures/"+capitalize(str(name))+".png")