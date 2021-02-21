from discord.ext import commands
from discord import Embed
from discord import Colour
import asyncio
from .economy import Economy
from ..misc import emote
from ..misc import currency_str
from ..timers import time_til_next_third_hr
from math import ceil

class Yubi(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.ec = Economy(bot, db)

    @commands.group(aliases=['y'])
    async def yubi(self, ctx):
        ch = ctx.message.channel
        author = ctx.message.author
        if ctx.invoked_subcommand is None:
            amt = self.db.get_currency('yubi', author.id)
            wait_seconds = time_til_next_third_hr()
            hr_only = int(wait_seconds//(60*60))
            min_only = ceil(wait_seconds%(60*60)/60)
            desc = '''You have %s Yubi.
To give a yubi, use `a.y give <user>`.
You can also regrow a yubi using %s AsaCoco with `a.regrow`, 2 times per 3 hours. Next reset is in **%sh %sm**.
'''%(currency_str('yubi', amt), currency_str('asacoco', 20),  hr_only, min_only)
            emb = Embed(description=desc, colour=Colour(1).gold())
            await ch.send(embed=emb)

    @yubi.command(aliases=['g'])
    async def give(self, ctx, user=None, amount=1):
        instruction = '`a.y give <user> (amount=1)`'
        await self.ec.give_currency(ctx, 'yubi', instruction, user, amount)  # yabai code

    @yubi.command(aliases=['t'])
    async def throw(self, ctx, amount=1):
        instruction = '`a.y throw <amount>`'
        await self.ec.throw_currency(ctx, 'yubi', instruction, amount)


    @yubi.command(aliases=['regrow', 'rg'])
    async def grow(self, ctx):
        await self.grow_yubi(ctx)

    @commands.command(aliases=['rg'])
    async def regrow(self, ctx):
        await self.grow_yubi(ctx)

    @asyncio.coroutine
    async def grow_yubi(self, ctx):
        ch = ctx.message.channel
        author = ctx.message.author
        yubi = self.db.get_currency('yubi', author.id)
        user_mention = author.mention
        limit = 2
        cost_ea = 20

        # Check if they haven't regrown more than twice this hour
        current_regrows = self.db.get_currency('regrows', author.id)
        if current_regrows >= limit:
            wait_seconds = time_til_next_third_hr()
            hr_only = int(wait_seconds//(60*60))
            min_only = ceil(wait_seconds%(60*60)/60)
            await ch.send('%s, `regrow` is limited to %s uses per 3 hour interval. Next reset is in **%sh %sm**.'%(user_mention, limit, hr_only, min_only))
            return

        # Check if they have less than 2 hands
        if yubi >= 10:
            await ch.send('You can\'t regrow yubi if you already have enough for two hands!')
            return

        # Ask for confirmation
        confirm_message = await ch.send('Regrowing a yubi costs %s AsaCoco each. Type the amount that you want to regrow (**%s** left). '%(currency_str('asacoco', cost_ea), limit-current_regrows))
        def check(m):
            return m.channel == ch and m.author == author
        msg = await self.bot.wait_for('message', timeout=30.0, check=check)
        try:
            amount = int(msg.content)
            print(amount)
        except:
            await confirm_message.add_reaction(emote['no'])
            return

        # Check if over regrow limit
        if 0 >= amount:
            await confirm_message.add_reaction(emote['no'])
            return
        if amount > limit - current_regrows:
            await ch.send('That\'s regrows than you can do!')
            return
        # Check if they're growing more than 2 hands
        if yubi+amount > 10:
            await ch.send('You can\'t regrow more yubi than your two hands can hold!')
            return

        # Spend asacoco
        cost_total = cost_ea*amount
        afford = self.db.spend_currency('asacoco', author.id, cost_total)
        if afford:
            self.db.add_currency('yubi', author.id, amount)
            self.db.add_currency('regrows', author.id, amount)
            current_yubi = self.db.get_currency('yubi', author.id)
            await ch.send('You grew back %s Yubi. You now have %s.' % (currency_str('yubi', amount),currency_str('yubi',current_yubi)))
        else:
            await ch.send('You don\'t have enough %sAsaCoco!'% emote['asacoco'])
