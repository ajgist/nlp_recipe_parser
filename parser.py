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
from structure import Step, Ingredient


from helpers import StepHelper
from transformations import Transform
from structure import Step, Ingredient


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


transformations = ['VEGETARIAN', 'NONVEG', 'VEGAN', 'NONVEGAN', 'NEWSTYLE', 'DOUBLE', 'HALVE']

veg = []
with open("veg.txt", "r") as f:
  content = f.read()
  veg = content.split(",")
non_veg = []
with open("nonveg.txt", "r") as f:
  content = f.read()
  non_veg = content.split(",")

proteins = ['meat', 'chicken', 'tofu', 'fish']

measurements = ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce', 'cups', 'tablespoons', 'teaspoons', 'pounds', 'ounces', 'cloves', 'clove'] #should also consider no unit (ex 1 lemon)
extra = ['seasoning', 'broth', 'juice', 'tomato', 'beef', 'bacon']
tools = ['knife', 'oven', 'pan', 'bowl', 'skillet', 'plate', 'microwave']
actions = ['shred', 'dice', 'place', 'preheat', 'cook', 'set', 'stir', 'heat', 'whisk', 'mix', 'add', 'drain', 'pour', 'sprinkle', 'reduce', 'transfer', 'season', 'discard', 'saute', 'cover', 'simmer', 'combine', 'layer', 'lay', 'finish', 'bake', 'uncover', 'continue', 'marinate', 'strain', 'reserve', 'dry', 'scrape', 'return', 'bring', 'melt', 'microwave', 'sit', 'squeeze', 'seal', 'brush', 'broil', 'serve', 'turn', 'scramble', 'toss', 'break', 'repeat', 'crush', 'moisten', 'press', 'open', 'leave', 'refrigerate', 'grate', 'salt', 'ladle', 'arrange', 'adjust']
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
    ingredientsRaw = soup.find_all("span", {"class": "ingredients-item-name"})
    timingAndServingsRaw = soup.find_all("div", {"class": "recipe-meta-item-body elementFont__subtitle"}) #WIP - total time and # servings that recipe makes
    stepsRaw = [a for a in (td.find_all('p') for td in soup.findAll("ul", {"class": "instructions-section"})) if a]
 

#grab text from html elements
    ingredients = []
    for x in ingredientsRaw:
        ingredients.append(x.contents[0])

    # for x in ingredients:
    #     print(x)

    steps = []
    for x in stepsRaw[0]: 
        # split the multiple sentences in a step into multiple steps
        contents = x.contents[0]
        innerSteps = contents.split('.')[:-1]
        steps += innerSteps

    '''for x in range(0,len(steps)):
        print("Step", x+1, ":", steps[x])'''


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
        quantity, units = find_number_and_units(iArr)
        

        # print(iArr)
        # print(quantity, units)
        # print("____________________________")

        iObject = Ingredient(text=data["ingredients"][i])
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
            sArr = word_tokenize(newStep)

            #finding ingredients
            ingredientsInStep = []
            for word in sArr:
                if word in veg or word in non_veg or word in extra: 
                    sArr.remove(word)
                    ingredientsInStep.append(word)

            ingredientsInStep += ingredientInIngredients #new step

            #finding method of preparation, separate preparation into 1. period before an action 2. action 3. result following action
            methodInStep = None
            for word in sArr:
                if word.lower() in actions:
                    methodInStep= word
                    break
            
            # remove double commas
            text = text.replace(",,", "and") 
            sObject = Step(text, number = j, method = methodInStep, time=time, ingredients=ingredientsInStep, tools = tools)
            j += 1
            sList.append(sObject)
            # print("Text:",text, "\n Method:", methodInStep, "\n Time:", time, "\n Ingredients:", ingredientsInStep, "\nTool:",tools)

    

    recipe = {"ingredients": iList, "steps": sList}
    return recipe



#helper func to substitute property and do a replace on the text (NOT good for step.ingredients since it is a list)



# def transform(steps, ingredients, transformation):
#     if transformation == "healthy":
#         return healthy(steps, ingredients)
#     elif transformation == "unhealthy":
#         return unhealthy(steps, ingredients)
#     elif transformation == "vegetarian":
#         return vegetarian(steps, ingredients)
#     elif transformation == "nonvegetarian":
#         return nonvegetarian(steps, ingredients)
#     elif transformation == "glutenfree":
#         return glutenfree(steps, ingredients)
#     elif transformation == "asian":
#         return asianfood(steps, ingredients)
#     elif transformation == "double":
#         return doubleRecipe(steps, ingredients) 
#     else:
#         print("Your request didn't match one of the available options :(")
#         return None


def printRecipe(steps, ingredients):
    print("Ingredients List")
    print("____________________________________")
    for x in ingredients:
        print(x.text)
    print(" ")

    print("Directions")
    print("____________________________________")
    for i in range(0,len(steps)):
        print("Step", i+1, ":", steps[i].text)
    return



def main():
    # Your Code here
    print("Welcome to the Interactive Recipe Parser!")
    url = "https://www.allrecipes.com/recipe/16167/beef-bourguignon-i/"
    # EXTRA RECIPE: https://www.allrecipes.com/recipe/20809/avocado-soup-with-chicken-and-lime/

    # veg 
    # url = "https://www.allrecipes.com/recipe/244716/shirataki-meatless-meat-pad-thai/"
    # non-veg
    # url = "https://www.allrecipes.com/recipe/24074/alysias-basic-meat-lasagna/"

    # healthy
    # url = "https://www.allrecipes.com/recipe/245362/chef-johns-shakshuka/"

    # takes user input from command line
    # url = input("Please paste the url of the recipe you want to use:")

    rawData = fetch_recipe(url)
    recipe = parse_data(rawData)
    # printRecipe(recipe["steps"],recipe["ingredients"])


    # get transformation from user
    # t = input("Please enter a transformation ( healthy, unhealthy, vegatarian, nonvegetarian, glutenfree, asian, double )")
    # transform(recipe["steps"],recipe["ingredients"], t)

    # transformObj = Transform()
    # ingredients, steps = transformObj.nonvegetarian(recipe["steps"],recipe["ingredients"])
    # printRecipe(steps, ingredients)
    # transformObj.vegetarian(recipe["steps"],recipe["ingredients"])

    # #Heat 2 tablespoons of the oil in a large skillet over medium high heat.
    # i = Ingredient("4 tablespoons olive oil, divided", "olive oil", 4.0, "tablespoons", ['divided'])
    # s = Step("Heat 2 tablespoons of the oil in a large skillet over medium high heat.", 2, "heat", 0, ['oil'], ['skillet'])

    # transformObj.unhealthy([s], [i])
    # printRecipe([s], [i])


if __name__ == '__main__':
    main()
