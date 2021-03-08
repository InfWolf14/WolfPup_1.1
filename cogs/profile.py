import io
import asyncio
import discord
from discord import File
from discord.ext import commands
from util import Util
from mongo import Mongo
from PIL import Image, ImageDraw, ImageFont


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Mongo.init_db(Mongo(self.bot))
        self.server_db = None
        self.sys_aliases = {'PS': {'PS', 'PSN', 'PS4', 'PS5', 'PLAYSTATION'},
                            'XB': {'XB', 'XB1', 'XBOX', 'MICROSOFT'},
                            'STEAM': {'STEAM', 'VALVE'},
                            'UPLAY': {'UPLAY', 'UBI', 'UBISOFT'},
                            'FFXIV': {'FFXIV', 'XIV', 'FF'}}

    @commands.command(name='build_profile', hidden=True, aliases=['rebuild_profile'])
    @commands.has_guild_permissions(administrator=True)
    async def build_profile(self, ctx, member: discord.Member = None):
        self.server_db = self.db['server'][str(ctx.guild.id)]
        if not Util.check_channel(ctx, True):
            return
        new_profile = {'profile': {'aliases': {
                       'ps': None, 'xb': None, 'uplay': None, 'steam': None, 'ffxiv': None},
                       'wanted_text': None}}
        if member:
            self.server_db.find_one_and_update({'_id': str(member.id)}, {'$set': new_profile}, upsert=True)
            return
        for member in ctx.guild.members:
            if not member.bot:
                self.server_db.find_one_and_update({'_id': str(member.id)}, {'$set': new_profile}, upsert=True)

    @commands.command(name='set', aliases=['add'])
    async def set(self, ctx, system: str, *name: str):
        """Add your usernames for your game system"""
        username = ' '.join(name)
        self.server_db = self.db['server'][str(ctx.guild.id)]
        if not Util.check_channel(ctx, True):
            return
        for platform in self.sys_aliases:
            if system.upper() in self.sys_aliases[platform]:
                self.server_db.find_one_and_update({'_id': str(ctx.author.id)},
                                                   {'$set': {f'profile.aliases.{platform.lower()}': username}})
                await ctx.send(embed=discord.Embed(title='Successfully changed Profile',
                                                   description=f'{platform} -> {username}'))
                return
        error = await ctx.send(embed=discord.Embed(title='Error: invalid platform'))
        await asyncio.sleep(5)
        await error.delete()

    @commands.command(name='get')
    async def get(self, ctx, system: str, member: discord.Member = None):
        """Get a users usernames."""
        self.server_db = self.db['server'][str(ctx.guild.id)]
        if not Util.check_channel(ctx):
            return
        if member is None:
            member = ctx.author
        for platform in self.sys_aliases:
            if system.upper() in self.sys_aliases[platform]:
                user = self.server_db.find({'_id': str(member.id)})
                for _, user_data in enumerate(user):
                    username = user_data['profile']['aliases'][platform.lower()]
                    if username is None:
                        username = 'N/A'
                    await ctx.send(embed=discord.Embed(title=f'{platform} : {username}'))
                    return
        error = await ctx.send(embed=discord.Embed(title='Error: invalid platform'))
        await asyncio.sleep(5)
        await error.delete()

    @commands.command(name='search')
    async def search(self, ctx, query, exact_match: bool = False):
        """Search for a user"""
        self.server_db = self.db['server'][str(ctx.guild.id)]
        results = []
        if not Util.check_channel(ctx):
            return
        user = self.server_db.find()
        for _, user_data in enumerate(user):
            for platform in self.sys_aliases:
                username = user_data['profile']['aliases'][platform.lower()]
                if username is not None:
                    if not exact_match:
                        query = query.lower()
                        username = username.lower()
                    if query in username and user_data['_id'] not in results:
                        member = await ctx.guild.fetch_member(int(user_data['_id']))
                        results.append(member.mention)
        if len(results) > 0:
            await ctx.send(embed=discord.Embed(title=f'Found {len(results)} match(es):',
                                               description='\n'.join(results)))
        else:
            await ctx.send(embed=discord.Embed(title=f'No Matches Found'))

    @commands.command(name='delete', aliases=['del'])
    async def delete(self, ctx, system):
        """Delete a username"""
        self.server_db = self.db['server'][str(ctx.guild.id)]
        if not Util.check_channel(ctx, True):
            return
        for platform in self.sys_aliases:
            if system.upper() in self.sys_aliases[platform]:
                self.server_db.find_one_and_update({'_id': str(ctx.author.id)},
                                                   {'$set': {f'profile.aliases.{platform.lower()}': None}})
                await ctx.send(embed=discord.Embed(title='Successfully changed Profile',
                                                   description=f'{platform} -> None'))
                return
            else:
                error = await ctx.send(embed=discord.Embed(title='Error: invalid platform'))
                await asyncio.sleep(5)
                await error.delete()

    @commands.command(aliases=['card', 'profilecard', 'canvas'])
    async def profile(self, ctx, member: discord.Member = None):
        """Displays your profile card."""
        self.server_db = self.db['server'][str(ctx.guild.id)]
        if not Util.check_channel(ctx):
            return

    @commands.command()
    async def wanted(self, ctx, *text):
        """Sets the custom wanted text on your profile card. """
        self.server_db = self.db['server'][str(ctx.guild.id)]
        wanted = ' '.join(text)
        if not Util.check_channel(ctx, True):
            return
        if len(wanted) != 0:
            self.server_db.find_one_and_update({'_id': str(ctx.author.id)}, {'$set': {f'profile.wanted_text': wanted}})
            await ctx.send(embed=discord.Embed(title='Successfully changed Wanted Text:',
                                               description=f'*{wanted}*'))
        else:
            self.server_db.find_one_and_update({'_id': str(ctx.author.id)}, {'$set': {f'profile.wanted_text': None}})
            await ctx.send(embed=discord.Embed(title='Successfully set Wanted Text to Default'))


def setup(bot):
    bot.add_cog(Profile(bot))
