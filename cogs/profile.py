import io
import asyncio
import discord
from discord import File
from discord.ext import commands
from lib.util import Util
from lib.mongo import Mongo
from PIL import Image, ImageDraw, ImageFont


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Mongo.init_db(Mongo())
        self.server_db = None
        self.sys_aliases = {'PS': {'PS', 'PSN', 'PS4', 'PS5', 'PLAYSTATION'},
                            'XB': {'XB', 'XB1', 'XBOX', 'MICROSOFT'},
                            'STEAM': {'STEAM', 'VALVE'},
                            'UPLAY': {'UPLAY', 'UBI', 'UBISOFT'},
                            'FFXIV': {'FFXIV', 'XIV', 'FF'}}

    @commands.command(name='build_profile', hidden=True, aliases=['rebuild_profile'])
    @commands.has_guild_permissions(administrator=True)
    async def build_profile(self, ctx, member: discord.Member = None, pending=None):
        self.server_db = self.db['server'][str(ctx.guild.id)]
        if pending:
            await pending.edit(embed=discord.Embed(title='Rebuilding Profile stats...'))
        else:
            pending = await ctx.send(embed=discord.Embed(title='Rebuilding Profile stats...'))
        if await Util.check_channel(ctx, True):
            new_profile = {'profile': {'aliases': {
                           'ps': None, 'xb': None, 'uplay': None, 'steam': None, 'ffxiv': None},
                           'wanted_text': None}}
            if member:
                self.server_db.find_one_and_update({'_id': str(member.id)}, {'$set': new_profile}, upsert=True)
                return
            for member in ctx.guild.members:
                if not member.bot:
                    self.server_db.find_one_and_update({'_id': str(member.id)}, {'$set': new_profile}, upsert=True)
            await pending.edit(embed=discord.Embed(title='Done'))
            return pending

    @commands.command(name='set', aliases=['add'])
    async def set(self, ctx, system: str, *name: str):
        """Add your usernames for your game system"""
        username = ' '.join(name)
        self.server_db = self.db['server'][str(ctx.guild.id)]
        if await Util.check_channel(ctx, True):
            for platform in self.sys_aliases:
                if system.upper() in self.sys_aliases[platform]:
                    self.server_db.find_one_and_update({'_id': str(ctx.author.id)},
                                                       {'$set': {f'profile.aliases.{platform.lower()}': username}})
                    await ctx.send(embed=discord.Embed(title='Successfully Updated Profile',
                                                       description=f'**[{platform}] \u27A4** *{username}*',
                                                       color=discord.Colour.gold()))
                    return
            error = await ctx.send(embed=discord.Embed(title='Error: invalid platform'))
            await asyncio.sleep(5)
            await error.delete()

    @commands.command(name='get')
    async def get(self, ctx, system: str, member: discord.Member = None):
        """Get a users usernames."""
        self.server_db = self.db['server'][str(ctx.guild.id)]
        if await Util.check_channel(ctx):
            if member is None:
                member = ctx.author
            for platform in self.sys_aliases:
                if system.upper() in self.sys_aliases[platform]:
                    user = self.server_db.find({'_id': str(member.id)})
                    for _, user_data in enumerate(user):
                        username = user_data['profile']['aliases'][platform.lower()]
                        if username is None:
                            username = 'N/A'
                        await ctx.send(embed=discord.Embed(title=f'*{username}*',
                                                           color=discord.Colour.gold()))
                        return
            error = await ctx.send(embed=discord.Embed(title='Error: invalid platform'))
            await asyncio.sleep(5)
            await error.delete()

    @commands.command(name='search')
    async def search(self, ctx, query, exact_match: bool = False):
        """Search for a user"""
        self.server_db = self.db['server'][str(ctx.guild.id)]
        results = []
        count = 0
        if await Util.check_channel(ctx):
            user = self.server_db.find()
            for _, user_data in enumerate(user):
                for platform in self.sys_aliases:
                    username = user_data['profile']['aliases'][platform.lower()]
                    if username is not None:
                        if not exact_match:
                            query = query.lower()
                            username = username.lower()
                        if query in username and user_data['_id'] not in results:
                            count += 1
                            member = await ctx.guild.fetch_member(int(user_data['_id']))
                            results.append(f'`[{str(count)}.]` {member.mention}')
            if len(results) > 0:
                await ctx.send(embed=discord.Embed(title=f'Found {len(results)} match(es):',
                                                   description='\n'.join(results),
                                                   color=discord.Colour.gold()))
            else:
                await ctx.send(embed=discord.Embed(title=f'No Matches Found'))

    @commands.command(name='delete', aliases=['del'])
    async def delete(self, ctx, system):
        """Delete a username"""
        self.server_db = self.db['server'][str(ctx.guild.id)]
        if await Util.check_channel(ctx, True):
            for platform in self.sys_aliases:
                if system.upper() in self.sys_aliases[platform]:
                    self.server_db.find_one_and_update({'_id': str(ctx.author.id)},
                                                       {'$set': {f'profile.aliases.{platform.lower()}': None}})
                    await ctx.send(embed=discord.Embed(title='Successfully Updated Profile',
                                                       description=f'**[{platform}] \u27A4** *N/A*',
                                                       color=discord.Colour.gold()))
                    return
                error = await ctx.send(embed=discord.Embed(title='Error: invalid platform'))
                await asyncio.sleep(5)
                await error.delete()

    @commands.command(aliases=['card', 'profilecard', 'canvas'])
    async def profile(self, ctx, member: discord.Member = None):
        """Displays your profile card."""
        self.server_db = self.db['server'][str(ctx.guild.id)]
        if await Util.check_channel(ctx):
            sys_alias = {'PS': "assets/icon/ps_logo.png",
                         'XB': "assets/icon/xb_logo.png",
                         'STEAM': "assets/icon/steam_logo.png",
                         'UPLAY': "assets/icon/ubi_logo.png",
                         'FFXIV': "assets/icon/xiv_logo.png"}
            if member is None:
                member = ctx.author
            async with ctx.message.channel.typing():
                user = self.server_db.find_one({'_id': str(member.id)})
                bg_img = Image.open('assets/card_to_draw.png').convert('RGBA')
                ref_img = bg_img.copy()
                draw = ImageDraw.Draw(ref_img)
                title_font = ImageFont.truetype('assets/font/NASHVILL.ttf', 42)
                buffer = 20
                draw_bounds = [buffer, (ref_img.width-buffer), buffer, (ref_img.height-buffer)]
                # # Initialize Coords # #
                ref_coord = [draw_bounds[0], draw_bounds[2]]
                # # Title Draw # #
                text_size = draw.textsize(text='WANTED', font=title_font)
                draw.text((int((ref_img.width/2)-(text_size[0]/2)), ref_coord[1]),
                          text='WANTED', fill=(16, 16, 16), font=title_font)
                draw.line((ref_coord[0], ref_coord[1]+(text_size[1]/2),
                           (ref_img.width/2)-(text_size[0]/2+buffer), ref_coord[1]+(text_size[1]/2)),
                          fill=(16, 16, 16), width=5)
                draw.line(((ref_img.width/2)+(text_size[0]/2+buffer), ref_coord[1]+(text_size[1]/2),
                           draw_bounds[1], ref_coord[1]+(text_size[1]/2)),
                          fill=(16, 16, 16), width=5)
                draw.line((draw_bounds[0]+(buffer*2), ref_coord[1]+(text_size[1]+(buffer/2)),
                           draw_bounds[1]-(buffer*2), ref_coord[1]+(text_size[1]+(buffer/2))),
                          fill=(16, 16, 16), width=5)
                # # Advance Coords # #
                ref_coord[0] += int(buffer/2)
                ref_coord[1] += int(text_size[1]+(buffer*1.5))
                # # Avatar Draw # #
                avatar_img = Image.open('assets/gigi_avatar.png')
                if member.avatar:
                    avatar_asset = member.avatar_url_as(format='png', size=128)
                    buffer_img = io.BytesIO()
                    await avatar_asset.save(buffer_img)
                    buffer_img.seek(0)
                    avatar_img = Image.open(buffer_img).resize((128, 128)).convert('RGBA')
                emblem_img = Image.open(f'assets/emblem_{user["level"]}.png').convert('RGBA')
                draw.rectangle((ref_coord[0]-5, ref_coord[1]-5,
                                ref_coord[0]+avatar_img.width+5, ref_coord[1]+avatar_img.height+5),
                               fill=(16, 16, 16), width=5)
                ref_img.paste(avatar_img, (ref_coord[0], ref_coord[1]), avatar_img)
                ref_img.paste(emblem_img, (int(ref_coord[0]+(avatar_img.width/2)-(emblem_img.width/2)),
                                           int(ref_coord[1]+avatar_img.height+1)), emblem_img)
                # # Advance Coords # #
                ref_coord[0] += avatar_img.width+(buffer/2)
                ref_coord[1] += (buffer/2)
                # # Draw Level|EXP # #

                # Send finished image
                send_buffer = io.BytesIO()
                ref_img.save(send_buffer, format='PNG')
                send_buffer.seek(0)
                await ctx.send(file=File(send_buffer, 'myimage.png'))

    @commands.command(name='wanted')
    async def wanted(self, ctx, *text):
        """Sets the custom wanted text on your profile card. """
        self.server_db = self.db['server'][str(ctx.guild.id)]
        wanted = ' '.join(text)
        if await Util.check_channel(ctx, True):
            if len(wanted) != 0:
                self.server_db.find_one_and_update({'_id': str(ctx.author.id)}, {'$set': {f'profile.wanted_text': wanted}})
                await ctx.send(embed=discord.Embed(title='Successfully Updated Wanted Text:',
                                                   description=f'*{wanted}*'))
            else:
                self.server_db.find_one_and_update({'_id': str(ctx.author.id)}, {'$set': {f'profile.wanted_text': None}})
                await ctx.send(embed=discord.Embed(title='Successfully set Wanted Text to Default'))


def setup(bot):
    bot.add_cog(Profile(bot))
