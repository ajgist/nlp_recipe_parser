'''Version 0.35'''

import json
import pandas as pd
import config
from configparser import ConfigParser

import import_ipynb
import nltk
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords as sw
from nltk import word_tokenize, pos_tag


import nltk 
import nltk.data
from nltk.tokenize import TweetTokenizer
from nltk.tokenize import word_tokenize


import nltk



import ssl

##this made nltk.pos_tag and word_tokenize work for me
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')


transformations = ['VEGETARIAN', 'NONVEG', 'VEGAN', 'NONVEGAN', 'NEWSTYLE', 'DOUBLE', 'HALVE']

class Step:
  def __init__(self, number, method, time, ingredients=[], tools=[]):
    self.number = number
    self.method = method #cooking method
    self.time = time
    self.ingredients=ingredients
    self.tools=tools

class Ingredient:
    def __init__(self, name, quantity, unit, descriptors=[], prep=[]):
        self.name=name
        self.quantity=quantity
        self.unit=unit #of measurement
        self.descriptors=descriptors
        self.prep=prep


def fetch_recipe(url):
    data = []
    #do stuff here
    return data

def parse_data():
    recipe = []
    """"
    return format:
    [list of Steps]
    """
    return recipe

def main():
    # Your Code here
    return


if __name__ == '__main__':
    main()
