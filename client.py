''' Melon.py is a lightweight Discord bot framework. Features include a MySQL database API, 
maintenance modes, schedules and front end tools such as pagination and templating.
'''

import discord
from discord.ext import commands
import configparser
import asyncio
import json

class MelonClient():
    def __init__(self):
        with open('melon.json') as settings:
            self.settings = json.load(settings)
        with open('app.json') as app:
            self.app = json.load(app)
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
        self.db = []


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
            if self.maintenance_mode:
                print('mente')
                if ctx.valid:
                    await message.channel.send(self.settings['maintenance_message'])
                    return
            await self.bot.process_commands(message)

    '''Run loop, with bot tasks and other concurrent support tasks
    '''
    def run(self):
        self.bot.run(self.env['App']['DISCORD_TOKEN'])
        # self.loop.create_task(self.start())
        # # Add async tasks to run concurrently with bot

        # try:
        #     self.loop.run_until_complete(self.start(*args, **kwargs))
        # except KeyboardInterrupt:
        #     self.loop.run_until_complete(self.bot.logout())
        #     # cancel all tasks lingering
        # finally:
        #     self.loop.close()


    async def start(self):
        print('Running bot. Connecting to Discord...')
        return await self.bot.start(self.env['App']['DISCORD_TOKEN'], bot=True)

    def register_controllers(self, controllers):
        for controller in controllers:
            self.bot.add_cog(controller(self))

if __name__ == '__main__':
    m = Melon()
    m.run()
