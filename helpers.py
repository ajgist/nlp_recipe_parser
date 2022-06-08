import json
from bs4 import BeautifulSoup
import requests
import re
import unicodedata


import nltk
from nltk.tokenize import TweetTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords as sw
from nltk import word_tokenize, pos_tag
import nltk.data
nltk.download('omw-1.4')


#----------------------------------Steps Helper functions-------------------------------------------------------------------------#


class StepHelper():
     def createNewSteps(self, actions, oldStep):
          newSteps = []
          pattern = re.compile("(and) (?P<possible_action>\w+)")
          while True:
               result = re.search(pattern, oldStep)
               if result == [] or result == None: break
               first = oldStep[:result.span(0)[0]]
               second = oldStep[result.span(1)[1]:]
               if result.group("possible_action") in actions:
                    newSteps.append(first.strip(' ').capitalize())
                    oldStep = second.strip(' ').capitalize()
               else: 
                    oldStep = first.strip(' ') + ',' + second 

          newSteps.append(oldStep)
          return newSteps

     def FindTools(self, sentence, Toolist):
          """
          Inputs: sentence: A step 
                  Toolist: A list of items
          Outputs: tools: A list of tools found in sentence
                   a: modified sentence
          """
          a = str(sentence.lower())
          tools = []
          for item in Toolist:
               if item in a and item not in tools:
                    a = a.replace(item, '')
                    tools.append(item)
          return tools, a

     def FindTime(self, sentence, Timelist):
          """
          inputs: sentence, Timelist
          outputs: time, sentence ( modified )
          """
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
          if time != 'None':
               sentence = sentence.replace(time, '')
               return time, sentence
          else: return None, sentence

     def FindIngredients(self, text, ingredientsNames,newStep, veg, non_veg, extra):
          ingredientsNamesInStep = [name for name in ingredientsNames if name in text]
          sArr = word_tokenize(newStep)

          #finding ingredients
          ingredientsInStep = []
          for word in sArr:
               if word in veg or word in non_veg or word in extra: 
                    if not any(word in name for name in ingredientsNamesInStep):
                         ingredientsInStep.append(word)
          
          ingredientsInStep += ingredientsNamesInStep
          return ingredientsInStep

#----------------------------------Steps Helper functions End-------------------------------------------------------------------------#

#---------------------------------helper functions to find ingredients and qty--------------------------#
class IngredientHelper():
     def __init__(self, wordReplacement = {}):
          self.wordReplacement = wordReplacement
          

     def find_name(self, iArr, measurements, ingredient_stopwords):
        # iArr = tokenized array 
        ingredient = ""
        checker = False
        in_parentheses = False
        for i in range(0, len(iArr)):
            if iArr[i] == ",":
                if ingredient == "":
                    ingredient = iArr[i-1]
                break
            elif iArr[i] == "(":
                in_parentheses = True
            elif iArr[i] == ")":
                in_parentheses = False
            elif not checker:
                if not in_parentheses and (iArr[i] in measurements or iArr[i] in ingredient_stopwords):
                    checker = True
            elif checker:
                ingredient = ingredient + iArr[i] + " "
        if ingredient == "":
            ingredient = iArr[len(iArr)-1]

        #this takes away last space after name - important for substitutions later
        else: ingredient = ingredient[0:len(ingredient)-1]
                    
        #print("ingredient name: " + ingredient)
        return ingredient
                
     def find_descriptors(self, iArr):
          # extract everything after the comma
          descriptor = ""
          checker = False
          in_parentheses = False
          for i in range(0, len(iArr)):
               if iArr[i] == "(":
                    in_parentheses = True
               elif iArr[i] == ")":
                    in_parentheses = False
               if not checker and iArr[i] == "," and not in_parentheses:
                    checker = True
               elif checker:
                    descriptor = descriptor + iArr[i] + " "
          #print("descriptors: " + descriptor)
          return descriptor
       

     #takes array of digit elements and fractions and returns sum
     def arrayToNum(self, numArr):
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
     def find_number_and_units(self, iArr, measurements):
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
                    temp = word
                    isFloat = False
                    try:
                         float(word)
                         isFloat = True
                    except ValueError:
                         nums = re.search("(\d+)/(\d+)", word)
                         if nums != None: 
                              word = str(int(nums[1])/int(nums[2]))
                              isFloat = True
                         else:
                              isFloat = False

                    if word.isnumeric() or isFloat:
                         self.wordReplacement[temp] = word
                         numArr.append(word)

          #search for numbers directly left of measurement keyword
          else:
               stopIndex = -1
               for i in range(index-1, -1, -1):
                    word = iArr[i]
                    temp = word
                    isFloat = False
                    try:
                         float(word)
                         isFloat = True
                    except ValueError:
                         nums = re.search("(\d+)/(\d+)", word)
                         if nums != None: 
                              word = str(int(nums[1])/int(nums[2]))
                              isFloat = True
                         else:
                              isFloat = False

                    if word.isnumeric() or isFloat: 
                         self.wordReplacement[temp] = word
                         numArr.insert(0, word)
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
                              nums = re.search("(\d+)/(\d+)", word)
                              if nums != None: 
                                   word = str(int(nums[1])/int(nums[2]))
                                   isFloat = True
                              else:
                                   isFloat = False
                         if word.isnumeric() or isFloat: multArr.insert(0, word)
                         multiplier = self.arrayToNum(multArr)
          sum = self.arrayToNum(numArr)
          sum = sum * multiplier
          return sum, unit

#---------------------------------helper functions to find ingredients and qty end----------------------#