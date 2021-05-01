import os
import json
import asyncio
from datetime import datetime
import discord
from discord.ext import commands


class IronWorks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = ''
        self.url = 'https://cdn.discordapp.com/attachments/532380077896237061/786762838789849139/Cid_ARR.jpg'

    @commands.command(name='init_ironworks', hidden=True, aliases=['init_iw', 'iw_init'])
    @commands.is_owner()
    async def init_ironworks(self, ctx):
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
            ironworks_config = {
                'ironworks_channel': ctx.channel.id,
                'conf_react': None,
                'decl_react': None
            }
            config['ironworks_config'] = ironworks_config
            with open(f'config/{ctx.guild.id}/config.json', 'w') as f:
                json.dump(config, f, indent=2)
            await ctx.send(embed=discord.Embed(title=f'Ironworks config initialized'))

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

    async def build_embed_reacts(self, message, config):
        if message.reactions:
            for react in message.reactions:
                async for user in react.users():
                    if not user == self.bot.user:
                        await react.remove(user)
        else:
            await discord.Message.add_reaction(message, self.bot.get_emoji(config['accept_emoji']))
            await discord.Message.add_reaction(message, self.bot.get_emoji(config['un-accept_emoji']))

    @commands.command(aliases=['comm'], description="Use this to commission in #xiv-ironworks")
    async def commission(self, ctx, *args):
        """This command allows you to make commissions and connect you to crafters,
        gatherers, etc. to help complete requests!"""
        self.prefix = ctx.prefix
        channel = await self.bot.fetch_channel(ctx.channel.id)
        comm_desc = ' '.join(args)
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
        try:
            config = config['ironworks_config']
        except KeyError:
            sent = await channel.send(embed=(await self.build_embed(error=True, error_type=1)))
            await asyncio.sleep(5)
            await sent.delete()
            return
        if channel.id == config['ironworks_channel']:
            if ctx.message.author.nick:
                comm_owner = str(ctx.message.author.nick)
            else:
                comm_owner = str(ctx.message.author)[:-5]
            if len(comm_desc) == 0:
                sent = await channel.send(embed=(await self.build_embed(error=True, error_type=2)))
                await asyncio.sleep(5)
                await sent.delete()
            else:
                await channel.send(embed=(await self.build_embed(author=comm_owner, description=comm_desc)))

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author == self.bot.user:
            return
        channel = await self.bot.fetch_channel(ctx.channel.id)
        if os.path.isfile(f'config/{str(ctx.guild.id)}/config.json'):
            with open(f'config/{str(ctx.guild.id)}/config.json', 'r') as f:
                config = json.load(f)
        try:
            config = config['ironworks_config']
        except KeyError:
            sent = await channel.send(embed=(await self.build_embed(error=True, error_type=1)))
            await asyncio.sleep(5)
            await sent.delete()
            return
        if channel.id == config['ironworks_channel']:
            if ctx.author == self.bot.user:
                if 'Error' in ctx.embeds[0].title:
                    return
                await self.build_embed_reacts(ctx, config)
                return
            elif ctx.author.permissions_in(channel).manage_messages and ctx.author != self.bot.user:
                if f'{self.prefix}comm' not in str(ctx.content)[:6]:
                    return
            await discord.Message.delete(ctx)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, ctx):
        payload = ctx
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = await channel.guild.fetch_member(payload.user_id)
        if os.path.isfile(f'config/{str(ctx.guild_id)}/config.json'):
            with open(f'config/{str(ctx.guild_id)}/config.json', 'r') as f:
                config = json.load(f)
        try:
            config = config['ironworks_config']
        except KeyError:
            sent = await channel.send(embed=(await self.build_embed(error=True, error_type=1)))
            await asyncio.sleep(5)
            await sent.delete()
            return
        if channel.id == config['ironworks_channel'] and message.author == self.bot.user and not member == self.bot.user and \
                message.embeds[0]:
            comm_owner = message.embeds[0].footer.text
            react_user = member.name
            if member.nick:
                react_user = member.nick
            if react_user not in comm_owner:
                if str(payload.emoji.name) == config['conf_emoji']:
                    await message.edit(embed=(await self.build_embed(old_embed=message.embeds[0], add=member)))
                elif str(payload.emoji.name) == config['decl_emoji']:
                    await message.edit(embed=(await self.build_embed(old_embed=message.embeds[0], remove=member)))
            elif react_user in message.embeds[0].footer.text:
                if str(payload.emoji.name) == config['decl_emoji']:
                    await discord.Message.delete(message)
                    return
            await self.build_embed_reacts(message, config)


def setup(bot):
    bot.add_cog(IronWorks(bot))
