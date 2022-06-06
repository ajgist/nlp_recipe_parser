import json
from bs4 import BeautifulSoup
import requests
import re
import string

from jinja2 import Environment, FileSystemLoader

import nltk
from nltk.tokenize import TweetTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords as sw
from nltk import word_tokenize, pos_tag
import nltk.data
nltk.download('omw-1.4')

from structure import Step, Ingredient


replacementIngredients = { "oil" : "olive oil", "fry": "bake", "margarine": "butter", "bacon": "canadian bacon", "beef": "extra lean beef", "butter": "reduced fat butter", "milk": "skim milk", "cheese": "reduced fat cheese", "sour cream": "nonfat sour cream", "bread": "whole wheat bread", "white sugar": "brown sugar", "sugar": "brown sugar"}
reduceIngredients = ["butter", "vegetable oil", "salt"]

unhealthyReplaceIngredients = inv_map = {val: key for key, val in replacementIngredients.items()} #reversed dict of above
gfReplacementIngredients = {"bread": "gluten-free bread", "flour": "rice flour", "soy sauce": "tamari", "teriyaki": "gluten-free teriyaki", "breadcrumbs": "gluten-free breadcrumbs", "pasta": "rice pasta", "noodles": "rice noodles" }

healthyReplacementActions = {"fry": "grill", "broil": "bake"}


def substitute(obj, substitution, property):
          replaceWord = getattr(obj, property)
          setattr(obj, property, substitution)
          newText = obj.text.replace(replaceWord, substitution)
          obj.text = newText
          return

class Transform():
     def reconstruct(self, texts):
          """
          input: Dictionary of step instructions
          output: Dictionary of step instructions modified. 

          idea: If a step is has 4 or less words, then carry on the next step into the same step        
          """

          newTexts = []
          i = 0
          j = 0
          L = len(texts)

          while i<L:
               text = texts[i]
               newText = text
               word_count = len([ word for word in text.split() if word not in string.punctuation])
               if word_count <= 4 and i+1<L:
                    newText += " and " + texts[i+1].lower()
                    i += 1
               newTexts.append(Step(text= newText))
               i += 1
          
          return newTexts

#---------------------------------------NON VEGETARIAN TRANSFORMATION---------------------------------------------------------#

     def nonvegetarian(self, steps, ingredients):
          print("making recipe non-vegetarian...")
          """ 
          ideas:
          - find any pre-existing methods in the steps :-
                    - CASE 0: TOFU
                    - CASE 1:if roast/bake( or find the tool: oven ) found then baked chicken recipe. 
                    - CASE 2:check if preheat and grill; we will add grilled chicken to the recipe.
                    - CASE 3: otherwise in ingredients and methods suggest grounded beef.
                    
                    
          """
          flag = 0

          stirIndex = None
          methodInStep = {}
          toolInStep = {}
          textInStep = {}
          
          j = 0
          number = 0
          L = len(steps)

          #case 0
          #ingredients part; search for tofu
          newIngredients = []
          flag = 0
          for ingredient in ingredients:
               if "tofu" in ingredient.text:
                    if flag == 0:
                         newIngredients.append(Ingredient(text="1 and 1/2 pounds ground beef"))
                         flag = 1
                    else: continue
               else:
                    newIngredients.append(ingredient)


          #steps part if tofu present
          if flag == 1:
               newSteps = []
               for step in steps:
                    text = re.sub('tofu', "beef", step.text)
                    newSteps.append(Step(text=text))
         
               
               return ( newSteps, newIngredients )

          # other cases
          while number < L:
               step = steps[number]
               textInStep[j] = step.text
               methodInStep[j] = step.method
               toolInStep[j] = step.tools

               #case 1
               if flag == 0 and step.method == "preheat" and "oven" in step.tools:
                    # add chicken breast in ingredients
                    ingredients.append(Ingredient(text="1 (3 pound) whole chicken, giblets removed"))

                    
                    # add all steps for baking chicken
                    j += 1
                    suggestedInstruction = "Place the chicken in a roasting pan, and season generously inside and out with salt and pepper."
                    textInStep[j] = suggestedInstruction

                    j += 1
                    suggestedInstruction = "Bake chicken uncovered in the preheated oven until no longer pink at the bone and the juices run clear, about 1 hour and 15 minutes"
                    textInStep[j] = suggestedInstruction

                    nextStep = steps[number + 1]
                    steps[number + 1] = Step(text = "Meanwhile, "+ nextStep.text.lower(), method=nextStep.method, tools=nextStep.tools) 
                    
                    # to bring the entire recipe together
                    suggestedInstruction = "Shred the baked chicken and serve with the rest."
                    finalStep = Step(text = suggestedInstruction, method="shred", tools=[]) 
                    steps.append(finalStep)
                    L += 1

                    flag = 1

               # case 2
               if flag == 0 and step.method == "preheat" and "grill" in step.tools:
                    # add more ingredients
                    ingredients.append(Ingredient(text="4 (8 ounce) boneless, skinless chicken breasts"))


                    # store this preheat grill step for later. First prepare chicken.
                    grillInstruction = textInStep[j]

                    
                    # add all steps for grilling chicken
                    suggestedInstruction = "Cut chicken breasts in half lengthwise."
                    textInStep[j] = suggestedInstruction

                    j += 1
                    suggestedInstruction = "Combine kosher salt, black pepper, oregano, and garlic powder in a bowl"
                    textInStep[j] = suggestedInstruction

                    j += 1
                    suggestedInstruction = "Add chicken and toss until thoroughly and evenly coated."
                    textInStep[j] = suggestedInstruction

                    j += 1
                    suggestedInstruction = "Cover with plastic wrap and marinate in the refrigerator for 1 to 12 hours, but 2 to 3 hours is ideal."
                    textInStep[j] = suggestedInstruction

                    # now add the preheat grill step
                    j += 1
                    suggestedInstruction = grillInstruction
                    textInStep[j] = suggestedInstruction

                    j += 1
                    suggestedInstruction = "Grill chicken over the hot coals for about 4 minutes per side."
                    textInStep[j] = suggestedInstruction

                    j += 1
                    suggestedInstruction = "Continue to flip and grill chicken until no longer pink in the center and an instant-read thermometer inserted into the center of each piece reads at least 150 degrees F (65 degrees C)."
                    textInStep[j] = suggestedInstruction

                    j += 1
                    suggestedInstruction = "Remove from the grill and let rest for about 5 minutes."
                    textInStep[j] = suggestedInstruction


                    nextStep = steps[number + 1]
                    steps[number + 1] = Step(text = "Meanwhile, "+ nextStep.text.lower(), method=nextStep.method, tools=nextStep.tools) 
                    
                    # to bring the entire recipe together
                    suggestedInstruction = "Serve with the grilled chicken."
                    finalStep = Step(text = suggestedInstruction, method="shred", tools=[]) 
                    steps.append(finalStep)
                    L += 1

                    flag = 1
               
               # case 3 ; more general case
               if flag == 0:
                    for key, method in methodInStep.items():
                         if method == "stir":
                              stirIndex = key
                              break 

                    if stirIndex is not None:
                         allMethods = [methodInStep[key] for key in methodInStep.keys()]
                         if "cook" in allMethods and "heat" in allMethods:
                              ingredients.append(Ingredient(text="1 pound ground beef"))
                              j += 1
                              suggestedInstruction = "Add grounded beef and cook, stirring and crumbling into small pieces until browned, 5 to 7 minutes."
                              textInStep[j] = suggestedInstruction
                              flag = 1

               j += 1
               number += 1

          newSteps = self.reconstruct(textInStep)
         
          return ( ingredients, newSteps )

          
#-----------------------------------------------NON VEGETARIAN TRANSFORMATION END--------------------------------------------------------------#

#-----------------------------------------------VEGETARIAN TANSFORMATION-----------------------------------------------------------------------#

     def vegetarian(self, steps, ingredients):
          print("making recipe vegetarian...")
          """ 
          ideas:
          - find any pre-existing methods in the steps :-
                    - Remove any meat steps
                    - add tofu steps
                    
                    
          """
          #ingredients part
          newIngredients = []
          meats = ["chicken", "beef", "pork"]
          flag = 0
          for ingredient in ingredients:
               if any(meat in ingredient.text for meat in meats):
                    if flag == 0:
                         newIngredients.append(Ingredient(text="1 (12 ounce) package tofu, cut into chunks"))
                    else: continue
               else:
                    newIngredients.append(ingredient)


          #steps part

          meat_descriptors = ["wings", "breast", "ground"] # remove these from step texts
          newSteps = []
          for step in steps:
               text = re.sub('(wings|breast|ground)', '', step.text)
               text = re.sub('(chicken|beef|pork)', "tofu", text)
               newSteps.append(text)
          

          print("Printing Ingredients...")
          for number, ingredient in enumerate(newIngredients):
               print( number , ":", ingredient.text)

          print("--------------------------------------------------------------------------------")

          print("Printing Instructions...")
          newSteps = self.reconstruct(newSteps)
          for number, step in newSteps.items():
               print( f"Step {number}: ", step)

          print("--------------------------------------------------------------------------------")

#----------------------------------------------------------------END------------------------------------------#


     def healthy(self, steps, ingredients):
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
                    print("Replacing", i.name, "with", replacementIngredients[i.name], "!")
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

     def unhealthy(self, steps, ingredients):
          print("making recipe unhealthy...")
          """ 
          ideas:
          - replace healty with unhealthy using dictionary
          """

          for i in ingredients:
               if i.name in unhealthyReplaceIngredients:
                    print("Replacing", i.name, "with", unhealthyReplaceIngredients[i.name], "!")
                    substitute(i, unhealthyReplaceIngredients[i.name], "name")

    
          for s in steps:
               #substituting ingredients for healthier ones
               for i in range(0, len(s.ingredients)):
                    si = s.ingredients[i]
                    if si in unhealthyReplaceIngredients:
                         s.ingredients[i] = unhealthyReplaceIngredients[si]
                         s.text = s.text.replace(si, unhealthyReplaceIngredients[si])

        
               #doubling bad common ingredients? - TO DO

          return

     def glutenfree(self, steps, ingredients):
          print("making recipe gluten free...")
          """ 
          ideas:
          - replace gluten with gluten free using dictionary
          """

          for i in ingredients:
               if i.name in gfReplacementIngredients:
                    print("Replacing", i.name, "with", gfReplacementIngredients[i.name], "!")
                    substitute(i, gfReplacementIngredients[i.name], "name")

    
          for s in steps:
               #substituting ingredients for healthier ones
               for i in range(0, len(s.ingredients)):
                    si = s.ingredients[i]
                    if si in gfReplacementIngredients:
                         s.ingredients[i] = gfReplacementIngredients[si]
                         s.text = s.text.replace(si, gfReplacementIngredients[si])

          return

     def asianfood(self, steps, ingredients): #some type of cuisine

          return

     def doubleRecipe(self, steps, ingredients):

          return






