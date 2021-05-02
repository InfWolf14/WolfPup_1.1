import os
import json
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from lib.mongo import Mongo


class Triumphant(commands.Cog, name='Triumphant'):
    def __init__(self, bot):
        self.bot = bot
        self.db = Mongo.init_db(Mongo())
        self.server_db = None

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        return

    @commands.command(hidden=True)
    @has_permissions(manage_messages=True)
    async def triumph_delete(self, ctx, member_id: int):
        return

    @commands.command(hidden=True)
    @has_permissions(manage_messages=True)
    async def triumph_add(self, ctx, member_id: int):
        return

    @commands.command(hidden=True)
    @has_permissions(manage_messages=True)
    async def triumph_list(self, ctx, copy: str = None):
        return

    @commands.command(hidden=True)
    @has_permissions(manage_messages=True)
    async def give_triumphant(self, ctx):
        return

    @staticmethod
    async def triumphant_reset(self, server):
        return

def setup(bot):
    bot.add_cog(Triumphant(bot))
