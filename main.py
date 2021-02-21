from client import MelonClient
import discord
from discord.ext import commands
from controllers.TestController import TestController

db_connection = ''

controllers = [
    TestController,
]

m = MelonClient()
m.register_controllers(controllers)
m.run()
