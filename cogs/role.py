import json
import discord
from discord.ext import commands


class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        with open(f'config/{before.guild.id}/config.json', 'r') as f:
            config = json.load(f)
        channel = self.bot.get_channel(config['channel_config']['rolepost_channel'])
        if before.roles == after.roles:
            return
        embed = discord.Embed(title=f'{before.name}#{before.discriminator}')
        embed.add_field(name='User:', value=after.mention)
        if set(before.roles) != set(after.roles):
            if len(before.roles) > len(after.roles):
                for role in before.roles:
                    if role not in after.roles:
                        embed.add_field(name='Role change:', value=f'{role.name} removed')
            elif len(before.roles) < len(after.roles):
                for role in after.roles:
                    if role not in before.roles:
                        embed.add_field(name='Role change:', value=f'{role.name} added')
        embed.set_footer(text=f'User ID:{after.id}', icon_url=after.avatar_url)
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Role(bot))
