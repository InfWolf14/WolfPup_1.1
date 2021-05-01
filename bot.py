import os
import json
import asyncio
import traceback as tb
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord
from discord.ext import commands
from master import Master
from lib.util import Util
from lib.mongo import Mongo
from cogs.level import Level


def get_prefix(bot, message):
    if os.path.isfile(f'config/{str(message.guild.id)}/config.json'):
        with open(f'config/{str(message.guild.id)}/config.json', 'r') as f:
            config = json.load(f)
        prefixes = [config['prefix']]
    else:
        prefixes = ['w^']
    return commands.when_mentioned_or(*prefixes)(bot, message)


initial_cogs = ['master', 'cogs.ironworks', 'cogs.leaderboard', 'cogs.level', 'cogs.mod', 'cogs.profile',
                'cogs.roles', 'cogs.starboard', 'cogs.thank', 'cogs.welcome', 'cogs.wishwall']
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix=get_prefix, description='A bot designed for GoldxGuns', intents=intents)
if __name__ == '__main__':
    for extension in initial_cogs:
        bot.load_extension(extension)
schedule = AsyncIOScheduler()


async def daily():
    """Daily Reset Timer"""
    for guild in bot.guilds:
        if os.path.isfile(f'config/{str(guild.id)}/config.json'):
            with open(f'config/{str(guild.id)}/config.json', 'r') as f:
                config = json.load(f)
        if config['channel_config']['config_channel']:
            try:
                config_channel = await bot.fetch_channel(config['channel_config']['config_channel'])
            except discord.errors.NotFound:
                return
            # Daily Reset Functions Here
            await Util.reset_user_flags(Util(), config_channel)
            await config_channel.send(embed=discord.Embed(title=f'{config_channel.guild.name} Daily Reset!'))


async def weekly():
    """Weekly reset timer"""
    for guild in bot.guilds:
        if os.path.isfile(f'config/{str(guild.id)}/config.json'):
            with open(f'config/{str(guild.id)}/config.json', 'r') as f:
                config = json.load(f)
        if config['channel_config']['config_channel']:
            try:
                config_channel = await bot.fetch_channel(config['channel_config']['config_channel'])
            except discord.errors.NotFound:
                return
            # Weekly Reset Functions Here
            await config_channel.send(embed=discord.Embed(title=f'{config_channel.guild.name} Weekly Reset!'))


async def monthly():
    """Monthly reset timer"""
    for guild in bot.guilds:
        if os.path.isfile(f'config/{str(guild.id)}/config.json'):
            with open(f'config/{str(guild.id)}/config.json', 'r') as f:
                config = json.load(f)
        if config['channel_config']['config_channel']:
            try:
                config_channel = await bot.fetch_channel(config['channel_config']['config_channel'])
            except discord.errors.NotFound:
                return
            # Monthly Reset Functions Here
            await Level.build_level(Level(bot), config_channel)
            await config_channel.send(embed=discord.Embed(title=f'{config_channel.guild.name} Monthly Reset!'))


@bot.event
async def on_member_join(member):
    with open(f'config/{str(member.guild.id)}/config.json', 'r') as f:
        config = json.load(f)
    config_channel = bot.get_channel(int(config['channel_config']['config_channel']))
    await Master.build_user_db(config_channel, member)


@bot.event
async def on_member_leave(member):
    with open(f'config/{str(member.guild.id)}/config.json', 'r') as f:
        config = json.load(f)
    config_channel = bot.get_channel(int(config['channel_config']['config_channel']))
    Mongo.init_db(Mongo())['server'][str(member.guild.id)].find_one_and_delete({'_id': str(member.id)})
    config_channel.send(embed=discord.Embed(title=f'{member.displayname} left'))


@bot.event
async def on_command_error(ctx, *e, **kwargs):
    config_channel = None
    try:
        if os.path.isfile(f'config/{str(ctx.guild.id)}/config.json'):
            with open(f'config/{str(ctx.guild.id)}/config.json', 'r') as f:
                config = json.load(f)
            config_channel = await bot.fetch_channel(config['channel_config']['config_channel'])
    except AttributeError:
        pass
    new_embed = discord.Embed(title=f'**[Error]** {type(e).__name__} error')
    try:
        new_embed.description = f'Message: \"*{ctx.content}*\"'
        await ctx.message.delete()
        new_embed.add_field(name='Traceback Information:',
                            value=''.join(tb.format_exception_only(type(e), e)).replace(':', ':\n'))
    except (AttributeError, discord.errors.NotFound):
        pass
    try:
        new_embed.set_footer(text=f'Use: [ {ctx.prefix}help ] for assistance')
    except: pass
    if config_channel is not None:
        error = await config_channel.send(embed=new_embed)
    else:
        print(''.join(tb.format_exception_only(type(e), e)).replace(':', ':\n'))
    # await asyncio.sleep(30)
    # await error.delete()


@bot.event
async def on_error(ctx, *e, **kwargs):
    config_channel = None
    try:
        if os.path.isfile(f'config/{str(ctx.guild.id)}/config.json'):
            with open(f'config/{str(ctx.guild.id)}/config.json', 'r') as f:
                config = json.load(f)
            config_channel = await bot.fetch_channel(config['channel_config']['config_channel'])
    except AttributeError: pass
    new_embed = discord.Embed(title=f'**[Error]** {type(e).__name__} error')
    try:
        new_embed.description = f'Message: \"*{ctx.content}*\"'
        await ctx.message.delete()
        new_embed.add_field(name='Traceback Information:',
                            value=''.join(tb.format_exception_only(type(e), e)).replace(':', ':\n'))
    except (AttributeError, discord.errors.NotFound):
        pass
    try:
        new_embed.set_footer(text=f'Use: [ {ctx.prefix}help ] for assistance')
    except: pass
    if config_channel is not None:
        error = await config_channel.send(embed=new_embed)
    else:
        print(''.join(tb.format_exception_only(type(e), e)).replace(':', ':\n'))
    # await asyncio.sleep(30)
    # await error.delete()


@bot.event
async def on_ready():
    print(f'\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}')
    print(f'Successfully logged in and booted...!')
    schedule.add_job(daily, 'cron', day='*', hour=18)
    schedule.add_job(weekly, 'cron', week='*', day_of_week='sun', hour=6)
    schedule.add_job(monthly, 'cron', month='*', day='1')
    schedule.start()
    for guild in bot.guilds:
        if not os.path.isdir(f'config/{guild.id}/'):
            os.makedirs(f'config/{guild.id}/')


async def on_disconnect():
    schedule.shutdown(wait=False)
    return


print('\nLoading token and connecting to client...')
token = open('token', 'r').readline()
bot.run(token, bot=True, reconnect=True)
