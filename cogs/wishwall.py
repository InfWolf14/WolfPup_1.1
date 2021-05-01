import os
import json
import asyncio
from datetime import datetime
import discord
from discord.ext import commands
from discord.utils import get


class WishWall(commands.Cog, name='WishWall'):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = ''
        self.url = 'https://cdn.discordapp.com/attachments/767568459939708950/800966534956318720/destiny_icon_grey.png'

    @commands.command(name='init_wishwall', hidden=True, aliases=['init_ww', 'ww_init'])
    @commands.is_owner()
    async def init_wishwall(self, ctx):
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
            wishwall_config = {
                'wishwall_channel': ctx.channel.id,
                'conf_react': None,
                'decl_react': None
            }
            config['wishwall_config'] = wishwall_config
            with open(f'config/{ctx.guild.id}/config.json', 'w') as f:
                json.dump(config, f, indent=2)
            await ctx.send(embed=discord.Embed(title=f'WishWall config initialized'))

    @staticmethod
    async def build_embed(self, old_embed: discord.Embed = None,
                          author: str = None, platform: str = None, description: str = None,
                          add: discord.Member = None, remove: discord.Member = None,
                          error: bool = False, error_type: int = 0):
        if not error:
            if old_embed:
                new_embed = discord.Embed(title=old_embed.title,
                                          description=old_embed.description,
                                          color=old_embed.color)
                new_embed.add_field(name=old_embed.fields[0].name,
                                    value=old_embed.fields[0].value,
                                    inline=True)
                new_embed.set_thumbnail(url=self.url)
                new_embed.set_footer(text=old_embed.footer.text)
                new_embed.timestamp = old_embed.timestamp
                if add:
                    user_list = old_embed.fields[1].value
                    if add.mention not in user_list:
                        user_list = user_list.replace('N/A', '')
                        user_list += '\n' + str(add.mention)
                elif remove:
                    user_list = old_embed.fields[1].value
                    if remove.mention in user_list:
                        user_list = user_list.replace(remove.mention, '')
                        if len(user_list) == 0:
                            user_list = 'N/A'
                new_embed.add_field(name=old_embed.fields[1].name,
                                    value=user_list,
                                    inline=True)
            if author and platform and description:
                new_embed = discord.Embed(title=f'{author} has made a new wish!',
                                          description=f'\"{description}\"',
                                          color=0xff0209)
                new_embed.add_field(name='**Platform:**',
                                    value=f'{platform}',
                                    inline=True)
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
                new_embed.description = (f'Configuration for WishWall is missing or unformatted.\n' +
                                         f'*Please contact staff for assistance.*')
            elif error_type == 2:
                new_embed.description = (f'Missing argument. Please properly format your wish.\n' +
                                         f'*{self.prefix}wish* ***<__platform__>*** *<description>*')
            elif error_type == 3:
                new_embed.description = (f'Missing argument. Please properly format your wish.\n' +
                                         f'*{self.prefix}wish <platform>* ***<__description__>***')
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
            await discord.Message.add_reaction(message, config['conf_react'])
            await discord.Message.add_reaction(message, config['decl_react'])

    @commands.command(name='wish')
    async def wish(self, ctx, platform: str = None, *args):
        """Use this in the WishWall channel to make a wish!"""
        self.prefix = ctx.prefix
        channel = await self.bot.fetch_channel(ctx.channel.id)
        author = ctx.message.author
        ps_emote = get(ctx.message.guild.emojis, name='ps4')
        xb_emote = get(ctx.message.guild.emojis, name='xbox')
        pc_emote = get(ctx.message.guild.emojis, name='pc')
        alias_list = {f'{ps_emote} Playstation': {'playstation', 'ps'},
                      f'{xb_emote} Xbox': {'xbox', 'xb'},
                      f'{pc_emote} Steam': {'pc', 'steam'}}
        if platform:
            for alias in alias_list:
                if platform.lower() in alias_list[alias]:
                    platform = alias
                    break
            if platform not in alias_list.keys():
                platform = None
        wish_desc = ' '.join(args)
        if os.path.isfile(f'config/{str(ctx.guild.id)}/config.json'):
            with open(f'config/{str(ctx.guild.id)}/config.json', 'r') as f:
                config = json.load(f)
        try:
            config = config['wishwall_config']
        except KeyError:
            sent = await channel.send(embed=(await self.build_embed(self, error=True, error_type=1)))
            await asyncio.sleep(5)
            await sent.delete()
            return
        if channel.id == config['wishwall_channel']:
            if author.nick:
                wish_owner = str(author.nick)
            else:
                wish_owner = str(author)[:-5]
            if not platform:
                sent = await channel.send(embed=(await self.build_embed(self, error=True, error_type=2)))
                await asyncio.sleep(5)
                await sent.delete()
            elif len(wish_desc) == 0:
                sent = await channel.send(embed=(await self.build_embed(self, error=True, error_type=3)))
                await asyncio.sleep(5)
                await sent.delete()
            else:
                await channel.send(embed=(await self.build_embed(self, author=wish_owner, platform=platform, description=wish_desc)))

    @commands.Cog.listener()
    async def on_message(self, ctx):
        channel = await self.bot.fetch_channel(ctx.channel.id)
        if os.path.isfile(f'config/{str(ctx.guild.id)}/config.json'):
            with open(f'config/{str(ctx.guild.id)}/config.json', 'r') as f:
                config = json.load(f)
        try:
            config = config['wishwall_config']
        except KeyError:
            sent = await channel.send(embed=(await self.build_embed(self, error=True, error_type=1)))
            await asyncio.sleep(5)
            await sent.delete()
            return
        if channel.id == config['wishwall_channel']:
            if ctx.author == self.bot.user:
                if 'Error' in ctx.embeds[0].title:
                    return
                await self.build_embed_reacts(ctx, config)
                return
            elif ctx.author.permissions_in(channel).manage_messages and ctx.author != self.bot.user:
                if f'{self.prefix}wish' not in str(ctx.content)[:6]:
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
            config = config['wishwall_config']
        except KeyError:
            sent = await channel.send(embed=(await self.build_embed(self, error=True, error_type=1)))
            await asyncio.sleep(5)
            await sent.delete()
            return
        if channel.id == config['wishwall_channel'] and message.author == self.bot.user and not member == self.bot.user and message.embeds[0]:
            wish_owner = message.embeds[0].footer.text
            react_user = member.name
            if member.nick:
                react_user = member.nick
            if react_user not in wish_owner:
                if str(payload.emoji) == config['conf_react']:
                    await message.edit(embed=(await self.build_embed(self, old_embed=message.embeds[0], add=member)))
                elif str(payload.emoji) == config['decl_react']:
                    await message.edit(embed=(await self.build_embed(self, old_embed=message.embeds[0], remove=member)))
            elif react_user in message.embeds[0].footer.text:
                if str(payload.emoji) == config['decl_react']:
                    await discord.Message.delete(message)
                    return
            await self.build_embed_reacts(message, config)


def setup(bot):
    bot.add_cog(WishWall(bot))
