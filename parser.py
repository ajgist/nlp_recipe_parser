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

replacementIngredients = { "oil" : "olive oil", "fry": "bake", "margarine": "butter", "bacon": "canadian bacon", "beef": "extra lean beef", "butter": "reduced fat butter", "milk": "skim milk", "cheese": "reduced fat cheese", "sour cream": "nonfat sour cream", "bread": "whole wheat bread", "white sugar": "brown sugar", "sugar": "brown sugar"}
reduceIngredients = ["butter", "vegetable oil", "salt"]

unhealthyReplaceIngredients = inv_map = {val: key for key, val in replacementIngredients.items()} #reversed dict of above

gfReplacementIngredients = {"bread": "gluten-free bread", "flour": "rice flour", "soy sauce": "tamari", "teriyaki": "gluten-free teriyaki", "breadcrumbs": "gluten-free breadcrumbs", "pasta": "rice pasta", "" }


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
    """
    iList = []
    for i in range(0, len(data["ingredients"])):
        ingredient = data["ingredients"][i]
        iArr = word_tokenize(ingredient)
        quantity, units = find_number_and_units(iArr)
        
        print(iArr)
        print(quantity, units)
        print("____________________________")

        
        

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


def substitute(obj, substitution, property):
    replaceWord = getattr(obj, property)
    setattr(obj, property, substitution)
    newText = obj.text.replace(replaceWord, substitution)
    obj.text = newText
    return


def vegetarian(steps, ingredients):

    return

def nonvegetarian(steps, ingredients):

    return

def healthy(steps, ingredients):
    print("making recipe healthy...")
    """ 
    ideas:
    - reduce amount of butter/oil by half??

    - replace unhealty with healthy using dictionary
    
    """

    for i in ingredients:
        #if i.name in reduceIngredients:
        #    substitute(i, (i.quantity)/2, i.quantity)
        if i.name in replacementIngredients:
            substitute(i, replacementIngredients[i.name], "name")
    
    for s in steps:
        #reducing bad common ingredients - TO DO


        #substituting ingredients for healthier ones
        for i in range(0, len(s.ingredients)):
            si = s.ingredients[i]
            if si in replacementIngredients:
                s.ingredients[i] = replacementIngredients[si]
                s.text = s.text.replace(si, replacementIngredients[si])

    return

def unhealthy(steps, ingredients):
    print("making recipe unhealthy...")
    """ 
    ideas:
    - replace healty with unhealthy using dictionary
    """

    for i in ingredients:
        #if i.name in reduceIngredients:
        #    substitute(i, (i.quantity)/2, i.quantity)
        if i.name in replacementIngredients:
            substitute(i, replacementIngredients[i.name], "name")

    
    for s in steps:
        #reducing bad common ingredients - TO DO


        #substituting ingredients for healthier ones
        for i in range(0, len(s.ingredients)):
            si = s.ingredients[i]
            if si in unhealthyReplaceIngredients:
                s.ingredients[i] = unhealthyReplaceIngredients[si]
                s.text = s.text.replace(si, unhealthyReplaceIngredients[si])

    return

def glutenfree(steps, ingredients):

    return

def asianfood(steps, ingredients): #some type of cuisine

    return

def doubleRecipe(steps, ingredients):

    return


def transform(steps, ingredients, transformation):
    if transformation == "healthy":
        return healthy(steps, ingredients)
    elif transformation == "unhealthy":
        return unhealthy(steps, ingredients)
    elif transformation == "vegetarian":
        return vegetarian(steps, ingredients)
    elif transformation == "nonvegetarian":
        return nonvegetarian(steps, ingredients)
    elif transformation == "glutenfree":
        return glutenfree(steps, ingredients)
    elif transformation == "asian":
        return asianfood(steps, ingredients)
    elif transformation == "double":
        return doubleRecipe(steps, ingredients) 
    else: 
        print("Your request didn't match one of the available options :(")
        return None


    return


def main():
    # Your Code here
    print("Welcome to the Interactive Recipe Parser!")
    # EXTRA RECIPE: https://www.allrecipes.com/recipe/20809/avocado-soup-with-chicken-and-lime/

    url = 'https://www.allrecipes.com/recipe/244716/shirataki-meatless-meat-pad-thai/' 
    #takes user input from command line
    #url = input("Please paste the url of the recipe you want to use:")



    #rawData = fetch_recipe(url)
    #parse_data(rawData)


#Heat 2 tablespoons of the oil in a large skillet over medium high heat.

    i = Ingredient("4 tablespoons olive oil, divided", "olive oil", 4.0, "tablespoons", ['divided'])

    s = Step("Heat 2 tablespoons of the oil in a large skillet over medium high heat.", 2, "heat", 0, ['oil'], ['skillet'])
   
    print("TEXT", s.text)
    print("INGREDIENTS", s.ingredients)

    unhealthy([s], [i])

    print("TEXT", s.text)
    print("INGREDIENTS", s.ingredients)





    return


if __name__ == '__main__':
    main()
