from email.utils import parsedate_to_datetime
import json
from bs4 import BeautifulSoup
import requests
import unicodedata

import nltk
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords as sw
from nltk import word_tokenize, pos_tag
import nltk.data
# from structure import Step, Ingredient

transformations = ['VEGETARIAN', 'NONVEG', 'VEGAN', 'NONVEGAN', 'NEWSTYLE', 'DOUBLE', 'HALVE']

proteins = ['meat', 'chicken', 'tofu', 'fish']
measurements = ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce', 'cups', 'tablespoons', 'teaspoons', 'pounds', 'ounces'] #should also consider no unit (ex 1 lemon)
tools = ['knife', 'over', 'pan', 'bowl', 'skillet', 'plate', 'microwave']
actions = ['place', 'preheat', 'cook', 'set', 'stir', 'heat', 'whisk', 'mix', 'add', 'drain', 'pour', 'sprinkle', 'reduce', 'transfer', 'season', 'discard', 'saute', 'cover', 'simmer', 'combine', 'layer', 'lay', 'finish', 'bake', 'uncover', 'continue', 'marinate', 'strain', 'reserve', 'dry', 'scrape', 'return', 'bring', 'melt', 'microwave', 'sit', 'squeeze', 'seal', 'brush', 'broil', 'serve', 'turn', 'scramble', 'toss', 'break', 'repeat', 'crush', 'moisten', 'press', 'open', 'leave', 'refrigerate', 'grate', 'salt', 'ladle', 'arrange', 'adjust']
prepositions = ['of', 'and', 'in', 'until', 'for']
ingredient_stopwords = ['can', 'cans', 'package', 'packages']

# Transformation words
transformation_words = {'long': '', 'grain': 'Koshihikari', 'jalapeno': 'kimchi'}

class Step:
  def __init__(self, text, number, method, time=0, ingredients=[], tools=[]):
    self.number = number
    self.text = text
    self.method = method #cooking method
    self.time = time
    self.ingredients=ingredients
    self.tools=tools

class Ingredient:
    def __init__(self, text, name, quantity, unit, descriptors=[]):
        self.name=name
        self.text = text
        self.quantity=quantity
        self.unit=unit #of measurement
        self.descriptors=descriptors


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

    for x in range(0,len(steps)):
        print("Step", x+1, ":", steps[x])


    data = {"ingredients": ingredients, "steps": steps}
    return data

def transform(data):


# __________transformation funcs_________________________________________________________
    def transform_mexican_to_asian(iArr):
        mexican = [*transformation_words]
        # print('mexican', mexican)
        for i in range(0, len(iArr)-1):
            if iArr[i] in mexican:
                # print('mexican ingredient: ' + iArr[i])
                iArr[i] = transformation_words[iArr[i]]
        return

# _______________________________________________________________________________
    recipe = {}

    iList = []
    for i in range(0, len(data["ingredients"])):
        ingredient = data["ingredients"][i]
        iArr = word_tokenize(ingredient)
        transformed_to_asian = transform_mexican_to_asian(iArr)
        #print(iArr)


    sList = []
    for i in range(0, len(data["steps"])):
        step = data["steps"][i]
        iArr = word_tokenize(step)
        transformed_to_asian = transform_mexican_to_asian(iArr)
        #print(iArr)

    recipe = {"ingredients": iList, "steps": sList}
    return recipe

def main():
    # Your Code here
    print("Welcome to the Interactive Recipe Parser!")
    # EXTRA RECIPE: https://www.allrecipes.com/recipe/20809/avocado-soup-with-chicken-and-lime/

    url = 'https://www.allrecipes.com/recipe/73303/mexican-rice-iii/' 
    #takes user input from command line
    #url = input("Please paste the url of the recipe you want to use:")



    rawData = fetch_recipe(url)
    transform(rawData)
    

    return


if __name__ == '__main__':
    main()
