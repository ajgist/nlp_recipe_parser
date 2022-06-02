from asyncio.windows_events import NULL
import json
from bs4 import BeautifulSoup
import requests
import re


import nltk
from nltk.tokenize import TweetTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords as sw
from nltk import word_tokenize, pos_tag
import nltk.data


from helpers import StepHelper

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
extra = ['seasoning', 'broth', 'juice', 'tomato']
measurements = ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce', 'cloves'] #should also consider no unit (ex 1 lemon)
tools = ['knife', 'oven', 'pan', 'bowl', 'skillet', 'plate', 'microwave']
actions = ['shred', 'dice', 'place', 'preheat', 'cook', 'set', 'stir', 'heat', 'whisk', 'mix', 'add', 'drain', 'pour', 'sprinkle', 'reduce', 'transfer', 'season', 'discard', 'saute', 'cover', 'simmer', 'combine', 'layer', 'lay', 'finish', 'bake', 'uncover', 'continue', 'marinate', 'strain', 'reserve', 'dry', 'scrape', 'return', 'bring', 'melt', 'microwave', 'sit', 'squeeze', 'seal', 'brush', 'broil', 'serve', 'turn', 'scramble', 'toss', 'break', 'repeat', 'crush', 'moisten', 'press', 'open', 'leave', 'refrigerate', 'grate', 'salt', 'ladle', 'arrange', 'adjust']
prepositions = ['of', 'and', 'in', 'until', 'for', 'to', 'on']


class Step:
  def __init__(self, text, number, method, time=0, ingredients=[], tools=[]):
    self.number = number
    self.text = text
    self.method = method #cooking method
    self.time = time    #
    self.ingredients=ingredients
    self.tools=tools    #

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
        # split the multiple sentences in a step into multiple steps
        contents = x.contents[0]
        innerSteps = contents.split('.')[:-1]
        steps += innerSteps

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
    # for i in range(0, len(data["ingredients"])):
    #     ingredient = data["ingredients"][i]
        

    #     iObject = Ingredient("name", "quantity", "unit")
    #     iList.append(iObject)




    """"
    parse steps: ideas
    - use list of ingredients as keywords to find all ingredients in a step
    - include check for prepositions for extra details
    - ** some words are ingredients/tools and verbs (microwave, salt) find way to distinguish the verb before the ingredient maybe? idk
    """
    sList = []
    prepositions = ['of', 'in', 'until', 'for', 'to', 'on']
    Toolist = ['plate', 'bowl', 'microwave', 'pan', 'whisk', 'saucepan', 'pot', 'spoon', 'knive',
        'oven', 'refrigerator', 'paper towels', 'baking dish', 'bag', 'tablespoon', 'teaspoon', 
          'plates', 'bowls', 'whisks', 'saucepans', 'pots', 'spoons', 'knives', 'skillet', 'skillets',
         'baking dishes', 'bags', 'tablespoons', 'teaspoons', 'baking sheet']
    Timelist = ['second', 'seconds', 'minute', 'minutes', 'hour', 'hours', 'day', 'days']
    lemmatizer = WordNetLemmatizer()

    j = 0
    for i in range(0, len(data["steps"])):
        step = data["steps"][i]
        sArr = word_tokenize(step)
        # lemmatize 
        lemmatized_step = ' '.join([lemmatizer.lemmatize(w) for w in sArr])
        helperObj = StepHelper()
        # divide step also by number of actions. hopefully most of these actions have a conjunctive word before 
        # them, such as, "and".
        newSteps = helperObj.createNewSteps(actions=actions, oldStep= lemmatized_step)
        
        for newStep in newSteps:
            text = newStep
            tools, newStep = helperObj.FindTools(sentence=newStep, Toolist=Toolist)
            time, newStep = helperObj.FindTime(sentence=newStep, Timelist=Timelist)
            sArr = word_tokenize(newStep)
            #finding ingredients
            ingredientsInStep = []
            # ingredientsText = ','.join(data["ingredients"])
            for word in sArr:
                if word in veg or word in non_veg or word in extra: 
                    sArr.remove(word)
                    ingredientsInStep.append(word)

            #finding method of preparation, separate preparation into 1. period before an action 2. action 3. result following action
            methodInStep = {"pre": None, "action": None, "post": None}
            for word in sArr:
                if word.lower() in actions:
                    methodInStep["pre"] = sArr[:sArr.index(word)]
                    methodInStep["action"] = [word]
                    methodInStep["post"] = sArr[sArr.index(word)+1:]
                    break

            methods = helperObj.getMethod(methodInStep=methodInStep)
            print(methods, ingredientsInStep, time, tools)
            
            sObject = Step(text, number = j, method = step, time=time, ingredients=ingredientsInStep, tools = tools)
            j += 1
            sList.append(sObject)

    

    recipe = {"ingredients": iList, "steps": sList}
    return recipe




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
    # url = "https://www.allrecipes.com/recipe/13125/chinese-sizzling-rice-soup/"
    #takes user input from command line
    #url = input("Please paste the url of the recipe you want to use:")

    rawData = fetch_recipe(url)
    recipe = parse_data(rawData)

    # for key, value in recipe.items():
    #     if key == "steps":
    #         print(value)


    #createStep(rawData["steps"])
    # for i in rawData["steps"]:
    #     print(i)
    #     print(FindTools(i))
    #     print(FindTime(i))
    #     print("-------------------------")
    # return


if __name__ == '__main__':
    main()
