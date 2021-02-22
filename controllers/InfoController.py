import discord
from discord.ext import commands
from discord import Embed

class InfoController(commands.Cog):
    def __init__(self, melon):
        self.melon = melon
        self.bot = melon.bot
        self.db = melon.db

    @commands.command()
    async def help(self, ctx):
        ch = ctx.message.channel
        emb = Embed(title='Help', description='''''', colour=discord.Colour(1).blue())
        emb.set_footer(text='A-chan help.')
        emb.add_field(name='Economy', value='''
`daily` - Get credits and AsaCoco. 20hr cooldown.
`profile (opt: user)` - Shows currency and stats of user.
`top` - Shows the top 10 users in many categories.
`superchat <user> <amount> (opt: description)` - Sends a superchat to a user.
`blackmarket`/`bm` - Do shady deals with your dealer.
`farm` - Purchase a farm to earn money. Use `a.farm help` for more farm info. 
    ''', inline=False)
        emb.add_field(name='Currency', value='''
`credits`/`c` - Use `a.credits` for credit-specific commands.
`asacoco`/`a` - Use `a.asacoco` for asacoco-specific commands.
`yubi`/`y` - Use `a.yubi` for yubi-specific commands.
    ''', inline=False)
        emb.add_field(name='Fun', value='''
`roll`/`r (opt: all)` - Roll for HoloCredits and a chance to win random prizes. Limit 7 per hour.
`percent` - Sends a random number from 0-100.
`janken` - Play janken with Watame!
`lastbossjanken` - Bet all your AsaCoco vs Watame.
`inhale`, `inject`, `insert`, `drink` ...and many more!
    ''', inline=False)
        emb.add_field(name='Others', value='''
`changelog` - See recent bot changes.
`bug <text here>` - Report an A-chan or YAGOO bug, no matter how small. Suggestions also welcome.
    ''', inline=False)
        await ch.send(embed=emb)


        # save it
        ttb = self.db.get_table('testable')
        ttb.insert({
            'user': ctx.message.author.id,
            'words': ctx.message.content
        })


    @commands.command()
    async def abc(self, ctx):
        ch = ctx.message.channel
        ttb = self.db.get_table('testable')
        await ch.send(str(ttb.get()))


