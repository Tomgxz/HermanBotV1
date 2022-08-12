import random
class Chicken:
    def __init__(self):
        self.strength = random.randint(40,80)

def newChicken():
    return Chicken()