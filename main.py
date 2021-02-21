from client import MelonClient
import discord
from discord.ext import commands
from controllers.InfoController import InfoController

db_connection = ''

controllers = [
    InfoController,
]

m = MelonClient()
m.register_controllers(controllers)
m.run()
