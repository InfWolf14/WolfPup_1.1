import discord
from discord.ext import commands
from mongo import Mongo


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Mongo.init_db(Mongo(self.bot))
        self.server_db = None

    @commands.command(name='leaderboard', aliases=['lb'])
    async def leaderboard(self, ctx, member: discord.Member = None):
        self.server_db = self.db['server'][str(ctx.guild.id)]



def setup(bot):
    bot.add_cog(Leaderboard(bot))
