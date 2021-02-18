'''
    Melon.py is a Discord bot framework. Features include a MySQL database API and front end tools such as pagination and templating.
'''
import discord
from discord.ext import commands
import settings

class Melon:
    def __init__(self):
        self.settings = settings.settings()
        self.description = self.settings['description']
        self.bot = None
        self.activity = discord.Game(name="Idol politics", type=1)
        self.maintenance_mode = True
        self.env = {}

    def run(self):
        print('Running bot. Connecting to Discord...')
        self.bot = commands.Bot(
            command_prefix=self.settings.bot['prefixes'], 
            description=self.settings.bot['description'],
            help_command=None, 
            case_insensitive=True 
        )
        print('Logged in to user: %s' % self.bot.user.name)
        if self.activity:
            await self.bot.change_presence(status=discord.Status.online, activity=self.activity)


