import os
import json
import discord
from discord.ext import commands


class Starboard(commands.Cog, name='Starboard'):
    def __init__(self, bot):
        self.bot = bot
        self.star_url = 'https://cdn.discordapp.com/attachments/767568459939708950/777605519623585822/11_Discord_icon_4_20.png'
        self.pinned_url = 'https://cdn.discordapp.com/attachments/767568459939708950/777605535801016350/11_Discord_icon_4_80.png'
        self.error_url = 'https://cdn.discordapp.com/attachments/767568459939708950/777606962480807956/11_Discord_icon_2_80.png'
        self.success_url = 'https://cdn.discordapp.com/attachments/767568459939708950/767568508414066739/Status_Indicators12.png'

    @commands.command(name='init_starboard', hidden=True, aliases=['init_sb', 'sb_init'])
    @commands.is_owner()
    async def init_starboard(self, ctx):
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
            starboard_config = {
                'starboard_channel': None,
                'star_react': None,
                'starred_react': None,
                'threshold': 3
            }
            config['starboard_config'] = starboard_config
            with open(f'config/{ctx.guild.id}/config.json', 'w') as f:
                json.dump(config, f, indent=2)
            await ctx.send(embed=discord.Embed(title=f'Starboard config initialized'))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, ctx):
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
        channel = self.bot.get_channel(ctx.channel_id)
        starboard_channel = self.bot.get_channel(config['starboard_config']['starboard_channel'])
        message = await channel.fetch_message(ctx.message_id)
        reaction = discord.utils.get(message.reactions, emoji=ctx.emoji.name)
        already_posted = discord.utils.get(message.reactions, emoji=config['starboard']['conf_react'])
        if ctx.emoji.name == config['starboard_config']['star_react']:
            if reaction.count >= config['starboard_config']['threshold'] and not already_posted:
                copy_embed = ""
                if message.embeds:
                    copy_embed = message.embeds[0].to_dict()
                    if message.content:
                        content = message.content.__add__(f'\n\n**Link Preview:**\n{copy_embed["description"]}')
                    else:
                        content = copy_embed.description
                    if "fields" in copy_embed:
                        for embeds in message.embeds:
                            for field in embeds.fields:
                                content = content.__add__(f'\n\n**{field.name}**')
                                content = content.__add__(f'\n{field.value}')
                else:
                    content = message.content
                embed = discord.Embed(title=f"{message.author} said...",
                                      description=f'{content}\n\n[Jump to Message](https://discordapp.com/channels/{ctx.guild_id}/{ctx.channel_id}/{ctx.message_id})',
                                      colour=0x784fd7,
                                      timestamp=message.created_at)
                embed.set_thumbnail(url=message.author.avatar_url)
                if message.embeds:
                    if copy_embed.image:
                        embed.set_image(url=copy_embed.image.url)
                    elif copy_embed.video:
                        embed.set_image(url=copy_embed.thumbnail.url)
                elif message.attachments:
                    embed.set_image(url=message.attachments[0].url)
                embed.set_footer(icon_url=self.star_url, text='Original Posted')
                await starboard_channel.send(
                    content=f"> **Posted in** {channel.mention} by {message.author.mention}", embed=embed)
                await message.add_reaction(config['starboard_config']['starred_react'])


def setup(bot):
    bot.add_cog(Starboard(bot))
