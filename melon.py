''' Melon.py is a lightweight Discord bot framework. Features include a MySQL database API, 
maintenance modes, schedules and front end tools such as pagination and templating.
'''

import discord
from discord.ext import commands
import configparser
import asyncio
import json

class Melon():
    def __init__(self):
        with open('melon.json') as settings:
            self.settings = json.load(settings)
        self.env = configparser.ConfigParser()
        self.env.read('.env')
        self.description = self.settings['description']
        self.activity = discord.Game(name="Idol politics", type=1)
        self.maintenance_mode = self.env.getboolean('App','MAINTENANCE_MODE')
        self.loop = asyncio.get_event_loop()
        self.bot = commands.Bot(
            command_prefix=self.settings['prefixes'], 
            description=self.settings['description'],
            help_command=None, 
            case_insensitive=True 
            )
        @self.bot.event
        async def on_ready():
            print('Logged in to user: %s' % self.bot.user.name)
            print('All ready. Let\'s go!')
            if self.activity:
                await self.bot.change_presence(status=discord.Status.online, activity=self.activity)

        @self.bot.event
        async def on_message(message):
            # Ignore commands in PMs
            if message.guild is None:
                return
            ctx = await self.bot.get_context(message)
            # Don't process commands in blocked channels
            if message.channel.id in self.settings['blocked_channels']:
                return
            # Display maintenance message and stop commands
            if self.env['App']['MAINTENANCE_MODE']:
                if ctx.valid:
                    await message.channel.send(self.settings['maintenance_message'])
                    return
            await self.bot.process_commands(message)

    def start(self):
        print('Running bot. Connecting to Discord...')
        # Add async tasks to run concurrently with bot
        # self.bot.loop.create_task(self.shutdown())
        # Run the bot loop
        self.bot.run(self.env['App']['DISCORD_TOKEN'])

    async def shutdown(self):
        print('I will kill')
        await asyncio.sleep(7)
        print('logging out')
        await self.bot.login(self.env['App']['DISCORD_TOKEN'], bot=True)

if __name__ == '__main__':
    m = Melon()
    m.start()
    
