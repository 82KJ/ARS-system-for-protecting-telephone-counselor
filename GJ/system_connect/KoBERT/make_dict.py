import pandas as pd
import bisect

class Sexual_dict:
    def __init__(self):
        self.dict = []
        self.make_sexual_dict()
    
    def make_sexual_dict(self):
        df = pd.read_csv("sexual_dictionary.csv")
        self.dict = list(df["0"])
    
    def match(self,word):
        if bisect.bisect_left(self.dict, word) == bisect.bisect_right(self.dict, word):
            return False
        else:
            return True