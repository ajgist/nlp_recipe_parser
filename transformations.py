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


class Transform():
     def reconstruct(self, texts):
          """
          input: Dictionary of step instructions
          output: Dictionary of step instructions modified. 

          idea: If a step is has 4 or less words, then carry on the next step into the same step        
          """

          newTexts = {}
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
               newTexts[j] = newText
               i += 1
               j += 1
          
          return newTexts

#---------------------------------------NON VEGETARIAN TRANSFORMATION---------------------------------------------------------#

     def nonvegetarian(self, steps, ingredients):
          print("making recipe non-vegetarian...")
          """ 
          ideas:
          - find any pre-existing methods in the steps :-
                    - CASE 1:if roast/bake( or find the tool: oven ) found then baked chicken recipe. 
                    - CASE 2: otherwise in ingredients and methods suggest grounded beef.
          
          """
          flag = 0

          stirIndex = None
          methodInStep = {}
          toolInStep = {}
          textInStep = {}
          
          j = 0
          number = 0
          L = len(steps)

          # case 1
          while number < L:
               step = steps[number]
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

                    nextStep = steps[number + 1]
                    steps[number + 1] = Step(text = "Meanwhile, "+ nextStep.text.lower(), method=nextStep.method, tools=nextStep.tools) 
                    
                    # to bring the entire recipe together
                    suggestedInstruction = "Shred the baked chicken and serve with the rest."
                    finalStep = Step(text = suggestedInstruction, method="shred", tools=[]) 
                    steps.append(finalStep)
                    L += 1

                    flag = 1
               
               # case 2
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

               # print( j , ":" , textInStep[j])
               j += 1
               number += 1


          print("Printing Ingredients...")
          for number, ingredient in enumerate(ingredients):
               print( number , ":", ingredient.text)

          print("--------------------------------------------------------------------------------")

          print("Printing Instructions...")
          newTextInStep = self.reconstruct(textInStep)
          for number, step in newTextInStep.items():
               print( f"Step {number}: ", step)

          print("--------------------------------------------------------------------------------")

          # # html output

          # wrapper = """
          #           <html>
          #           <header>
          #           Recipe: Non Vegetarian Transformation
          #           </header>
          #           <body>
          #           <title> Ingredients </title>
          #                {{htmlText}}
          #           </body>
          #           </html>
          #           """

          # file_loader = FileSystemLoader('templates')
          # env = Environment(loader=file_loader)

          # htmlLines = ["<ul>"]
          # for ingredient in ingredients:
          #      textLine = ingredient.text
          #      htmlLines.append('<li>%s</li>' % textLine) # or something even nicer
          # htmlLines.append("</ul>")
          # htmlText = '\n'.join(htmlLines)

          # with open("templates/ingredients.txt",'w') as f:
          #      f.write(wrapper)
          


          # template = env.get_template("ingredients.txt")
          # output = template.render(htmlText = htmlText)
          
          # with open("ingredients.html",'w') as f:
          #      f.write(output)
#-----------------------------------------------NON VEGETARIAN TRANSFORMATION END--------------------------------------------------------------#







