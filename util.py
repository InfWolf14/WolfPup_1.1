import os
import json
import asyncio
import discord
from discord.ext import commands
from mongo import Mongo
from cogs.level import Level
from cogs.profile import Profile
from cogs.thank import Thank


class Util(commands.Cog, name='Utility'):
    def __init__(self, bot):
        self.bot = bot
        self.db = Mongo.init_db(Mongo(self.bot))
        self.server_db = None

    @staticmethod
    def check_channel(ctx, bot_exclusive: bool = None):
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
            if bot_exclusive:
                if str(ctx.channel.id) not in config['bot_channels']:
                    try:
                        await ctx.message.delete()
                    except:
                        await ctx.delete()
                    await ctx.send(embed=discord.Embed(title='This command is __only__ available in bot channels!'))
                    return False
            elif not bot_exclusive:
                if str(ctx.channel.id) in config['bot_channels']:
                    try:
                        await ctx.message.delete()
                    except:
                        await ctx.delete()
                    await ctx.send(embed=discord.Embed(title='This command is __not__ available in bot channels!'))
                    return False
            else:
                return True

    @commands.command(name='ping', hidden=True)
    @commands.is_owner()
    async def ping(self, ctx):
        await ctx.send(f':ping_pong:**Pong!**⠀{round(self.bot.latency, 3)}ms')

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
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
    @commands.has_guild_permissions(administrator=True)
    async def build_db(self, ctx, member: discord.Member = None):
        """Rebuilds specified user's database doc (Rebuilds entire server if no user specified!)"""
        pending = await ctx.send(embed=discord.Embed(title='Rebuilding Database...'))
        if member is None:
            self.db['server'].drop_collection(str(ctx.guild.id))
            self.db['server'].create_collection(str(ctx.guild.id))
        else:
            self.db['server'][str(ctx.guild.id)].find_one_and_delete({'_id': str(member.id)})
        await pending.edit(embed=discord.Embed(title='Rebuilding Levels...'))
        await Level.build_level(Level(self.bot), ctx, member)
        await pending.edit(embed=discord.Embed(title='Rebuilding Profiles...'))
        await Profile.build_profile(Profile(self.bot), ctx, member)
        await pending.edit(embed=discord.Embed(title='Rebuilding Thanks...'))
        await Thank.build_thank(Thank(self.bot), ctx, member)
        if member is None:
            await pending.edit(embed=discord.Embed(title='Server Rebuild Complete',
                                                   description=f'Server ID: {str(ctx.guild.id)}'))
        else:
            await pending.edit(embed=discord.Embed(title='User Rebuild Complete',
                                                   description=f'User ID: {str(member.id)}'))


def setup(bot):
    bot.add_cog(Util(bot))
