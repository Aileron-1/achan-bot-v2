from discord.ext import commands

class Shadowban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def shadowban(self, ctx, user):
        """Sends a user to an alternate dimension where only shitposters can chat.
        """
        ch = ctx.message.channel
        await ch.send('Ban')

