import os
import json
import discord
from lib.mongo import Mongo


class Util:
    def __init__(self):
        self.db = Mongo.init_db(Mongo())
        self.server_db = None

    @staticmethod
    async def check_channel(ctx, bot_exclusive: bool = None):
        if not os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            await Util.reset_config(ctx)
        with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
            config = json.load(f)
        if bot_exclusive:
            if ctx.channel.id not in config['channel_config']['bot_channels']:
                await ctx.send(embed=discord.Embed(title='This command is __only__ available in bot channels!'))
                return False
        elif bot_exclusive is not None:
            if ctx.channel.id in config['channel_config']['bot_channels']:
                await ctx.send(embed=discord.Embed(title='This command is __not__ available in bot channels!'))
                return False
        return True

    @staticmethod
    async def check_exp_blacklist(ctx):
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
            if ctx.channel.id in config['channel_config']['exp_blacklist']:
                return False
            return True
        else:
            await ctx.send(embed=discord.Embed(title='**[Error]** : Server config not initialized',
                                               description='Please run initialization'))
            return

    async def reset_user_flags(self, ctx):
        self.server_db = self.db[str(ctx.guild.id)]['users']
        reset_flags = {'flags': {'daily': True, 'daily_stamp': None, 'thank': True}}
        for member in ctx.guild.members:
            if not member.bot:
                self.server_db.find_one_and_update({"_id": str(member.id)}, {'$set': reset_flags})

    @staticmethod
    async def reset_config(ctx):
        config = {
            'prefix': 'w^',
            'channel_config': {
                'config_channel': ctx.channel.id,
                'modlog_channel': ctx.channel.id,
                'rolepost_channel': ctx.channel.id,
                'welcome_channel': ctx.channel.id,
                'wishwall': ctx.channel.id,
                'ironworks': ctx.channel.id,
                'cactpot': ctx.channel.id,
                'bot_channels': [],
                'exp_blacklist': []
            },
            'role_config': {
                'top_5': None,
                'level_1': None,
                'level_2': None,
                'level_3': None,
                'level_4': None,
                'level_5': None,
                'most_wanted': None,
                'most_helpful': None,
                'most_thankful': None,
                'triumphant': None,
                'birthday': None,
                'cactpot': None,
                'top_5_blacklist': []
            }
        }
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            os.remove(f'config/{ctx.guild.id}/config.json')
        with open(f'config/{ctx.guild.id}/config.json', 'w') as f:
            json.dump(config, f, indent=2)
        await ctx.send(embed=discord.Embed(title=f'Default server config set'))
