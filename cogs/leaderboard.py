import asyncio
import discord
from discord.ext import commands
from util import Util
from mongo import Mongo


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Mongo.init_db(Mongo(self.bot))
        self.server_db = None
        self.leaderboards = {'exp': {'exp', 'experience', 'xp'},
                             'thanks.thanks_received': {'thankee'},
                             'thanks.thanks_given': {'thanker'}}

    @commands.command(name='leaderboard', aliases=['lb'])
    async def leaderboard(self, ctx, leaderboard):
        self.server_db = self.db['server'][str(ctx.guild.id)]
        if await Util.check_channel(ctx):
            new_embed = discord.Embed(title='Leaderboard')
            for stat in self.leaderboards:
                if leaderboard in self.leaderboards[stat]:
                    users = self.server_db.find().sort(leaderboard, -1)
                    rank = 1
                    listing = ''
                    f_name = ''
                    stat_1, stat_2 = None, None
                    for user in users:
                        try:
                            stat_1, stat_2 = stat.split('.')
                        except ValueError: pass
                        if stat_2 is not None:
                            f_name = f'__**{stat_2.capitalize().replace("_", " ")}**__'
                            listing += f'`[{str(rank)}.]` {self.bot.get_user(int(user["_id"])).name} : {user[stat_1][stat_2]}\n'
                        else:
                            f_name = f'__**{stat.capitalize()}**__'
                            listing += f'`[{str(rank)}.]` {self.bot.get_user(int(user["_id"])).name} : {user[stat]}\n'
                        rank += 1
                    new_embed.add_field(name=f_name,
                                        value=listing)
                    await ctx.send(embed=new_embed)
                    return


def setup(bot):
    bot.add_cog(Leaderboard(bot))
