import discord
from discord.ext import commands
from discord import Embed

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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


    @commands.command(aliases=['changelog', 'log'])
    async def changes(self, ctx):
        ch = ctx.message.channel
        emb = Embed(title='A-chan changelog', description='''''', colour=discord.Colour(1).blue())
        days = [
            Day('09/08', [
                'Fixed a rare bug where farm wouldn\'t appear for specific users.',
                'Update Help command.'
            ]),
            Day('09/04', [
                'Fixed farms command only working on \'f\' and \'farm\'.',
                'Fixed some farm-related typos.'
            ]),
            Day('09/04', [
                'Added Farms, a new income source. Use a.farms help for more info.',
                'Added initial item system, which grants bonuses to the user.',
                'Look forward to new and improved custom profiles in the coming updates!'
            ]),
            Day('08/12', [
                'Fixed SC having no limits but wouldn\'t go through (no damage).',
                'Re-enabled black market. Nerfed to only 2 items per hour to balance with farms.',
                'Farms alpha coming in a few days or so.'
            ]),
            Day('07/30', [
                'Updates :honma_yay:.',
                'Added top SIMPs. More to come. Yes you can spam trade sc but if you do I\'ll start taxing it :watame_smug:'
            ]),
            Day('05/04', [
                'Slightly modified janken delays, and other small janken improvements.',
                'Now able to change your choice in lastboss janken again.'
            ]),
            Day('05/03', [
                'Change yubi regrow to 3hr intervals and allow growing multiple in 1 command.',
                'Add shortened alias for yubi regrow, a.rg.',
                'Dailies now give an additional +1 yubi.',
                'No longer deletes superchat command message.',
                'Reworded janken win announcements (still the same mechanics).'
            ]),
            Day('05/02', [
                'Added superchat colours! They map to the same japanese yen amounts as on Youtube.'
            ])
        ]

        first = True
        max_entries = 3
        for d in days:
            max_entries -= 1
            if max_entries < 0:
                break
            if first:
                name = '**%s**' % d.day
            else:
                name = d.day
            first = False
            desc = ''
            for e in d.entries:
                desc += '`- %s`\n' % e
            emb.add_field(name=name, value=desc, inline=False)
        await ch.send(embed=emb)

    @commands.command()
    async def bug(self, ctx):
        ch = self.bot.get_channel(702831466127556688)
        await ch.send('%s `%s`: %s'%(ctx.message.author.mention, ctx.message.author.id, ctx.message.content))
        await ctx.message.channel.send('Thank you %s, report received.'%ctx.message.author.mention)

class Day:
    def __init__(self, day='??/??', entries=None):
        if entries is None:
            entries = []
        self.day = day
        self.entries = entries

    def log(self, desc):
        self.entries.append(desc)
