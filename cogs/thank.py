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
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
            if str(ctx.channel.id) not in config['bot_channels']: # <- Change 'not in' to 'in' for release
                await ctx.message.delete()
                error = await ctx.send(embed=discord.Embed(title='This command is __not__ available in bot channels!'))
                await asyncio.sleep(5)
                await error.delete()
                return
        if not member.bot:
            if ctx.author == None: #member:
                new_embed = discord.Embed(
                    title='\U0001f441\U0001f441 You tried to thank yourself, shame on you \U0001f441\U0001f441')
                shame_gifs = ['https://media.giphy.com/media/NSTS6t7qKTiDu/giphy.gif',
                              'https://media.giphy.com/media/vX9WcCiWwUF7G/giphy.gif',
                              'https://media.giphy.com/media/eP1fobjusSbu/giphy.gif',
                              'https://media.giphy.com/media/Db3OfoegpwajK/giphy.gif',
                              'https://media.giphy.com/media/8UGoOaR1lA1uaAN892/giphy.gif']
                new_embed.set_image(url=random.choice(shame_gifs))
                await ctx.send(embed=new_embed)
                return
            self.server_db.find_one_and_update({'_id': str(ctx.author.id)}, {'$inc': {'thanks.thanks_given': 1,
                                                                                                'thanks.total_given': 1}})
            await Level.add_experience(Level(self.bot), ctx, ctx.author, random.randint(450, 550))
            self.server_db.find_one_and_update({'_id': str(member.id)}, {'$inc': {'thanks.thanks_recieved': 1,
                                                                                            'thanks.total_recieved': 1}})
            await Level.add_experience(Level(self.bot), ctx, member, random.randint(700, 800))
            await ctx.channel.send(embed=discord.Embed(title=f'\U0001f49d {ctx.author.display_name}'
                                                             f' has thanked {member.display_name} \U0001f49d',
                                                       color=discord.Colour.gold()))


def setup(bot):
    bot.add_cog(Thank(bot))