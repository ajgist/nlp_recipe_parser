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

     # def getMethod(self, methodInStep):
     #      method = None
          
     #      if methodInStep["pre"]!= []:
     #           if methodInStep["post"] != []:
     #                method = [" ".join(methodInStep["pre"])] + methodInStep["action"] + [" ".join(methodInStep["post"])]
     #           else:
     #                method = [" ".join(methodInStep["pre"])] + methodInStep["action"] + ['']
     #      else: 
     #           if methodInStep["post"] != []:
     #                method =  [''] + methodInStep["action"] + [" ".join(methodInStep["post"])]
     #           else: 
     #                method = [''] + methodInStep["action"] + ['']
     
     #      return method


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




#----------------------------------Steps Helper functions End-------------------------------------------------------------------------#
