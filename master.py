import os
import json
import asyncio
import discord
from discord.ext import commands
from time import time
import datetime as dt
from lib.util import Util
from lib.mongo import Mongo
from cogs.level import Level
from cogs.profile import Profile
from cogs.thank import Thank


class Master(commands.Cog, name='Master'):
    def __init__(self, bot):
        self.bot = bot
        self.db = Mongo.init_db(Mongo())
        self.server_db = None
        self.start_time = time()

    @commands.command(name='ping')
    @commands.is_owner()
    async def ping(self, ctx):
        """Shows the bot ping in milliseconds."""
        await ctx.send(f':ping_pong: **Pong!**⠀{round(self.bot.latency, 3)}ms')

    @commands.command(name='uptime')
    async def uptime(self, ctx):
        """Shows the uptime for the bot."""
        current_time = time()
        difference = int(round(current_time - self.start_time))
        time_converted = dt.timedelta(seconds=difference)
        hours, remainder = divmod(time_converted.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        new_embed = discord.Embed()
        new_embed.add_field(name="Uptime", value='{} hours, {} minutes, {} seconds'.format(hours, minutes, seconds),
                            inline=True)
        new_embed.set_thumbnail(url='https://media.discordapp.net/attachments/742389103890268281/746419792000319580'
                                    '/shiinabat_by_erickiwi_de3oa60-pre.png?width=653&height=672')
        await ctx.send(embed=new_embed)

    @commands.command(name="update", hidden=True, pass_context=True, aliases=['change', 'modify'])
    @commands.is_owner()
    async def update(self, ctx, setting: str, update: int):
        """Administrator command"""
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
            try:
                subfields = []
                for field in config:
                    while isinstance(config[field], dict):
                        subfields.append(field)
                        field = config[field]
                    if len(subfields) > 0:
                        config = config[f'{".".join(subfields)}']
                    if field == setting:
                        config[field] = update
                        await ctx.send(embed=discord.Embed(title=f'{setting} has been changed.',
                                                           description=f'Updated: {update}'))
            except KeyError:
                await ctx.send(embed=discord.Embed(title='**[Error]** : Setting not found'))
                return
            with open(f'config/{ctx.guild.id}/config.json', 'w') as f:
                json.dump(config, f)

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        """Administrator command."""
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await discord.Message.add_reaction(ctx.message, '\U0000274E')
            error = await ctx.send(f'Failed to load module: {type(e).__name__} - {e}')
            await asyncio.sleep(10)
            await error.delete()
        else:
            await discord.Message.add_reaction(ctx.message, '\U00002705')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        """Administrator command."""
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await discord.Message.add_reaction(ctx.message, '\U0000274E')
            error = await ctx.send(f'Failed to unload module: {type(e).__name__} - {e}')
            await asyncio.sleep(10)
            await error.delete()
        else:
            await discord.Message.add_reaction(ctx.message, '\U00002705')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        """Administrator command."""
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await discord.Message.add_reaction(ctx.message, '\U0000274E')
            error = await ctx.send(f'Failed to reload module: {type(e).__name__} - {e}')
            await asyncio.sleep(10)
            await error.delete()
        else:
            await discord.Message.add_reaction(ctx.message, '\U00002705')

    @commands.command(name="build_db", hidden=True, aliases=['rebuild_db'])
    @commands.is_owner()
    async def build_db(self, ctx, member: discord.Member = None):
        """Administrator command."""
        if await Util.check_channel(ctx, True):
            pending = await ctx.send(embed=discord.Embed(title='Rebuilding Database...'))
            if member is None:
                self.db['server'].drop_collection(str(ctx.guild.id))
                self.db['server'].create_collection(str(ctx.guild.id))
            else:
                self.db['server'][str(ctx.guild.id)].find_one_and_delete({'_id': member.id})
            pending = await Level.build_level(Level(self.bot), ctx, member, pending)
            pending = await Profile.build_profile(Profile(self.bot), ctx, member, pending)
            pending = await Thank.build_thank(Thank(self.bot), ctx, member, pending)
            if member is None:
                await pending.edit(embed=discord.Embed(title='Server Rebuild Complete',
                                                       description=f'Server ID: {str(ctx.guild.id)}'))
            else:
                await pending.edit(embed=discord.Embed(title='User Rebuild Complete',
                                                       description=f'User ID: {str(member.id)}'))


def setup(bot):
    bot.add_cog(Master(bot))
