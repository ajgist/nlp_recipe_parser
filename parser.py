'''Version 0.35'''

import json
from bs4 import BeautifulSoup
import requests


import nltk
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords as sw
from nltk import word_tokenize, pos_tag
import nltk.data
"""import ssl

##this made nltk.pos_tag and word_tokenize work for me
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')"""


transformations = ['VEGETARIAN', 'NONVEG', 'VEGAN', 'NONVEGAN', 'NEWSTYLE', 'DOUBLE', 'HALVE']

class Step:
  def __init__(self, text, number, method, time, ingredients=[], tools=[]):
    self.number = number
    self.text = text    #
    self.method = method #cooking method
    self.time = time    #
    self.ingredients=ingredients
    self.tools=tools    #

class Ingredient:
    def __init__(self, text, name, quantity, unit, descriptors=[], prep=[]):
        self.name=name
        self.text = text
        self.quantity=quantity
        self.unit=unit #of measurement
        self.descriptors=descriptors
        self.prep=prep


def fetch_recipe(link):
    html = requests.get(url = link).text
    soup = BeautifulSoup(html, 'html.parser')

#grab raw html elements for relevant sections
    ingredientsRaw = soup.find_all("span", {"class": "ingredients-item-name"})
    timingAndServingsRaw = soup.find_all("div", {"class": "recipe-meta-item-body elementFont__subtitle"}) #WIP - total time and # servings that recipe makes
    stepsRaw = [a for a in (td.find_all('p') for td in soup.findAll("ul", {"class": "instructions-section"})) if a]
 

#grab text from html elements
    ingredients = []
    for x in ingredientsRaw:
        ingredients.append(x.contents[0])

    print("Ingredients List")
    for x in ingredients:
        print(x)

    steps = []
    for x in stepsRaw[0]: 
        steps.append(x.contents[0])

    '''for x in range(0,len(steps)):
        print("Step", x+1, ":", steps[x])'''


    data = {"ingredients": ingredients, "steps": steps}
    return data

def parse_data():
    recipe = []
    """"
    return format:
    [list of Steps]
    """
    return recipe

Toolist = ['plate', 'bowl', 'microwave', 'pan', 'whisk', 'saucepan', 'pot', 'spoon', 'knive',
        'oven', 'refrigerator', 'paper towels', 'baking dish', 'bag', 'tablespoon', 'teaspoon', 
          'plates', 'bowls', 'whisks', 'saucepans', 'pots', 'spoons', 'knives',
         'baking dishes', 'bags', 'tablespoons', 'teaspoons']
Timelist = ['second', 'seconds', 'minute', 'minutes', 'hour', 'hours', 'day', 'days']


def createStep(steps):
    st = 0
    for i in steps:
        st += 1
        tools = []
        a = str(i.lower())
        for item in Toolist:
            if item in a and item not in tools:
                tools.append(item)
        y = nltk.word_tokenize(str(i.lower()))
        print(i)
        y = nltk.pos_tag(y)
        
        time = 'None'
        #print(y)
        for i in range(len(y)):
            if y[i][0] in Timelist:
                pt = -1
                for index in range(i, i - 6, -1):
                    if index < 0:   break
                    if y[index][1] == 'CD': pt = index
                if pt != -1:
                    ans = y[pt][0]
                    for j in range(pt + 1, i + 1):
                        ans = ans + " " + y[j][0]
                    time = ans

        print("step", st, "tools =", tools)
        print("step", st, "time =", time)
        print("--------------------------------")
    
def main():
    # Your Code here
    print("Welcome to the Interactive Recipe Parser!")

    url = 'https://www.allrecipes.com/recipe/16167/beef-bourguignon-i/' 
    #takes user input from command line
    #url = input("Please paste the url of the recipe you want to use:")

    rawData = fetch_recipe(url)

    createStep(rawData["steps"])

    return


if __name__ == '__main__':
    main()
