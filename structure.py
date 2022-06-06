class Step:
<<<<<<< HEAD
  def __init__(self, text, number, method, time=0, ingredients=[], tools=[]):
    self.number = number
    self.text = text
    self.method = method #cooking method
    self.time = time    #
    self.ingredients=ingredients
    self.tools=tools    #

class Ingredient:
    def __init__(self, text, name, quantity, unit, descriptors=[]):
=======
  def __init__(self, text=None, number=None, method=None, time=None, ingredients=[], tools=[]):
    self.number = number
    self.text = text
    self.method = method #cooking method
    self.time = time
    self.ingredients=ingredients
    self.tools=tools

class Ingredient:
    def __init__(self, text=None, name=None, quantity=None, unit=None, descriptors=[]):
>>>>>>> origin/main
        self.name=name
        self.text = text
        self.quantity=quantity
        self.unit=unit #of measurement
        self.descriptors=descriptors