from pymongo import MongoClient

class Mongo:
  def __init__(self):
    self.db = MongoClient('mongodb+srv://Gigi-Bot:t48L477c42EpiHUG@gigidb.rztdf.mongodb.net/?retryWrites=true&w=majority')

  def init_db(self):
    return self.db