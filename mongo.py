from pymongo import MongoClient
from discord.ext import commands


class Mongo(commands.Cog, name='Mongo'):
    def __init__(self, bot):
        self.bot = bot
        self.db = MongoClient('mongodb+srv://Gigi-Bot:t48L477c42EpiHUG@gigidb.rztdf.mongodb.net/?retryWrites=true&w=majority')

    def init_db(self):
        return self.db


def setup(bot):
    bot.add_cog(Mongo(bot))