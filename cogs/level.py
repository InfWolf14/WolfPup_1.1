import random
from math import sqrt, floor
import datetime as dt
import discord
from discord.ext import commands
from lib.util import Util
from lib.mongo import Mongo
from pymongo import ReturnDocument


class Level(commands.Cog, name='Level'):
    def __init__(self, bot):
        self.bot = bot
        self.db = Mongo.init_db(Mongo())
        self.server_db = None

    @commands.command(name='build_level', hidden=True, aliases=['rebuild_level'])
    @commands.has_guild_permissions(administrator=True)
    async def build_level(self, ctx, member: discord.Member = None, pending=None):
        self.server_db = self.db[str(ctx.guild.id)]['users']
        if pending:
            await pending.edit(embed=discord.Embed(title='Rebuilding Level stats...'))
        else:
            pending = await ctx.send(embed=discord.Embed(title='Rebuilding Level stats...'))
        if await Util.check_channel(ctx, True):
            new_level = {'level': 1, 'exp': 0, 'exp_streak': 0, 'timestamp': dt.datetime.utcnow(),
                         'flags': {'daily': True, 'thank': True}}
            if member:
                self.server_db.find_one_and_update({"_id": str(member.id)}, {'$set': new_level}, upsert=True)
                return
            for member in ctx.guild.members:
                if not member.bot:
                    new_level['exp'] = random.randint(200, 27150)
                    self.server_db.find_one_and_update({"_id": str(member.id)}, {'$set': new_level}, upsert=True)
            await pending.edit(embed=discord.Embed(title='Done'))
            return pending

    @commands.command(name='stats', pass_context=True)
    async def stats(self, ctx, member: discord.Member = None):
        """Returns a user's current profile level and experience"""
        member = member or ctx.author
        if await Util.check_channel(ctx, True):
            await self.add_experience(ctx, member, 0)

    @commands.command(name='add_experience', hidden=True, pass_context=True, aliases=['xp'])
    @commands.has_guild_permissions(administrator=True)
    async def add_experience(self, ctx, member: discord.Member, amount: int):
        if await Util.check_channel(ctx):
            if isinstance(member, discord.Member):
                user_level, user_exp = await self.update_experience(ctx.guild.id, member.id, amount)
                new_embed = discord.Embed(title=f'{member.display_name}\'s Stats',
                                          color=discord.Colour.gold())
                new_embed.add_field(name=f'**Level :**',
                                    value=user_level)
                new_embed.add_field(name=f'**Experience :**',
                                    value=user_exp)
                await ctx.send(embed=new_embed)

    @staticmethod
    def update_level(xp):
        return floor(((sqrt(40 + xp)) / 110) + 1)

    async def update_experience(self, guild_id, user_id, amount: int = None):
        self.server_db = self.db[str(guild_id)]['users']
        if amount is None:
            amount = random.randint(100, 150)
        user = self.server_db.find_one_and_update({'_id': str(user_id)}, {'$inc': {'exp': amount}},
                                                  return_document=ReturnDocument.AFTER)
        user = self.server_db.find_one_and_update({'_id': str(user_id)}, {'$set': {'level': self.update_level(user['exp'])}},
                                                  return_document=ReturnDocument.AFTER)
        return user['level'], user['exp']

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and await Util.check_exp_blacklist(message):
            self.server_db = self.db[str(message.guild.id)]['users']
            user = self.server_db.find_one({'_id': str(message.author.id)})
            try:
                if (user['timestamp'] + dt.timedelta(seconds=45)) <= dt.datetime.utcnow():
                    self.server_db.update_one({'_id': str(message.author.id)}, {'$set': {'timestamp': dt.datetime.utcnow()}})
                    await self.update_experience(message.guild.id, message.author.id)
            except KeyError:
                pass


def setup(bot):
    bot.add_cog(Level(bot))
