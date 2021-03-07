import json
import discord
from discord.ext import commands
from mongo import Mongo


class Thank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Mongo.init_db(Mongo(self.bot))
        self.server_db = None

    @commands.command(name='build_thank', hidden=True, aliases=['rebuild_thank'])
    @commands.has_guild_permissions(administrator=True)
    async def build_thank(self, ctx, member: discord.Member = None):
        self.server_db = self.db['server'][str(ctx.guild.id)]
        new_thank = {'thank': {'thank_received': 0, 'total_received': 0,
                               'thank_given': 0, 'total_given': 0}}
        if member:
            self.server_db.find_one_and_update({'_id': str(member.id)}, {'$set': new_thank}, upsert=True)
            return
        for member in ctx.guild.members:
            if not member.bot:
                self.server_db.find_one_and_update({'_id': str(member.id)}, {'$set': new_thank}, upsert=True)


def setup(bot):
    bot.add_cog(Thank(bot))