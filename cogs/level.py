import os
import json
import random
import asyncio
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
                         'flags': {'daily': True, 'daily_stamp': dt.datetime.utcnow(), 'thank': True}}
            if member:
                self.server_db.find_one_and_update({"_id": str(member.id)}, {'$set': new_level}, upsert=True)
                return
            for member in ctx.guild.members:
                if not member.bot:
                    new_level['exp'] = random.randint(100, 15000)
                    self.server_db.find_one_and_update({"_id": str(member.id)}, {'$set': new_level}, upsert=True)
            await pending.edit(embed=discord.Embed(title='Done'))
            return pending

    @commands.command(name='stats', pass_context=True)
    async def stats(self, ctx, member: discord.Member = None):
        """Returns a user's current profile level and experience"""
        await ctx.message.delete()
        member = member or ctx.author
        if await Util.check_channel(ctx, True):
            await self.add_experience(ctx, member, 0)

    @commands.command(name='daily')
    async def daily(self, ctx, member: discord.Member = None):
        """Use to claim your daily exp bonus or give to a friend!"""
        self.server_db = self.db[str(ctx.guild.id)]['users']
        if member is None:
            member = ctx.author
        if await Util.check_channel(ctx, True):
            self.server_db.find_one_and_update({'_id': str(ctx.author.id)}, {'$inc': {'exp_streak': 1}})
            user = self.server_db.find_one({'_id': str(ctx.author.id)})
            if user['flags']['daily']:
                streak = user['exp_streak']
                new_embed = discord.Embed(title='You\'ve claimed your daily bonus!',
                                          color=discord.Colour.gold())
                new_embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/532380077896237061/800924153053970476'
                                            '/terry_coin.png')
                if member != ctx.author:
                    new_embed.title = 'You\'ve given your bonus to your friend!'
                try:
                    if (user['flags']['daily_stamp']+dt.timedelta(hours=36)) < dt.datetime.utcnow():
                        new_embed.description = f'This is day {streak}. You missed your streak window...'
                        self.server_db.find_one_and_update({'_id': str(ctx.author.id)}, {'$set': {'exp_streak': 0}})
                        streak -= 1
                except TypeError:
                    pass
                else:
                    if streak >= 5:
                        new_embed.description = '__BONUS__ This is your 5-day streak! __BONUS__'
                        self.server_db.find_one_and_update({'_id': str(ctx.author.id)}, {'$set': {'exp_streak': 0}})
                        streak = 10
                    else:
                        new_embed.description = f'This is day {streak}. Keep it up to day 5!'
                self.server_db.find_one_and_update({'_id': str(ctx.author.id)}, {'$set': {'flags.daily': False}})
                self.server_db.find_one_and_update({'_id': str(ctx.author.id)}, {'$set': {'flags.daily_stamp': dt.datetime.utcnow()}})
                daily_exp = int(random.randint(150, 250)*(1+(0.15*streak)))
                await self.update_experience(ctx.guild.id, member.id, daily_exp)
                await ctx.send(embed=new_embed)
            else:
                await ctx.message.delete()
                pending = await ctx.send(embed=discord.Embed(title='You\'ve already claimed your daily bonus today!'))
                await asyncio.sleep(5)
                await pending.delete()

    @commands.command(name='add_experience', hidden=True, pass_context=True, aliases=['xp'])
    @commands.has_guild_permissions(administrator=True)
    async def add_experience(self, ctx, member: discord.Member, amount: int):
        """Used to award exp to a specified user"""
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
        if os.path.isfile(f'config/{guild_id}/config.json'):
            with open(f'config/{guild_id}/config.json', 'r') as f:
                config = json.load(f)
        self.server_db = self.db[str(guild_id)]['users']
        if amount is None:
            amount = random.randint(100, 150)
        guild = await self.bot.fetch_guild(int(guild_id))
        member = await guild.fetch_member(int(user_id))
        user = self.server_db.find_one_and_update({'_id': str(user_id)}, {'$inc': {'exp': amount}},
                                                  return_document=ReturnDocument.AFTER)
        user = self.server_db.find_one_and_update({'_id': str(user_id)}, {'$set': {'level': self.update_level(user['exp'])}},
                                                  return_document=ReturnDocument.AFTER)
        if guild.get_role(config['role_config'][f'level_{user["level"]}']) not in member.roles:
            for x in range(5):
                if guild.get_role(config['role_config'][f'level_{x+1}']) in member.roles:
                    await member.remove_roles(guild.get_role(config['role_config'][f'level_{x+1}']))
            if user["level"] > 1:
                await member.add_roles(guild.get_role(config['role_config'][f'level_{user["level"]}']))
        await self.generate_top_5(guild.id)
        return user['level'], user['exp']

    async def generate_top_5(self, guild_id):
        if os.path.isfile(f'config/{guild_id}/config.json'):
            with open(f'config/{guild_id}/config.json', 'r') as f:
                config = json.load(f)
        self.server_db = self.db[str(guild_id)]['users']
        guild = self.bot.get_guild(guild_id)
        users = self.server_db.find().sort('exp', -1)[0:5]
        top_5 = []
        for user in users:
            top_5.append(int(user['_id']))
        for member in guild.members:
            if member.id in top_5 and guild.get_role(config['role_config']['top_5']) not in member.roles:
                for role in member.roles:
                    if role.id in config['role_config']['top_5_blacklist']:
                        continue
                await member.add_roles(guild.get_role(config['role_config']['top_5']))
            elif member.id not in top_5 and guild.get_role(config['role_config']['top_5']) in member.roles:
                await member.remove_roles(guild.get_role(config['role_config']['top_5']))

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            return
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
