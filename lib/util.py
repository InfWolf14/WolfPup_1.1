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
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
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
            if ctx.channel.id in config['channel_config']['exp_channel_blacklist']:
                return False
            return True

    async def reset_flags(self, ctx):
        self.server_db = self.db['server'][str(ctx.guild.id)]
        reset_flags = {'flags': {'daily': True, 'thank': True}}
        for member in ctx.guild.members:
            if not member.bot:
                self.server_db.find_one_and_update({"_id": str(member.id)}, {'$set': reset_flags})
