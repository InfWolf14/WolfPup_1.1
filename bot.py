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
from cogs.triumphant import Triumphant
from cogs.mod import Mod


def get_prefix(bot, message):
    if os.path.isfile(f'config/{str(message.guild.id)}/config.json'):
        with open(f'config/{str(message.guild.id)}/config.json', 'r') as f:
            config = json.load(f)
        prefixes = [config['prefix']]
    else:
        prefixes = ['*']
    return commands.when_mentioned_or(*prefixes)(bot, message)


initial_cogs = ['master', 'cogs.mod', 'cogs.welcome',
                'cogs.level', 'cogs.profile', 'cogs.thank', 'cogs.leaderboard', 'cogs.friend',
                'cogs.games', 'cogs.roles', 'cogs.starboard', 'cogs.timer', 'cogs.triumphant']
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
            await Level.daily_bday_reset(Level(bot), guild)
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
            await Triumphant.triumphant_reset(Triumphant(bot), guild)
            await config_channel.send(embed=discord.Embed(title=f'{config_channel.guild.name} Weekly Reset!'))


async def cactpot():
    """Cactpot Reminder"""
    for server in bot.guilds:
        with open(f'config/{str(server.id)}/config.json', 'r') as f:
            config = json.load(f)
        role = server.get_role(int(config['role_config']['cactpot']))
        channel = bot.get_channel(int(config['channel_config']['cactpot']))
        if not role or not channel:
            return
        embed = discord.Embed(title='**The JumboCactPot has been drawn!**', description="Don't forget to check your "
                                                                                        "tickets within the hour for the "
                                                                                        "Early Bird bonus (+7%). If the "
                                                                                        "Jackpot II action isn't activated"
                                                                                        " on the Free Company, then please "
                                                                                        "activate it now.")
        embed.set_image(url="https://img.finalfantasyxiv.com/lds/blog_image/jp_blog/jp20170607_iw_04.png")

        await channel.send({role.ment})
        await channel.send(embed=embed)


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
            await Mod.award_monthly_roles(Mod(bot), guild)
            await config_channel.send(embed=discord.Embed(title=f'{config_channel.guild.name} Monthly Reset!'))


@bot.event
async def on_command_error(self, ctx, e):
    config_channel = None
    if os.path.isfile(f'config/{str(ctx.guild.id)}/config.json'):
        with open(f'config/{str(ctx.guild.id)}/config.json', 'r') as f:
            config = json.load(f)
        config_channel = await self.bot.fetch_channel(config['channel_config']['config_channel'])
    new_embed = discord.Embed(title=f'**[Error]** {type(e).__name__} **[Error]**')
    try:
        new_embed.description = f'Message: \"*{ctx.message.content}*\"'
        await ctx.message.delete()
    except discord.errors.NotFound:
        pass
    new_embed.add_field(name='Traceback Information:',
                        value=''.join(tb.format_exception_only(type(e), e)).replace(':', ':\n'))
    new_embed.set_footer(text=f'Use: [ {ctx.prefix}help ] for assistance')
    if config_channel is not None:
        error = await config_channel.send(embed=new_embed)
    else:
        error = await ctx.send(embed=new_embed)
    # await asyncio.sleep(30)
    # await error.delete()


@bot.event
async def on_error(self, ctx, e):
    config_channel = None
    if os.path.isfile(f'config/{str(ctx.guild.id)}/config.json'):
        with open(f'config/{str(ctx.guild.id)}/config.json', 'r') as f:
            config = json.load(f)
        config_channel = await self.bot.fetch_channel(config['channel_config']['config_channel'])
    new_embed = discord.Embed(title=f'**[Error]** {type(e).__name__} **[Error]**')
    try:
        new_embed.description = f'Message: \"*{ctx.message.content}*\"'
        await ctx.message.delete()
    except discord.errors.NotFound:
        pass
    new_embed.add_field(name='Traceback Information:',
                        value=''.join(tb.format_exception_only(type(e), e)).replace(':', ':\n'))
    new_embed.set_footer(text=f'Use: [ {ctx.prefix}help ] for assistance')
    if config_channel is not None:
        error = await config_channel.send(embed=new_embed)
    else:
        error = await ctx.send(embed=new_embed)
    # await asyncio.sleep(30)
    # await error.delete()

@bot.event
async def on_member_join(member):
    with open(f'config/{str(member.guild.id)}/config.json', 'r') as f:
        config = json.load(f)
    config_channel = bot.get_channel(int(config['channel_config']['config_channel']))
    await Master.build_user_db(config_channel, member)


@bot.event
async def on_member_remove(member):
    with open(f'config/{str(member.guild.id)}/config.json', 'r') as f:
        config = json.load(f)
    config_channel = bot.get_channel(int(config['channel_config']['config_channel']))
    Mongo.init_db(Mongo())['server'][str(member.guild.id)].find_one_and_delete({'_id': str(member.id)})
    await config_channel.send(f"{member.name}'s data was deleted")

@bot.event
async def on_ready():
    print(f'\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}')
    print(f'Successfully logged in and booted...!')
    schedule.add_job(daily, 'cron', day='*', hour=18)
    schedule.add_job(weekly, 'cron', week='*', day_of_week='sat', hour=22)
    schedule.add_job(monthly, 'cron', month='*', day='1')
    schedule.add_job(cactpot, 'cron', week='*', day_of_week='sat', hour=20)
    schedule.start()
    for guild in bot.guilds:
        if not os.path.isdir(f'config/{guild.id}/'):
            os.makedirs(f'config/{guild.id}/')


async def on_disconnect():
    schedule.shutdown(wait=False)
    return


print('\nLoading token and connecting to client...')
token = open('token.txt', 'r').readline()
bot.run(token, bot=True, reconnect=True)
