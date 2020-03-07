import time
import bs4 as BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import urllib.request


# My internet is slow so I need to wait for selenium to process before I begin the next steps
SCROLL_PAUSE_TIME = 5
URL = 'https://www.pokemon.com/us/pokedex/'



# Initializing the webdriver
options = FirefoxOptions()
options.add_argument("--headless")
browser = webdriver.Firefox(options=options)
browser.get(URL)
time.sleep(SCROLL_PAUSE_TIME)


# Closing the annoying cookie notification that prevents the scraper from seeing the 'see more pokemon' button
cookies = browser.find_element_by_class_name('gus-close-button')
cookies.click()

# Scrolling down to and pressing the 'see more pokmeon' button
browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")
time.sleep(SCROLL_PAUSE_TIME)
button = browser.find_elements_by_class_name('button-lightblue')[1]
button.click()


# Setting up the page height value so that the scraper knows the current height
last_height = browser.execute_script("return document.body.scrollHeight")



while True:

	# Scrolls all the way down to load more pokemon and resets page height value
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = browser.execute_script("return document.body.scrollHeight")

 	# If there is nothing more to load, the scraper stops
    if new_height == last_height:
        break

    last_height = new_height
    

# Grabbing the web element for every pokemon
resultSet = browser.find_element_by_xpath("/html/body/div[4]/section[5]/ul")
pokemons = resultSet.find_elements_by_tag_name("li")


# Saving the image of each pokemon titled with its name
for pokemon in pokemons:
    
    name_pkg = pokemon.find_element_by_tag_name("a")
    name = name_pkg.get_attribute("href").replace('https://www.pokemon.com/us/pokedex/','')
 
    location_pkg = pokemon.find_element_by_tag_name("img")
    location = location_pkg.get_attribute("src")
    
    urllib.request.urlretrieve(location,"Pictures/"+str(name).title()+".png")

browser.close()