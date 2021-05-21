import datetime
import pytz
import discord
from dateutil import tz
from discord.ext import commands


class Time(commands.Cog, name="Time Conversion"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def time(self, ctx):
        """Shows the time in a range of timezones."""
        async with ctx.typing():
            timezones_to_convert_dict = {
                'PT/California': 'America/Los_Angeles',
                'MT/Alberta': 'America/Edmonton',
                'SK': 'Canada/Saskatchewan',
                'CT/Winnipeg': 'America/Winnipeg',
                'ET/New York': 'America/New_York',
                'UK/London': 'Europe/London',
                'CET/Copenhagen': 'Europe/Copenhagen',
                'AEST/Sydney': 'Australia/Sydney',
            }

            tz_field = []
            time_field = []
            for display, zone in timezones_to_convert_dict.items():
                tz_field.append("**{}**".format(display))
                time_field.append(datetime.datetime.now(pytz.timezone(zone)).strftime('%H:%M'))

            embed = discord.Embed(title="Time Conversions", description='Current Times', color=0x00ff00)
            embed.add_field(name="Time Zones", value='\n'.join(tz_field), inline=True)
            embed.add_field(name="Time", value='\n'.join(time_field), inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def convert(self, ctx, time_zone_input: str, *time_input: str):
        """Shows a range of timezones in the future. Format: TZ h:m day/month/year. Example SK 12:30 4/8/2020"""
        async with ctx.typing():

            try:
                time_join = " ".join(time_input)
                time_join.strip(' ')
                time_to_convert = datetime.datetime.strptime(str(time_join), '%H:%M %d/%m/%Y')

                tz_dict = {
                    'PT': 'America/Los_Angeles',
                    'MT': 'America/Edmonton',
                    'SK': 'Canada/Saskatchewan',
                    'CT': 'America/Winnipeg',
                    'ET': 'America/New_York',
                    'UK': 'Europe/London',
                    'CET': 'Europe/Paris',
                    'AU': 'Australia/Sydney'
                }
                timezones_to_use = {
                    'PT/California': 'America/Los_Angeles',
                    'MT/Alberta': 'America/Edmonton',
                    'SK/Saskatchewan': 'Canada/Saskatchewan',
                    'CT/Winnipeg': 'America/Winnipeg',
                    'ET/New York': 'America/New_York',
                    'UK/London': 'Europe/London',
                    'CET/Copenhagen': 'Europe/Copenhagen',
                    'AEST/Sydney': 'Australia/Sydney',
                }

                from_zone = tz.gettz(tz_dict.get(time_zone_input))
                tz_field = []
                time_field = []
                for display, zone in timezones_to_use.items():
                    tz_field.append("**{}**".format(display))
                    mt = time_to_convert.replace(tzinfo=from_zone)
                    to_zone = tz.gettz(zone)
                    converted = mt.astimezone(to_zone)
                    time_field.append(converted.strftime('%H:%M %d/%m/%y'))

                embed = discord.Embed(title="Time Conversions", description='In the Future', color=0x00ff00)
                embed.add_field(name="Time Zones", value='\n'.join(tz_field), inline=True)
                embed.add_field(name="Time", value='\n'.join(time_field), inline=True)
                await ctx.send(embed=embed)
            except ValueError:
                await ctx.send('Check formatting for your command. Must be in HH:MM D/M/YYYY using the 24 hour clock. '
                               'Ex. 14:00 8/12/2020 ')

    @commands.command(pass_context=True)
    async def timezones(self, ctx):
        """Shows the timezones able to be used in the convert command."""
        tz_dict = {
            'PT': 'Pacific Time',
            'MT': 'Mountain Time',
            'SK': 'Saskatchewan Time',
            'CT': 'Central Time',
            'ET': 'Eastern Time',
            'UK': 'United Kingdom',
            'CET': 'Central European Time',
            'AU': 'Australian (Sydney)'
        }
        embed = discord.Embed(title='Time Zones', description='Usable Timezones', color=0x00ff00)
        embed.add_field(name='Time Zones', value='\n'.join(tz_dict), inline=True)
        embed.add_field(name='Names', value='\n'.join(tz_dict.values()))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Time(bot))
