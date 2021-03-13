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

    @commands.command(name='change_prefix', hidden=True, aliases=['prefix'])
    @commands.is_owner()
    async def change_prefix(self, ctx, prefix: str):
        """Administrator command"""
        if await Util.check_channel(ctx, True):
            if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
                with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                    config = json.load(f)
                if len(prefix) > 3:
                    await ctx.send(embed=discord.Embed(title='Bot prefix must be 3 or less characters'))
                    return
                config['prefix'] = prefix
                with open(f'config/{ctx.guild.id}/config.json', 'w') as f:
                    json.dump(config, f)

    @commands.command(name="channel_config", hidden=True)
    @commands.is_owner()
    async def channel_config(self, ctx, setting: str, update: str):
        """Administrator command"""
        if await Util.check_channel(ctx, True):
            if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
                with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                    config = json.load(f)
                try:
                    if isinstance(config['channel_config'][setting], list):
                        if '?' in update:
                            config['channel_config'][setting].remove(int(update.replace('?', '')))
                            update = f'Removed {update.replace("?", "")}'
                        else:
                            config['channel_config'][setting].append(int(update))
                    else:
                        config['channel_config'][setting] = int(update)
                    await ctx.send(embed=discord.Embed(title=f'Successfully updated \'{setting}\'',
                                                       description=update))
                except KeyError:
                    await ctx.send(embed=discord.Embed(title=f'**[Error]** : \'{setting}\' not found'))
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
