import json
import os
import discord
from discord.ext import commands


class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
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
        new_embed.add_field(name='Traceback Information:', value=''.join(tb.format_exception_only(type(e), e)).replace(':', ':\n'))
        new_embed.set_footer(text=f'Use: [ {ctx.prefix}help ] for assistance')
        if config_channel is not None:
            error = await config_channel.send(embed=new_embed)
        else:
            error = await ctx.send(embed=new_embed)
        # await asyncio.sleep(30)
        # await error.delete()


    @commands.Cog.listener()
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
        new_embed.add_field(name='Traceback Information:', value=''.join(tb.format_exception_only(type(e), e)).replace(':', ':\n'))
        new_embed.set_footer(text=f'Use: [ {ctx.prefix}help ] for assistance')
        if config_channel is not None:
            error = await config_channel.send(embed=new_embed)
        else:
            error = await ctx.send(embed=new_embed)
        # await asyncio.sleep(30)
        # await error.delete()


def setup(bot):
    bot.add_cog(Error(bot))