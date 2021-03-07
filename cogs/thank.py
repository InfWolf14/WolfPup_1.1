import os
import json
import asyncio
import random
import discord
from discord.ext import commands
from mongo import Mongo
from cogs.level import Level


class Thank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Mongo.init_db(Mongo(self.bot))
        self.server_db = None

    @commands.command(name='build_thank', hidden=True, aliases=['rebuild_thank'])
    @commands.has_guild_permissions(administrator=True)
    async def build_thank(self, ctx, member: discord.Member = None):
        self.server_db = self.db['server'][str(ctx.guild.id)]
        new_thank = {'thanks': {'thanks_received': 0, 'total_received': 0,
                               'thanks_given': 0, 'total_given': 0}}
        if member:
            self.server_db.find_one_and_update({'_id': str(member.id)}, {'$set': new_thank}, upsert=True)
            return
        for member in ctx.guild.members:
            if not member.bot:
                self.server_db.find_one_and_update({'_id': str(member.id)}, {'$set': new_thank}, upsert=True)

    @commands.command(name='thank', aliases=['thanks'])
    async def thank(self, ctx, member: discord.Member):
        self.server_db = self.db['server'][str(ctx.guild.id)]
        if not member.bot:
            thanker = self.server_db.find_one_and_update({'_id': str(ctx.author.id)}, {'$inc': {'thanks.thanks_given': 1,
                                                                                                'thanks.total_given': 1}})
            thankee = self.server_db.find_one_and_update({'_id': str(member.id)}, {'$inc': {'thanks.thanks_recieved': 1,
                                                                                            'thanks.total_recieved': 1}})
            for _, user_data in enumerate(thanker, thankee):
                await Level.update_experience(Level(self.bot), ctx.guild.id, user_data['_id'], random.randint(800, 950))
        await ctx.send(embed=discord.Embed(title=f'\U0001f49d {ctx.author.name} has thanked {thankee.name} \U0001f49d',
                                           colour=discord.Colour.gold()))


def setup(bot):
    bot.add_cog(Thank(bot))