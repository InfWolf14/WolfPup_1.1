import os
import json
import discord


class Util:
    @staticmethod
    async def check_channel(ctx, bot_exclusive: bool = None):
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
            if bot_exclusive:
                if ctx.channel.id not in config['bot_channels']:
                    await ctx.send(embed=discord.Embed(title='This command is __only__ available in bot channels!'))
                    return False
            elif bot_exclusive is not None:
                if ctx.channel.id in config['bot_channels']:
                    await ctx.send(embed=discord.Embed(title='This command is __not__ available in bot channels!'))
                    return False
            return True

    @staticmethod
    async def check_exp_blacklist(ctx):
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
            if ctx.channel.id in config['exp_channel_blacklist']:
                return False
            return True
