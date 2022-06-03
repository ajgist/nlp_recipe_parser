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

def parse_data(data):


# __________helper funcs_________________________________________________________

    def find_name(iArr):
        # iArr = tokenized array 
        ingredient = ""
        checker = False
        in_parentheses = False
        for i in range(0, len(iArr)):
            if iArr[i] == ",":
                if ingredient == "":
                    ingredient = iArr[i-1]
                break
            elif iArr[i] == "(":
                in_parentheses = True
            elif iArr[i] == ")":
                in_parentheses = False
            elif not checker:
                if not in_parentheses and (iArr[i] in measurements or iArr[i] in ingredient_stopwords):
                    checker = True
            elif checker:
                ingredient = ingredient + iArr[i] + " "
        if ingredient == "":
            ingredient = iArr[len(iArr)-1]
                    
        print("ingredient name: " + ingredient)
        return ingredient
                
    def find_descriptors(iArr):
        # extract everything after the comma
        descriptor = ""
        checker = False
        in_parentheses = False
        for i in range(0, len(iArr)):
            if iArr[i] == "(":
                in_parentheses = True
            elif iArr[i] == ")":
                in_parentheses = False
            if not checker and iArr[i] == "," and not in_parentheses:
                checker = True
            elif checker:
                descriptor = descriptor + iArr[i] + " "
        print("descriptors: " + descriptor)
        return descriptor
        


# _______________________________________________________________________________
    recipe = {}
    """"
    fit raw data to classes/objects

    parse ingredients: ideas
    - anything to the right of a comma = descriptor or preparation
    - first element is always a number
    - second element is either a unit of measurement or nothing
    - for quantity, 1 can (8 ounces) should be ___ just 8 ounces i think?
    """
    iList = []
    for i in range(0, len(data["ingredients"])):
        ingredient = data["ingredients"][i]
        iArr = word_tokenize(ingredient)
        print(iArr)
        #descriptors = find_descriptors(iArr)
        ingredients = find_name(iArr)
        #quantity, units = find_number_and_units(iArr)
        
        #print(iArr)
        #print(num, units)
        #print("____________________________")

        
        

        #iObject = Ingredient("name", quantity, units)
        #iList.append(iObject)

    sList = []


    """"
    parse steps: ideas
    - use list of ingredients as keywords to find all ingredients in a step
    - include check for prepositions for extra details
    - ** some words are ingredients/tools and verbs (microwave, salt) find way to distinguish the verb before the ingredient maybe? idk
   
    sList = []
    for i in range(0, len(data["steps"])):
        step = data["steps"][i]

        #finding ingredients from raw list
        ingredientsInStep = []
        sArr = word_tokenize(step)
        for word in sArr:
            if word in data["ingredients"]: ingredientsInStep.append(word)

        #sObject = Step(i, "method goes here")
        #sList.append(sObject)
 """
    

    recipe = {"ingredients": iList, "steps": sList}
    return recipe

def main():
    # Your Code here
    print("Welcome to the Interactive Recipe Parser!")
    # EXTRA RECIPE: https://www.allrecipes.com/recipe/20809/avocado-soup-with-chicken-and-lime/

    url = 'https://www.allrecipes.com/recipe/244716/shirataki-meatless-meat-pad-thai/' 
    #takes user input from command line
    #url = input("Please paste the url of the recipe you want to use:")



    rawData = fetch_recipe(url)
    #print(rawData)
    parse_data(rawData)
    

    return


if __name__ == '__main__':
    main()
