import re
import string

import nltk
from nltk.tokenize.treebank import TreebankWordDetokenizer

import nltk.data
nltk.download('omw-1.4')

from structure import Step, Ingredient
from helpers import IngredientHelper

from nltk import word_tokenize

replacementIngredients = { "oil" : "olive oil", "fry": "bake", "margarine": "butter", "bacon": "canadian bacon", "beef": "extra lean beef", "butter": "reduced fat butter", "milk": "skim milk", "cheese": "reduced fat cheese", "sour cream": "nonfat sour cream", "bread": "whole wheat bread", "white sugar": "brown sugar", "sugar": "brown sugar", "cubed beef chuck roast": "extra lean cubed beef chuck roast"}
reduceIngredients = ["butter", "vegetable oil", "salt", "olive oil", "oil", "sugar", "reduced-fat butter"]

unhealthyReplaceIngredients = inv_map = {val: key for key, val in replacementIngredients.items()} #reversed dict of above
gfReplacementIngredients = {"bread": "gluten-free bread", "flour": "rice flour", "soy sauce": "tamari", "teriyaki": "gluten-free teriyaki", "breadcrumbs": "gluten-free breadcrumbs", "pasta": "rice pasta", "noodles": "rice noodles", "all-purpose flour": "brown rice flour" }


transformation_words_asian = {'long grain white rice': 'Koshihikari rice', 'jalapeno': 'kimchi', 'vegetable oil': 'sesame oil', 'chili sauce': 'red pepper', 'bacon': 'grilled pork', 'sour cream': 'soy sauce', 'black bean': 'red bean', "oil":"sesame oil", "chili powder": "szechuan","tomato sauce": "gochujang", "tomato paste": "gochujang",  "pepper": "chinese 5 spice", "allspice": "chinese 5 spice", "tortilla": "roti bread", "corn tortilla": "roti bread", "flour tortilla": "roti bread"}

otherVegTransformations = {"sausage flavor": "basil flavor", "pork flavor": "basil flavor", "chicken flavor": "basil flavor", "beef flavor": "basil flavor"}
healthyReplacementActions = {"fry": "grill", "broil": "bake", "deep fry": "air fry", "broil": "grill", "broiler": "grilling"}


def substitute(obj, substitution, property):
          replaceWord = getattr(obj, property)
          setattr(obj, property, substitution)
          newText = obj.text.replace(replaceWord, substitution)
          obj.text = newText
          return

def checkTheIndexofNumtoChange(sentence, i, Timelist):
    s = nltk.word_tokenize(sentence)
    for j in range(i, i + 6):
        if j >= len(s):  break
        if sentence[j] in Timelist:
            return False
    return True

def handleFraction(token):
     # deal with symbols like ¾ 
     if len(token) == 1:
          if ord(token) == 188: return 0.25
          if ord(token) == 189: return 0.5
          if ord(token) == 190: return 0.75

def remove_time(obj):
               text = obj.text
               time = obj.time
               if time != None:
                    text = text.replace(time, '')
               return text

class Transform():
     def __init__(self, title=None):
          self.title = title
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
                    - case -1: pizza
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

          #case -1
          if "pizza" in self.title.lower():
               print("Adding some pepperoni to ingredients..")
               newIngredients = ingredients + [Ingredient(text="8 slices of pepperoni")]
               for step in steps:
                    if "top with" in step.text.lower():
                         print("Topping with pepperoni..")
                         step.text = step.text.lower().replace("top with", "top with pepperoni,").capitalize()
                         break
               return ( newIngredients, steps )

          #case 0
          #ingredients part; search for tofu
          newIngredients = []
          flag = 0
          for ingredient in ingredients:
               if "tofu" in ingredient.text:
                    if flag == 0:
                         print("Removing tofu in ingredients and adding ground beef")
                         newIngredients.append(Ingredient(text="1 and 1/2 pounds ground beef"))
                         flag = 1
                    else: continue
               else:
                    newIngredients.append(ingredient)


          #steps part if tofu present
          if flag == 1:
               newSteps = []
               print("Substituting tofu with beef.")
               for step in steps:
                    text = re.sub('tofu', "beef", step.text)
                    step.text = text
                    newSteps.append(step)
         
               
               return (newIngredients, newSteps )

          # other cases
          while number < L:
               step = steps[number]
               textInStep[j] = step.text
               methodInStep[j] = step.method
               toolInStep[j] = step.tools

               #case 1
               if flag == 0 and step.method.lower() == "preheat" and "oven" in step.tools:
                    print("Adding baked chicken instructions.")
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
               if flag == 0 and step.method.lower() == "preheat" and "grill" in step.tools:
                    # add more ingredients
                    print("Adding grilled chicken instructions.")
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
                              print("Adding instructions for cooking beef.")
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
                    - bacon -> eggplant
                    - any meat broth -> veg broth
                    
                    
          """
          #ingredients part
          newIngredients = []
          meats = ["ground beef", "ground chicken", "ground pork", "chicken", "beef", "pork", "pepperoni"]
          for ingredient in ingredients:
               flag = 0
               if "broth" in ingredient.text:
                    ingredient.text = re.sub("(\w+) (broth)", "vegetable broth", ingredient.text)
                    newIngredients.append(ingredient)
                    continue

               for nonveg, transformation in otherVegTransformations.items(): 
                    if nonveg in ingredient.text: 
                         print(f"Replacing {nonveg} to {transformation} in ingredients.")
                         ingredient.text = ingredient.text.replace(nonveg, transformation)
                         newIngredients.append(ingredient)
                         flag = 1
                         break

               if flag: continue

               if any(meat in ingredient.text for meat in meats):
                    print("Replacing meat with tofu in ingredients..")
                    newIngredients.append(Ingredient(text="1 (12 ounce) package tofu, cut into chunks"))
                    continue
                    
               if "bacon" in ingredient.text:
                    print("Replacing bacon with eggplant in ingredients..")
                    newIngredients.append(Ingredient(text="1 large eggplant, peeled and thinly sliced"))
                    continue

               

               newIngredients.append(ingredient)
              


          #steps part

          meat_descriptors = ["wings", "breast", "ground"] # remove these from step texts
          newSteps = []
          for step in steps:
               text = step.text.lower()
               if step.method.lower() == "bake":
                    print("Adjusting time for baking..")
                    text = re.sub("for (\d+) (minute(s?)|hour(s?)|second(s?)|minutes|)", "for 1 hour", text) 
               text = re.sub('(wings|breast|ground)', '', text)
               text = re.sub("(\w+) (broth)", "vegetable broth", text)
               text = text.replace("bacon", "eggplant")
               step.text = re.sub('(chicken|beef|pork|pepperoni|meat)', "tofu", text).capitalize()
               newSteps.append(step)

          return ( newIngredients, newSteps )

#----------------------------------------------------------------END------------------------------------------#


     def healthy(self, steps, ingredients):
          print("making recipe healthy...")
          """ 
          actions:
          - reduce amount of butter/oil/etc by half
          - replace unhealty with healthy using dictionary
          """

          for i in ingredients:
               if i.name in replacementIngredients:
                    print("Replacing", i.name, "with", replacementIngredients[i.name], "!")
                    substitute(i, replacementIngredients[i.name], "name")
    
          for s in steps:

               #substituting ingredients for healthier ones
               for i in range(0, len(s.ingredients)):
                    si = s.ingredients[i]
                    if si in replacementIngredients:
                         s.ingredients[i] = replacementIngredients[si]
                         s.text = s.text.replace(si, replacementIngredients[si])
     
          #reducing bad common ingredients
          self.changeIngredients(steps, ingredients, [], 0.5)

          return (ingredients, steps)

     def unhealthy(self, steps, ingredients):
          print("making recipe unhealthy...")
          """ 
          actions:
          - replace healty with unhealthy using dictionary
          """

          for i in ingredients:
               if i.name in unhealthyReplaceIngredients:
                    print("Replacing", i.name, "with", unhealthyReplaceIngredients[i.name], "!")
                    substitute(i, unhealthyReplaceIngredients[i.name], "name")

    
          for s in steps:
               #substituting ingredients for unhealthier ones
               for i in range(0, len(s.ingredients)):
                    si = s.ingredients[i]
                    if si in unhealthyReplaceIngredients:
                         s.ingredients[i] = unhealthyReplaceIngredients[si]
                         s.text = s.text.replace(si, unhealthyReplaceIngredients[si])
     
          #doubling bad common ingredients
          self.changeIngredients(steps, ingredients, [], 2)

          return (ingredients, steps)

     def glutenfree(self, steps, ingredients):
          print("making recipe gluten free...")
          """ 
          acitons:
          - replace gluten with gluten free using dictionary
          """

          for i in ingredients:
               if i.name in gfReplacementIngredients:
                    print("Replacing", i.name, "with", gfReplacementIngredients[i.name], "!")
                    substitute(i, gfReplacementIngredients[i.name], "name")

    
          for s in steps:
               for i in range(0, len(s.ingredients)):
                    si = s.ingredients[i]
                    if si in gfReplacementIngredients:
                         s.ingredients[i] = gfReplacementIngredients[si]
                         s.text = s.text.replace(si, gfReplacementIngredients[si])

          return (ingredients, steps)

     def asianfood(self, steps, ingredients): 
          print("making recipe asian...")

          for i in ingredients:
               if i.name in transformation_words_asian:
                    print("Replacing", i.name, "with", transformation_words_asian[i.name], "!")
                    substitute(i, transformation_words_asian[i.name], "name")

    
          for s in steps:
               #substituting ingredients for asian ones
               for i in range(0, len(s.ingredients)):
                    si = s.ingredients[i]
                    if si in transformation_words_asian:
                         s.ingredients[i] = transformation_words_asian[si]
                         s.text = s.text.replace(si, transformation_words_asian[si])
          return (ingredients, steps)

     def doubleRecipe(self, steps, ingredients, Timelist):          
          for obj in steps:
               text = remove_time(obj)
               iobj = IngredientHelper({})
               token = nltk.word_tokenize(text)
               method = obj.method # avoid changing the temperature in preheating stage
               if method != "preheat" and method != 'Preheat':
                    _ = iobj.find_number_and_units(token, [])
                    wordMap = iobj.wordReplacement
                    for word, replacement in wordMap.items():
                         try: float(replacement)
                         except: replacement = handleFraction(replacement)
                         replacement = float(replacement)*2
                         if int(replacement) == replacement: replacement = int(replacement)
                         textNew = text.replace(word, str(replacement))
                         obj.text = obj.text.replace(text, " "+textNew+" ")
               
          for obj in ingredients:
               inner = re.search("(\((.)*\))", obj.text)
               text = re.sub("(\((.)*\))", "[MASK]", obj.text)
               iobj = IngredientHelper({})
               token = nltk.word_tokenize(text)
               _ = iobj.find_number_and_units(token, [])
               wordMap = iobj.wordReplacement
               for word, replacement in wordMap.items():
                    try: float(replacement)
                    except: replacement = handleFraction(replacement)
                    replacement = float(replacement)*2
                    if int(replacement) == replacement: replacement = int(replacement)
                    obj.text = text.replace(word, str(replacement))
                    if inner != None:
                         obj.text = obj.text.replace("[MASK]", inner[0])

          return (ingredients, steps)


     def changeIngredients(self, steps, ingredients, Timelist, ratio):
          for obj in steps:
               text = remove_time(obj) 
               token = nltk.word_tokenize(text)
               s = nltk.pos_tag(token)
               if (bool(set(obj.ingredients) & set(reduceIngredients))):
                    for i in range(len(s)):
                         if s[i][1] == 'CD' and checkTheIndexofNumtoChange(obj.text, i, Timelist=Timelist):
                              token[i] = str(ratio * int(token[i]))
               textNew = TreebankWordDetokenizer().detokenize(token)
               obj.text = obj.text.replace(text, " "+ textNew+" ")
    
          for obj in ingredients:
               if any(ingredient in obj.text for ingredient in reduceIngredients):
                    inner = re.search("(\((.)*\))", obj.text)
                    text = re.sub("(\((.)*\))", "[MASK]", obj.text)
                    iobj = IngredientHelper({})
                    token = nltk.word_tokenize(text)
                    _ = iobj.find_number_and_units(token, [])
                    wordMap = iobj.wordReplacement
                    for word, replacement in wordMap.items():
                         try: float(replacement)
                         except: replacement = handleFraction(replacement)
                         replacement = float(replacement)*ratio
                         if int(replacement) == replacement: replacement = int(replacement)
                         obj.text = text.replace(word, str(replacement)) 
                         if inner != None:
                              obj.text = obj.text.replace("[MASK]", inner[0])
          return (ingredients, steps)
                    
