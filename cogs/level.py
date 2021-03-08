import random
from math import sqrt, floor
import datetime as dt
import discord
from discord.ext import commands
from util import Util
from mongo import Mongo
from pymongo import ReturnDocument


class Level(commands.Cog, name='Level'):
    def __init__(self, bot):
        self.bot = bot
        self.db = Mongo.init_db(Mongo(self.bot))
        self.server_db = None

    @commands.command(name='build_level', hidden=True, aliases=['rebuild_level'])
    @commands.has_guild_permissions(administrator=True)
    async def build_level(self, ctx, member: discord.Member = None):
        self.server_db = self.db['server'][str(ctx.guild.id)]
        if not Util.check_channel(ctx, True):
            return
        new_level = {'level': 1, 'exp': 0, 'exp_streak': 0, 'timestamp': dt.datetime.utcnow()}
        if member:
            self.server_db.find_one_and_update({"_id": str(member.id)}, {'$set': new_level}, upsert=True)
            return
        for member in ctx.guild.members:
            if not member.bot:
                self.server_db.find_one_and_update({"_id": str(member.id)}, {'$set': new_level}, upsert=True)

    @commands.command(name='stats', pass_context=True)
    async def stats(self, ctx, user: discord.Member):
        """Returns a user's current profile level and experience"""
        if not Util.check_channel(ctx, True):
            return
        await self.add_experience(ctx, user, 0)

    @commands.command(name='add_experience', hidden=True, pass_context=True, aliases=['xp'])
    @commands.has_guild_permissions(administrator=True)
    async def add_experience(self, ctx, user: discord.Member, amount: int):
        if not Util.check_channel(ctx):
            return
        if isinstance(user, discord.Member):
            user_level, user_exp = await self.update_experience(str(ctx.guild.id), str(user.id), amount)
            await ctx.send(embed=discord.Embed(title=f'{user.display_name}\'s Stats',
                                               description=f'[LVL] **{user_level}**   [EXP] **{user_exp}**'))

    @staticmethod
    def update_level(xp):
        return floor(((sqrt(40 + xp)) / 110) + 1)

    async def update_experience(self, guild_id, user_id, amount: int = None):
        self.server_db = self.db['server'][guild_id]
        user = self.server_db.find_one_and_update({'_id': user_id}, {'$inc': {'exp': amount or random.randint(100, 150)}},
                                                  return_document=ReturnDocument.AFTER)
        user = self.server_db.find_one_and_update({'_id': user_id}, {'$set': {'level': self.update_level(user['exp'])}},
                                                  return_document=ReturnDocument.AFTER)
        return user['level'], user['exp']

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            self.server_db = self.db['server'][str(message.guild.id)]
            user = self.server_db.find_one({'_id': str(message.author.id)})
            try:
                if (user['timestamp'] + dt.timedelta(seconds=45)) <= dt.datetime.utcnow():
                    self.server_db.update_one({'_id': str(message.author.id)}, {'$set': {'timestamp': dt.datetime.utcnow()}})
                    await self.update_experience(str(message.guild.id), str(message.author.id))
            except KeyError:
                pass


def setup(bot):
    bot.add_cog(Level(bot))
