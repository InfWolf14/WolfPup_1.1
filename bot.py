import os
import json
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord
from discord.ext import commands
from util import Util
from mongo import Mongo


def get_prefix(bot, message):
    if os.path.isfile(f'config/{str(message.guild.id)}/config.json'):
        with open(f'config/{str(message.guild.id)}/config.json', 'r') as f:
            config = json.load(f)
        prefixes = [config['prefix']]
    else:
        prefixes = ['w^']
    return commands.when_mentioned_or(*prefixes)(bot, message)


initial_cogs = ['util', 'cogs.level', 'cogs.profile', 'cogs.thank']
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=get_prefix, description='A bot designed for GoldxGuns', intents=intents)
if __name__ == '__main__':
    for extension in initial_cogs:
        bot.load_extension(extension)
schedule = AsyncIOScheduler()


async def daily():
    """Daily Reset Timer"""
    print('Daily Reset')


async def weekly():
    """Weekly reset timer"""
    print('Weekly Reset')


async def monthly():
    """Monthly reset timer"""
    print('Monthly Reset')


@bot.event
async def on_member_join(member):
    with open(f'config/{str(member.guild.id)}/config.json', 'r') as f:
        config = json.load(f)
    config_channel = bot.get_channel(int(config['config_channel']))
    await Util.build_db(config_channel, member)

@bot.event
async def on_member_leave(member):
    with open(f'config/{str(member.guild.id)}/config.json', 'r') as f:
        config = json.load(f)
    config_channel = bot.get_channel(int(config['config_channel']))
    Mongo.init_db(Mongo(Mongo(bot)))['server'][str(member.guild.id)].find_one_and_delete({'_id': str(member.id)})
    config_channel.send(embed=discord.Embed(title=f'{member.displayname} left'))

@bot.event
async def on_command_error(ctx, error):
    try:
        await ctx.message.delete()
    except discord.errors.NotFound:
        pass
    if isinstance(error, commands.MissingRequiredArgument):
        error = await ctx.send(embed=discord.Embed(title='**[Error]** : Command missing arguments!'))
    elif isinstance(error, commands.MissingPermissions):
        error = await ctx.send(embed=discord.Embed(title='**[Error]** : You are missing required permissions!'))
    elif isinstance(error, commands.CommandNotFound):
        error = await ctx.send(embed=discord.Embed(title='**[Error]** : Command not found!'))
    else:
        new_embed = discord.Embed(title=f'**[Error]** : {type(error).__name__}',
                                           description=f'{error.__cause__}')
        new_embed.set_footer(text='Please contact an administrator')
        await ctx.send(embed=new_embed)
        return
    await asyncio.sleep(5)
    await error.delete()

@bot.event
async def on_ready():
    print(f'\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}')
    print(f'Successfully logged in and booted...!')
    schedule.add_job(daily, 'cron', day='*', hour=18)
    schedule.add_job(weekly, 'cron', week='*', day_of_week='sun', hour=6)
    schedule.add_job(monthly, 'cron', month='*', day='1')
    schedule.start()


async def on_disconnect():
    schedule.shutdown(wait=False)
    return


print('\nLoading token and connecting to client...')
token = open("token.txt", "r").readline()
bot.run(token, bot=True, reconnect=True)
