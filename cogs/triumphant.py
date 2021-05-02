import os
import json
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from lib.mongo import Mongo


class Triumphant(commands.Cog, name='Triumphant'):
    def __init__(self, bot):
        self.bot = bot
        self.db = Mongo.init_db(Mongo())
        self.server_db = None

    @commands.command(name='init_triumphant', hidden=True)
    @commands.is_owner()
    async def init_triumphant(self, ctx):
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
            triumphant_config = {
                'triumph_channel': ctx.channel.id,
                'triumph_react': None
            }
            config['triumphant_config'] = triumphant_config
            with open(f'config/{ctx.guild.id}/config.json', 'w') as f:
                json.dump(config, f, indent=2)
            await ctx.send(embed=discord.Embed(title=f'Triumphant config initialized'))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if os.path.isfile(f'config/{str(payload.guild_id)}/config.json'):
            with open(f'config/{str(payload.guild_id)}/config.json', 'r') as f:
                config = json.load(f)
                config = config['triumphant_config']
        self.server_db = self.db[str(payload.guild_id)]['users']
        guild = await self.bot.get_guild(payload.guild_id)
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        for reaction in message.reactions:
            async for user in reaction.users():
                if user.id == self.bot.user.id:
                    return
                if payload.member.bot or payload.emoji != config['triumph_react']:
                    return
        await message.add_reaction(config['triumph_react'])
        if message.embeds:
            copy_embed = message.embeds[0].to_dict()
            for member in guild.members:
                if member.name in message.embeds[0].description:

                else:
                    continue

    @commands.command(hidden=True)
    @has_permissions(manage_messages=True)
    async def triumph_delete(self, ctx, member_id: int):
        return

    @commands.command(hidden=True)
    @has_permissions(manage_messages=True)
    async def triumph_add(self, ctx, member_id: int):
        return

    @commands.command(hidden=True)
    @has_permissions(manage_messages=True)
    async def triumph_list(self, ctx, copy: str = None):
        return

    @commands.command(hidden=True)
    @has_permissions(manage_messages=True)
    async def give_triumphant(self, ctx):
        return

    @staticmethod
    async def triumphant_reset(self, server):
        return


def setup(bot):
    bot.add_cog(Triumphant(bot))
