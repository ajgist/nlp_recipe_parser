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
nltk.download('omw-1.4')

from structure import Step, Ingredient

class Transform():
     def nonvegetarian(self, steps, ingredients):
          print("making recipe non-vegetarian...")
          """ 
          ideas:
          - find any pre-existing methods in the steps :-
                    - if roast/bake( or find the tool: oven ) found then baked chicken recipe. 
                    - otherwise in ingredients and methods suggest grounded beef.
          
          """
          flag = 0

          stirIndex = None
          methodInStep = {}
          toolInStep = {}
          textInStep = {}
          j = 0
          for step in steps:
               textInStep[j] = step.text
               methodInStep[j] = step.method
               toolInStep[j] = step.tools

               if flag == 0 and step.method == "preheat" and "oven" in step.tools:
                    # add chicken breast in ingredients
                    ingredients.append(Ingredient(text="1 (3 pound) whole chicken, giblets removed"))

                    
                    # add a step for baking chicken
                    j += 1
                    suggestedInstruction = "Place the chicken in a roasting pan, and season generously inside and out with salt and pepper."
                    textInStep[j] = suggestedInstruction

                    j += 1
                    suggestedInstruction = "Bake chicken uncovered in the preheated oven until no longer pink at the bone and the juices run clear, about 1 hour and 15 minutes"
                    textInStep[j] = suggestedInstruction
                    
                    flag = 1
               

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

               # print( j , ":" , textInStep[j])
               j += 1

          print("Printing Ingredients...")
          for number, ingredient in enumerate(ingredients):
               print( number , ":", ingredient.text)

          print("--------------------------------------------------------------------------------")

          print("Printing Instructions...")
          for number, step in textInStep.items():
               print( f"Step {number}: ", step)

          print("--------------------------------------------------------------------------------")









