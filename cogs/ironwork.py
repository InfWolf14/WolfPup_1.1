import asyncio
import json
from datetime import datetime

import discord
from discord.ext import commands


class IronWorks(commands.Cog, name='IronWorks'):
    def __init__(self, bot):
        self.bot = bot
        self.url = 'https://cdn.discordapp.com/attachments/532380077896237061/786762838789849139/Cid_ARR.jpg'
        self.prefix: str = ''

    @staticmethod
    async def build_embed(self, old_embed: discord.Embed = None, author: str = None, description: str = None,
                          add: discord.Member = None, remove: discord.Member = None,
                          error: bool = False, error_type: int = 0):
        if not error:
            if old_embed:
                new_embed = discord.Embed(title=old_embed.title,
                                          description=old_embed.description,
                                          color=old_embed.color)
                new_embed.set_thumbnail(url=self.url)
                new_embed.set_footer(text=old_embed.footer.text)
                new_embed.timestamp = old_embed.timestamp
                if add:
                    user_list = old_embed.fields[0].value
                    if add.mention not in user_list:
                        user_list = user_list.replace('N/A', '')
                        user_list += '\n' + str(add.mention)
                elif remove:
                    user_list = old_embed.fields[0].value
                    if remove.mention in user_list:
                        user_list = user_list.replace(remove.mention, '')
                        if len(user_list) == 0:
                            user_list = 'N/A'
                new_embed.add_field(name=old_embed.fields[0].name,
                                    value=user_list,
                                    inline=True)
            if author and description:
                new_embed = discord.Embed(title=f'{author} has made a new commission!',
                                          description=f'\"{description}\"',
                                          color=0xff0209)
                new_embed.add_field(name='**Accepted by:**',
                                    value='N/A',
                                    inline=True)
                new_embed.set_thumbnail(url=self.url)
                new_embed.set_footer(text=f'Created by: {author}')
                new_embed.timestamp = datetime.utcnow()
        else:
            new_embed = discord.Embed(title=f'**Error**',
                                      color=0xff0209)
            if error_type == 1:
                new_embed.description = (f'Configuration for IronWorks is missing or unformatted.\n' +
                                         f'*Please contact staff for assisstance.*')
            elif error_type == 2:
                new_embed.description = (f'Please include a full description of your request.\n' +
                                         f'*{self.prefix}commission* ***<__description__>***')
            else:
                new_embed.description = (f'An unspecified error has occured while executing command.\n' +
                                         f'*Please contact staff for assistance.*')
        return new_embed

    @staticmethod
    async def build_embed_reacts(self, message, config):
        if message.reactions:
            for react in message.reactions:
                async for user in react.users():
                    if not user == self.bot.user:
                        await react.remove(user)
        else:
            await discord.Message.add_reaction(message, config['accept_emoji'])
            await discord.Message.add_reaction(message, config['un-accept_emoji'])

    @commands.command(aliases=['comm'], description="Use this to commission in #xiv-ironworks")
    async def commission(self, ctx, *args):
        """This command allows you to make commissions and connect you to crafters,
        gatherers, etc. to help complete requests!"""
        self.prefix = ctx.prefix
        guild = ctx.guild.id
        channel = await self.bot.fetch_channel(ctx.channel.id)
        author = ctx.message.author
        comm_desc = ' '.join(args)
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        try:
            config = config[str(guild)]['ironworks']
        except KeyError:
            sent = await channel.send(embed=(await self.build_embed(self, error=True, error_type=1)))
            await asyncio.sleep(5)
            await sent.delete()
            return
        if channel.id == config['channel']:
            if author.nick:
                comm_owner = str(author.nick)
            else:
                comm_owner = str(author)[:-5]
            if len(comm_desc) == 0:
                sent = await channel.send(embed=(await self.build_embed(self, error=True, error_type=2)))
                await asyncio.sleep(5)
                await sent.delete()
            else:
                await channel.send(embed=(await self.build_embed(self, author=comm_owner, description=comm_desc)))

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            return
        guild = ctx.guild.id
        channel = await self.bot.fetch_channel(ctx.channel.id)
        message = ctx
        author = message.author
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        try:
            config = config[str(guild)]['ironworks']
        except KeyError:
            sent = await channel.send(embed=(await self.build_embed(self, error=True, error_type=1)))
            await asyncio.sleep(5)
            await sent.delete()
            return
        if channel.id == config['channel']:
            if author == self.bot.user:
                if 'Error' in message.embeds[0].title:
                    return
                await self.build_embed_reacts(self, message, config)
                return
            elif author.permissions_in(channel).manage_messages and author != self.bot.user:
                if f'{self.prefix}comm' not in str(message.content)[:6]:
                    return
            await discord.Message.delete(message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, ctx):
        payload = ctx
        guild = payload.guild_id
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = await channel.guild.fetch_member(payload.user_id)
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        try:
            config = config[str(guild)]['ironworks']
        except KeyError:
            sent = await channel.send(embed=(await self.build_embed(self, error=True, error_type=1)))
            await asyncio.sleep(5)
            await sent.delete()
            return
        if channel.id == config['channel'] and message.author == self.bot.user and not member == self.bot.user and \
                message.embeds[0]:
            comm_owner = message.embeds[0].footer.text
            react_user = member.name
            if member.nick:
                react_user = member.nick
            if react_user not in comm_owner:
                if str(payload.emoji) == config['accept_emoji']:
                    await message.edit(embed=(await self.build_embed(self, old_embed=message.embeds[0], add=member)))
                elif str(payload.emoji) == config['un-accept_emoji']:
                    await message.edit(embed=(await self.build_embed(self, old_embed=message.embeds[0], remove=member)))
            elif react_user in message.embeds[0].footer.text:
                if str(payload.emoji) == config['un-accept_emoji']:
                    await discord.Message.delete(message)
                    return
            await self.build_embed_reacts(self, message, config)


def setup(bot):
    bot.add_cog(IronWorks(bot))
