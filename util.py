import os
import json
import discord
from discord.ext import commands
from mongo import Mongo


class Util(commands.Cog, name='Util'):
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
                    ctx.send(embed=discord.Embed(title='This command is __only__ available in bot channels!'))
                    return False
            elif not bot_exclusive:
                if str(ctx.channel.id) in config['bot_channels']:
                    ctx.send(embed=discord.Embed(title='This command is __not__ available in bot channels!'))
                    return False
            else:
                return True


def setup(bot):
    bot.add_cog(Util(bot))
