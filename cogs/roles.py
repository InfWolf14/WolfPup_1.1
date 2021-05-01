import json
from lib.mongo import Mongo
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.ext.commands.errors import EmojiNotFound


class RolesCog(commands.Cog, name='roles'):
    """Role Reaction System"""

    def __init__(self, bot):
        self.bot = bot
        self.db = Mongo.init_db(Mongo())
        self.server_db = None

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        server = self.bot.get_guild(payload.guild_id)
        user = server.get_member(payload.user_id)

        if user.bot:
            return
        self.server_db = self.db[str(payload.guild_id)]['roles']
        if not payload.emoji.is_custom_emoji():
            return
        role_dict = self.server_db.find_one({'emoji': str(payload.emoji.id)})
        if not role_dict:
            return
        role_id = int(role_dict["_id"])
        emoji_id = int(role_dict['emoji'])
        message_id = int(role_dict['message'])
        if payload.message_id != message_id:
            return
        role = server.get_role(role_id)
        if user not in role.members:
            return
        await user.remove_roles(role)
        channel = await user.create_dm()
        await channel.send(f'{role.name} was successfully removed')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        self.server_db = self.db[str(payload.guild_id)]['roles']
        if not payload.emoji.is_custom_emoji():
            return
        role_dict = self.server_db.find_one({'emoji': str(payload.emoji.id)})
        if not role_dict:
            return
        role_id = int(role_dict["_id"])
        emoji_id = int(role_dict['emoji'])
        message_id = int(role_dict['message'])
        user = payload.member
        if payload.message_id != message_id:
            return
        role = user.guild.get_role(role_id)
        if user in role.members:
            return
        await user.add_roles(role)
        channel = await user.create_dm()
        await channel.send(f'{role.name} was successfully added')



    @commands.command(hidden=True)
    @has_permissions(administrator=True)
    async def set_role(self, ctx, role: discord.Role, message: int, emoji: discord.Emoji):
        try:
            print(emoji)
            with open(f'assets/json/config.json', 'r') as f:
                config = json.load(f)
            self.server_db = self.db[str(ctx.guild.id)]['roles']
            self.server_db.find_one_and_replace({'_id': str(role.id)}, {'emoji': str(emoji.id), 'message': str(message)})
            channel = self.bot.get_channel(int(config[str(ctx.guild.id)]['getroles']))
            msg = await channel.fetch_message(message)
            await msg.add_reaction(emoji)
            await ctx.send(emoji)
        except EmojiNotFound:
            await ctx.send("Error with the Emoji.", delete_after=6)
        except:
            await ctx.send("Something went wrong.", delete_after=6)

    @commands.command(hidden=True)
    @has_permissions(administrator=True)
    async def build_roles(self, ctx):
        self.server_db = self.db[str(ctx.guild.id)]['roles']

        for role in ctx.guild.roles:
            self.server_db.insert_one({'_id': str(role.id)},
                                      {'$set': dict})

        await ctx.send('Done')


def setup(bot):
    bot.add_cog(RolesCog(bot))
