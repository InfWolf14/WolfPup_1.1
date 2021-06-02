from discord.ext import commands
from lib.mongo import Mongo
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive



class Google(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()  # client_secrets.json need to be in the same directory as the script
        self.drive = GoogleDrive(gauth)

    @commands.command(hidden=True)
    @commands.has_permissions(manage_messages=True)
    async def pictures(self, ctx):
        fileList = self.drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        for file in fileList:
            print('Title: %s, ID: %s' % (file['title'], file['id']))





def setup(bot):
    bot.add_cog(Google(bot))
