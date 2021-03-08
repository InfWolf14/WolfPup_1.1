import discord
from discord.ext import commands
from util.util import Util
from util.util import Mongo


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Mongo.init_db(Mongo(self.bot))
        self.server_db = None
        self.leaderboards = {'exp': {'exp', 'experience', 'xp'},
                             'thanks.thanks_received': {'thankee'},
                             'thanks.thanks_given': {'thanker'}}

    @commands.command(name='leaderboard', aliases=['lb'])
    async def leaderboard(self, ctx, leaderboard: str = None):
        self.server_db = self.db['server'][str(ctx.guild.id)]
        if await Util.check_channel(ctx):
            new_embed = discord.Embed(title=f'{ctx.guild.name} Leaderboard',
                                      color=discord.Colour.gold())
            if leaderboard is not None:
                for stat in self.leaderboards:
                    if leaderboard in self.leaderboards[stat]:
                        users = self.server_db.find().sort(leaderboard, -1)
                        rank = 1
                        listing, list_user, f_name, user_str = '', '', '', ''
                        stat_1, stat_2, my_stat = None, None, None
                        for user in users:
                            list_user = self.bot.get_user(int(user["_id"]))
                            if rank < 21:
                                try:
                                    stat_1, stat_2 = stat.split('.')
                                except ValueError: pass
                                if stat_2 is not None:
                                    f_name = f'**__Stat:__ {stat_2.capitalize().replace("_", " ")}**'
                                    user_str = f'`[{str(rank)}.]` *{list_user.name} :* {user[stat_1][stat_2]}'
                                else:
                                    f_name = f'**__Stat:__ {stat.capitalize()}**'
                                    user_str = f'`[{str(rank)}.]` *{list_user.name} :* {user[stat]}'
                                if list_user == ctx.author:
                                    my_stat = user_str
                                    user_str = f'**>>>** {user_str}'
                                listing += f'{user_str}\n'
                                rank += 1
                        if my_stat is not None:
                            listing += f'\n__**Your Ranking:**__\n{my_stat}'
                        new_embed.add_field(name=f_name,
                                            value=listing,
                                            inline=True)
                        await ctx.send(embed=new_embed)
                        return


def setup(bot):
    bot.add_cog(Leaderboard(bot))
