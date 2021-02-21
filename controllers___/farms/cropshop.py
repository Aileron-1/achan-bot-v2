from discord.ext import commands
from discord import Embed
from ..misc import emote
from ..misc import currency_names
import asyncio
import datetime

class CropShop(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db