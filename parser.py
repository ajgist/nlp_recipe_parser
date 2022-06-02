import json
from bs4 import BeautifulSoup
import requests


import nltk
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords as sw
from nltk import word_tokenize, pos_tag
import nltk.data
from structure import Step, Ingredient

transformations = ['VEGETARIAN', 'NONVEG', 'VEGAN', 'NONVEGAN', 'NEWSTYLE', 'DOUBLE', 'HALVE']

proteins = ['meat', 'chicken', 'tofu', 'fish']
measurements = ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce'] #should also consider no unit (ex 1 lemon)
tools = ['knife', 'over', 'pan', 'bowl', 'skillet', 'plate', 'microwave']
actions = ['place', 'preheat', 'cook', 'set', 'stir', 'heat', 'whisk', 'mix', 'add', 'drain', 'pour', 'sprinkle', 'reduce', 'transfer', 'season', 'discard', 'saute', 'cover', 'simmer', 'combine', 'layer', 'lay', 'finish', 'bake', 'uncover', 'continue', 'marinate', 'strain', 'reserve', 'dry', 'scrape', 'return', 'bring', 'melt', 'microwave', 'sit', 'squeeze', 'seal', 'brush', 'broil', 'serve', 'turn', 'scramble', 'toss', 'break', 'repeat', 'crush', 'moisten', 'press', 'open', 'leave', 'refrigerate', 'grate', 'salt', 'ladle', 'arrange', 'adjust']
prepositions = ['of', 'and', 'in', 'until', 'for']

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

def parse_data(data):
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
        

        #iObject = Ingredient("name", "quantity", "unit")
        #iList.append(iObject)




    """"
    parse steps: ideas
    - use list of ingredients as keywords to find all ingredients in a step
    - include check for prepositions for extra details
    - ** some words are ingredients/tools and verbs (microwave, salt) find way to distinguish the verb before the ingredient maybe? idk
    """
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

    

    recipe = {"ingredients": iList, "steps": sList}
    return recipe

Toolist = ['plates', 'bowls', 'whisks', 'saucepans', 'pots', 'spoons', 'knives', 'skillet', 'skillets',
         'baking dishes', 'bags', 'tablespoons', 'teaspoons',
        'plate', 'bowl', 'microwave', 'pan', 'whisk', 'saucepan', 'pot', 'spoon', 'knive',
        'oven', 'refrigerator', 'paper towels', 'baking dish', 'bag', 'tablespoon', 'teaspoon']

Timelist = ['second', 'seconds', 'minute', 'minutes', 'hour', 'hours', 'day', 'days']

def FindTools(sentence):
    a = str(sentence.lower())
    tools = []
    for item in Toolist:
        if item in a and item not in tools:
            tools.append(item)
    return tools

def FindTime(sentence):
    time = 'None'
    y = nltk.word_tokenize(str(sentence.lower()))
    y = nltk.pos_tag(y)
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
    if time != 'None':  return time
    else: return None

'''def createStep(steps):
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
        print("--------------------------------")'''
    
def main():
    # Your Code here
    print("Welcome to the Interactive Recipe Parser!")
    # EXTRA RECIPE: https://www.allrecipes.com/recipe/20809/avocado-soup-with-chicken-and-lime/

    url = 'https://www.allrecipes.com/recipe/20809/avocado-soup-with-chicken-and-lime/' 
    #takes user input from command line
    #url = input("Please paste the url of the recipe you want to use:")

    rawData = fetch_recipe(url)

    #createStep(rawData["steps"])
    for i in rawData["steps"]:
        print(i)
        print(FindTools(i))
        print(FindTime(i))
        print("-------------------------")
    return


if __name__ == '__main__':
    main()
