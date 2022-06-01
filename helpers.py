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
                    newSteps.append(first)
                    oldStep = second
               else: 
                    oldStep = first + ',' + second 

          newSteps.append(oldStep)
          return newSteps

     def getMethod(self, methodInStep):
          method = None
          
          if methodInStep["pre"]!= []:
               if methodInStep["post"] != []:
                    method = [" ".join(methodInStep["pre"])] + methodInStep["action"] + [" ".join(methodInStep["post"])]
               else:
                    method = [" ".join(methodInStep["pre"])] + methodInStep["action"] + ['']
          else: 
               if methodInStep["post"] != []:
                    method =  [''] + methodInStep["action"] + [" ".join(methodInStep["post"])]
               else: 
                    method = [''] + methodInStep["action"] + ['']
     
          return method



#----------------------------------Steps Helper functions End-------------------------------------------------------------------------#
