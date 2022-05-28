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

transformations = ['VEGETARIAN', 'NONVEG', 'VEGAN', 'NONVEGAN', 'NEWSTYLE', 'DOUBLE', 'HALVE']

proteins = ['meat', 'chicken', 'tofu', 'fish']
measurements = ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce', 'cups', 'tablespoons', 'teaspoons', 'pounds', 'ounces'] #should also consider no unit (ex 1 lemon)
tools = ['knife', 'over', 'pan', 'bowl', 'skillet', 'plate', 'microwave']
actions = ['place', 'preheat', 'cook', 'set', 'stir', 'heat', 'whisk', 'mix', 'add', 'drain', 'pour', 'sprinkle', 'reduce', 'transfer', 'season', 'discard', 'saute', 'cover', 'simmer', 'combine', 'layer', 'lay', 'finish', 'bake', 'uncover', 'continue', 'marinate', 'strain', 'reserve', 'dry', 'scrape', 'return', 'bring', 'melt', 'microwave', 'sit', 'squeeze', 'seal', 'brush', 'broil', 'serve', 'turn', 'scramble', 'toss', 'break', 'repeat', 'crush', 'moisten', 'press', 'open', 'leave', 'refrigerate', 'grate', 'salt', 'ladle', 'arrange', 'adjust']
prepositions = ['of', 'and', 'in', 'until', 'for']

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

    #takes array of digit elements and fractions and returns sum
    def arrayToNum(numArr):
            sum = 0
            for num in numArr:
                if len(num)>1: 
                    sum = sum+float(num)
                    continue
                try:
                    charName = unicodedata.name(num)
                except ValueError:
                    continue
                if charName.startswith('VULGAR FRACTION'):
                    charNorm = unicodedata.normalize('NFKC', num)
                    top, mid, bottom = charNorm.partition('⁄')
                    decimal = float(top) / float(bottom)
                    sum = sum + float(decimal)
                else: 
                    sum = sum + float(num)
            return sum

    #helper func that returns number and units of measurement for a given ingredient
    def find_number_and_units(iArr):
        index = -1 #default if no unit of measurement is found
        unit = "" #default / if there is no unit (1 lemon, 2 onions, etc)
        numArr = []
        multiplier = 1
        for m in measurements:
            if m in iArr: 
                index = iArr.index(m)
                unit = m
                break


        #if measurement word isn't found, search for any numbers in order
        if index == -1:
            for word in iArr:
                isFloat = False
                try:
                    float(word)
                    isFloat = True
                except ValueError:
                    isFloat = False

                if word.isnumeric() or isFloat: numArr.append(word)

        #search for numbers directly left of measurement keyword
        else:
            stopIndex = -1
            for i in range(index-1, -1, -1):
                word = iArr[i]
                isFloat = False
                try:
                    float(word)
                    isFloat = True
                except ValueError:
                    isFloat = False

                if word.isnumeric() or isFloat: numArr.insert(0, word)
                else: 
                    stopIndex = i
                    break
        
            #search for multipliers before the direct number of units (ex. 2 (7 ounce) cans)
            if stopIndex != -1:
                multArr = []
                for i in range(stopIndex, -1, -1):
                    word = iArr[i]
                    isFloat = False
                    try:
                        float(word)
                        isFloat = True
                    except ValueError:
                        isFloat = False
                    if word.isnumeric() or isFloat: multArr.insert(0, word)
                    multiplier = arrayToNum(multArr)
        sum = arrayToNum(numArr)
        sum = sum * multiplier
        return sum, unit
        #return {"number": sum, "unit": unit}

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
        quantity, units = find_number_and_units(iArr)
        
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
    parse_data(rawData)

    return


if __name__ == '__main__':
    main()
