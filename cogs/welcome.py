import json
import random
import discord
from discord.ext import commands
import datetime


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open(f'config/{member.guild.id}/config.json', 'r') as f:
            config = json.load(f)
        config_channel = self.bot.get_channel(config['channel_config']['welcome_channel'])

        welcome_embed = discord.Embed(title="Member joined", description=f'{member} has joined.')
        welcome_embed.add_field(name="ID:", value=f"{member.id}", inline=True)
        created = datetime.datetime.utcnow() - member.created_at
        days = created.days
        years = 0
        if days > 365:
            years = int(days / 365)
            days = int(days - (years * 365))
        if days < 5:
            welcome_embed.add_field(name="**New Account!**", value=" ")
        seconds = created.seconds
        hours = int(seconds / 3600)
        minutes = int((seconds - (hours * 3600)) / 60)
        seconds = int(seconds - ((hours * 3600) + (minutes * 60)))
        welcome_embed.add_field(name="Created ", value=f"{years} years, {days} days, {hours} hours, {minutes} minutes, {seconds} seconds ago", inline=True)
        welcome_embed.set_thumbnail(url=member.avatar_url)
        welcome_embed.timestamp = datetime.datetime.utcnow()
        i = 0
        for member in member.guild.members:
            if member.bot:
                i += 1
        total = member.guild.member_count
        welcome_embed.add_field(name="Join number: ", value=f"{total - i}", inline=True)
        await config_channel.send(embed=welcome_embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        with open(f'config/{before.guild.id}/config.json', 'r') as f:
            config = json.load(f)
        role = before.guild.get_role(config['role_config']['posse'])
        welcome_channel = self.bot.get_channel(config['channel_config']['lounge'])

        if role not in before.roles and role in after.roles:
            ment = after.mention
            welcome_messages = [
                f"\U0001f4e2 \U0000269f Say hello to {ment}!",
                f"\U0001f4e2 \U0000269f Hello there! ~~General Kenobi~~ {ment}!!",
                f"\U0001f4e2 \U0000269f A wild {ment} appeared.",
                f"\U0001f4e2 \U0000269f Everyone welcome, {ment}",
                f"\U0001f4e2 \U0000269f Welcome, {ment}! We hope you brought pizza.",
                f"\U0001f4e2 \U0000269f Brace yourselves. {ment} is here!",
                f"\U0001f4e2 \U0000269f {ment} is here, as the prophecy foretold.",
                f"\U0001f4e2 \U0000269f Hey! Listen! {ment} has joined!",
                f"\U0001f4e2 \U0000269f {ment} is near.",
                f"\U0001f4e2 \U0000269f {ment} joined your party.",
                f"\U0001f4e2 \U0000269f {ment} is breaching the wall on the north side. Give them all you got!",
                f"\U0001f4e2 \U0000269f Welcome ~~Tenno~~ {ment}!",
                f"\U0001f4e2 \U0000269f {ment} just arrived. Seems OP - please nerf.",
                f"\U0001f4e2 \U0000269f {ment} joined. You must construct additional pylons.",
                f"\U0001f4e2 \U0000269f ~~**Tactical nuke**~~ {ment}, incoming!🚨"
            ]
            await welcome_channel.send(random.choice(welcome_messages))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        with open(f'config/{member.guild.id}/config.json', 'r') as f:
            config = json.load(f)
        config_channel = self.bot.get_channel(config['channel_config']['welcome_channel'])
        leave_embed = discord.Embed(title="Member left", description=f'{member} has left')
        leave_embed.add_field(name="Nick: ", value=f"{member.nick}", inline=True)
        leave_embed.add_field(name="ID:", value=f"{member.id}", inline=True)
        joined = datetime.datetime.utcnow() - member.joined_at
        days = joined.days
        years = 0
        if days > 365:
            years = int(days / 365)
            days = int(days - (years * 365))
        seconds = joined.seconds
        hours = int(seconds / 3600)
        minutes = int((seconds - (hours * 3600)) / 60)
        seconds = int(seconds - ((hours * 3600) + (minutes * 60)))
        leave_embed.add_field(name="Joined", value=f"{years} years, {days} days, {hours} hours, {minutes} minutes, {seconds} seconds ago")
        mentions = [role.mention for role in member.roles if role.name != '@everyone']
        if not mentions:
            mentions = 'N/A'
        leave_embed.add_field(name="Roles:", value=" ".join(mentions))
        leave_embed.set_thumbnail(url=member.avatar_url)
        leave_embed.timestamp = datetime.datetime.utcnow()
        await config_channel.send(embed=leave_embed)


def setup(bot):
    bot.add_cog(Welcome(bot))
