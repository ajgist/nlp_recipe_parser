import json
from bs4 import BeautifulSoup
import requests
import unicodedata
import re

import nltk
from nltk.tokenize import TweetTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords as sw
from nltk import word_tokenize, pos_tag
import nltk.data
import copy
import sys

from structure import Step, Ingredient


from helpers import StepHelper, IngredientHelper
from transformations import Transform
from structure import Step, Ingredient
from convert_to_html import template

#for nltk import errors
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('wordnet')
nltk.download('omw-1.4')



veg = []
with open("veg.txt", "r") as f:
  content = f.read()
  veg = content.split(",")
non_veg = []
with open("nonveg.txt", "r") as f:
  content = f.read()
  non_veg = content.split(",")

proteins = ['meat', 'chicken', 'tofu', 'fish']

ingredient_stopwords = ['can', 'cans', 'package', 'packages']

measurements = ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce', 'cups', 'tablespoons', 'teaspoons', 'pounds', 'ounces', 'cloves', 'clove'] #should also consider no unit (ex 1 lemon)
extra = ['seasoning', 'broth', 'juice', 'tomato', 'beef', 'bacon']
tools = ['knife', 'oven', 'pan', 'bowl', 'skillet', 'plate', 'microwave']
actions = ['shred', 'dice', 'place', 'preheat', 'cook', 'set', 'stir', 'heat', 'whisk', 'mix', 'add', 'drain', 'pour', 'sprinkle', 'reduce', 'transfer', 'season', 'discard', 'saute', 'cover', 'simmer', 'combine', 'layer', 'lay', 'finish', 'bake', 'uncover', 'continue', 'marinate', 'strain', 'reserve', 'dry', 'scrape', 'return', 'bring', 'melt', 'microwave', 'sit', 'squeeze', 'seal', 'brush', 'broil', 'serve', 'turn', 'scramble', 'toss', 'break', 'repeat', 'crush', 'moisten', 'press', 'open', 'leave', 'refrigerate', 'grate', 'ladle', 'arrange', 'adjust']
prepositions = ['of', 'and', 'in', 'until', 'for', 'to', 'on']

Toolist = ['plate', 'bowl', 'microwave', 'pan', 'whisk', 'saucepan', 'pot', 'spoon', 'knive',
        'oven', 'refrigerator', 'paper towels', 'baking dish', 'bag', 'tablespoon', 'teaspoon', 
          'plates', 'bowls', 'whisks', 'saucepans', 'pots', 'spoons', 'knives', 'skillet', 'skillets',
         'baking dishes', 'bags', 'tablespoons', 'teaspoons', 'baking sheet', "grill"]
Timelist = ['second', 'seconds', 'minute', 'minutes', 'hour', 'hours', 'day', 'days']



def fetch_recipe(link):
    html = requests.get(url = link).text
    soup = BeautifulSoup(html, 'html.parser')

#grab raw html elements for relevant sections
    titleRaw = soup.find_all("h1", {"class": "headline heading-content elementFont__display"})
    ingredientsRaw = soup.find_all("span", {"class": "ingredients-item-name"})
    timingAndServingsRaw = soup.find_all("div", {"class": "recipe-meta-item-body elementFont__subtitle"}) #WIP - total time and # servings that recipe makes
    stepsRaw = [a for a in (td.find_all('p') for td in soup.findAll("ul", {"class": "instructions-section"})) if a]
 

#grab text from html elements
    ingredients = []
    for x in ingredientsRaw:
        ingredients.append(x.contents[0])

    steps = []
    for x in stepsRaw[0]: 
        # split the multiple sentences in a step into multiple steps
        contents = x.contents[0]
        innerSteps = contents.split('.')[:-1]
        steps += innerSteps

    title = None 
    for x in titleRaw:
        title = x.contents[0]

    data = {"title": title, "ingredients": ingredients, "steps": steps}
    return data
    



def parse_data(data):
  
# __________helper funcs_________________________________________________________

    IngredientHelperObj = IngredientHelper()
    
        
# ______________end of ingredient quantity/unit parsing__________________________________
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
        quantity, units = IngredientHelperObj.find_number_and_units(iArr, measurements)
        name = IngredientHelperObj.find_name(iArr, measurements, ingredient_stopwords)
        descriptors = [IngredientHelperObj.find_descriptors(iArr)]

        # print(iArr)
        # print(quantity, units)
        # print("____________________________")

        iObject = Ingredient(text=data["ingredients"][i], name=name, quantity=quantity, unit=units, descriptors=descriptors)
        iList.append(iObject)


        #iObject = Ingredient("name", quantity, units)
        #iList.append(iObject)

    sList = []

    """
    parse steps: ideas
    - use list of ingredients as keywords to find all ingredients in a step
    - include check for prepositions for extra details
    - ** some words are ingredients/tools and verbs (microwave, salt) find way to distinguish the verb before the ingredient maybe? idk
    """


    sList = []
    ingredientInIngredients = [ingredient.name for ingredient in sList] # new step

    lemmatizer = WordNetLemmatizer()
    ingredientsNames = [ingredient.name for ingredient in iList]

    j = 0
    for i in range(0, len(data["steps"])):
        step = data["steps"][i]
        step = step.encode("ascii", "ignore").decode() # remove unicode
        sArr = word_tokenize(step)

        # lemmatize 
        lemmatized_step = ' '.join([lemmatizer.lemmatize(w) for w in sArr])
        helperObj = StepHelper()

        # divide step also by number of actions.
        newSteps = helperObj.createNewSteps(actions=actions, oldStep= lemmatized_step)
        
        for newStep in newSteps:
            text = newStep
            tools, newStep = helperObj.FindTools(sentence=newStep, Toolist=Toolist)
            time, newStep = helperObj.FindTime(sentence=newStep, Timelist=Timelist)
            ingredientsInStep = helperObj.FindIngredients(text=text, ingredientsNames=ingredientsNames, newStep=newStep, veg= veg, non_veg=non_veg, extra=extra)

            ingredientsInStep += ingredientInIngredients #new step

            #finding method of preparation, separate preparation into 1. period before an action 2. action 3. result following action
            methodInStep = None
            for word in sArr:
                if word.lower() in actions:
                    methodInStep= word
                    break
            
            # remove double commas
            text = text.replace(",,", "and") 
            sObject = Step(text=text, number = j, method = methodInStep, time=time, ingredients=ingredientsInStep, tools = tools)
            j += 1
            sList.append(sObject)

    return iList, sList



#helper func to substitute property and do a replace on the text (NOT good for step.ingredients since it is a list)



def transform(steps, ingredients, transformation, obj):
    if transformation == "healthy":
        return obj.healthy(steps, ingredients)
    elif transformation == "unhealthy":
        return obj.unhealthy(steps, ingredients)
    elif transformation == "vegetarian":
        return obj.vegetarian(steps, ingredients)
    elif transformation == "nonvegetarian":
        return obj.nonvegetarian(steps, ingredients)
    elif transformation == "glutenfree":
        return obj.glutenfree(steps, ingredients)
    elif transformation == "asian":
        return obj.asianfood(steps, ingredients)
    elif transformation == "double":
        return obj.doubleRecipe(steps, ingredients, Timelist) 
    else:
        print("Your request didn't match one of the available options :(")
        return None


def printRecipe(steps, ingredients):
    print(" ")
    print("------------------------------------")
    print("----------Ingredients List----------")
    print("------------------------------------")
    for x in ingredients:
        print(x.text)
    print(" ")
    print("------------------------------------")
    print("-------------Directions-------------")
    print("------------------------------------")
    for i in range(0,len(steps)):
        print("Step", i+1, ":", steps[i].text)
    return

def printIngredient(i):
    print(" -ingredient- ")
    print("text:", i.text)
    print("name:", i.name)
    print("quantity:", i.quantity)
    print("units:", i.unit)
    print("descrips:", i.descriptors)
    print(" ")
    return

def printStep(s):
    print(" -step- ")
    print("text:", s.text)
    print("number:", s.number)
    print("method:", s.method)
    print("time:", s.time)
    print("ingreds:", s.ingredients)
    print("tools:", s.tools)
    print(" ")
    return



def main():
    # Your Code here
    print("Welcome to the Interactive Recipe Parser!")
    # url = "https://www.allrecipes.com/recipe/16167/beef-bourguignon-i/"


    # EXTRA RECIPE: 
    # url = "https://www.allrecipes.com/recipe/20809/avocado-soup-with-chicken-and-lime/"



    # veg 
    # url = "https://www.allrecipes.com/recipe/244716/shirataki-meatless-meat-pad-thai/"
    # non-veg
    # url = "https://www.allrecipes.com/recipe/24074/alysias-basic-meat-lasagna/"

    # healthy
    # url = "https://www.allrecipes.com/recipe/245362/chef-johns-shakshuka/"

    #  unhealthy:
    #  https://www.allrecipes.com/recipe/228285/teriyaki-salmon/

    #GLUTENFREE RECIPE::
    # https://www.allrecipes.com/recipe/6814/valentinos-pizza-crust/

    # takes user input from command line
    url = input("Please paste the url of the recipe you want to use: ")


    rawData = fetch_recipe(url)

    print(rawData["title"])

    ingredients, steps = parse_data(rawData)
    ingredientsOld, stepsOld = [ingredient.text for ingredient in ingredients], [step.text for step in steps]
    printRecipe(steps,ingredients)


    # --to print out data representation/properties for steps and ingredients--

    for i in ingredients:
       printIngredient(i)

    for s in steps:
       printStep(s)


    # get transformation from user
    t = input("Please enter a transformation ( healthy, unhealthy, vegatarian, nonvegetarian, glutenfree, asian, double )\n")

    transformObj = Transform(title = rawData["title"])
    ingredientsT, stepsT = transform(steps=steps, ingredients=ingredients, transformation=t, obj=transformObj)
    printRecipe(stepsT, ingredientsT)

    ingredientsNew, stepsNew = [ingredient.text for ingredient in ingredientsT], [step.text for step in stepsT]
    template(stepsOld, ingredientsOld, stepsNew, ingredientsNew, t)


if __name__ == '__main__':
    main()
