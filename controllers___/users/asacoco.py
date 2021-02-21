from discord.ext import commands
from discord import Embed
from discord import Colour
import asyncio
from .economy import Economy
from .emotes import emote

class AsaCoco(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.ec = Economy(bot, db)

    @commands.group(aliases=['a'])
    async def asacoco(self, ctx):
        ch = ctx.message.channel
        author = ctx.message.author
        if ctx.invoked_subcommand is None:
            amt = self.db.get_currency('asacoco', author.id)

            desc = '''You have %s**%s** AsaCoco.
To give AsaCoco, use `a.a give <user> <amount>`.
To throw some AsaCoco on the floor, use `a.a throw <amount>`.
'''%(emote['asacoco'], amt)
            emb = Embed(description=desc, colour=Colour(1).dark_green())
            await ch.send(embed=emb)

    @asacoco.command(aliases=['g'])
    async def give(self, ctx, user=None, amount=1):
        instruction = '`a.a give <user> <amount>`'
        await self.ec.give_currency(ctx, 'asacoco', instruction, user, amount)


    @asacoco.command(aliases=['t'])
    async def throw(self, ctx, amount=1):
        instruction = '`a.a throw <amount>`'
        await self.ec.throw_currency(ctx, 'asacoco', instruction, amount)


    @asyncio.coroutine
    async def consume_asacoco(self, ctx, string, suffix):
        ch = ctx.message.channel
        author = ctx.message.author
        user_id = author.id

        print('new user?: ', self.db.new_user(user_id))

        afforded = self.db.spend_currency(self.db.currency[1], user_id, 1)
        if afforded:
            self.db.add_currency('overdose', user_id, 1)
            await ch.send('**' + author.mention + '** just **' + string + '** an ' + emote['asacoco'] + 'AsaCoco ' + suffix)
        else:
            await ch.send('**' + author.mention + '**... you\'ve run out of ' + emote['asacoco'] + 'AsaCoco...')

    @commands.command()
    async def inject(self, ctx):
        await self.consume_asacoco(ctx, 'injected', '')

    @commands.command()
    async def smoke(self, ctx):
        await self.consume_asacoco(ctx, 'smoked', '')

    @commands.command()
    async def inhale(self, ctx):
        inhale = '<:Watame_AsaCoco:724450405525880865>'
        await self.consume_asacoco(ctx, 'inhaled', inhale)

    @commands.command()
    async def drink(self, ctx):
        await self.consume_asacoco(ctx, 'drank', '<:ac_drink:695570179605659699>')

    @commands.command()
    async def pill(self, ctx):
        await self.consume_asacoco(ctx, 'swallowed', ':pill:')

    @commands.command()
    async def insert(self, ctx):
        await self.consume_asacoco(ctx, 'inserted', '<:Coco_Haah:724450363905671269>')

    @commands.command()
    async def eyedrop(self, ctx):
        await self.consume_asacoco(ctx, 'dropped', 'in their eyes')

    @commands.command()
    async def mouthwash(self, ctx):
        await self.consume_asacoco(ctx, 'gargled', '')

    @commands.command()
    async def ointment(self, ctx):
        await self.consume_asacoco(ctx, 'rubbed', 'all over their body')

    @commands.command()
    async def lotion(self, ctx):
        await self.consume_asacoco(ctx, 'applied', 'all over their body')

    @commands.command()
    async def lubricant(self, ctx):
        await self.consume_asacoco(ctx, 'squirted', 'all over their body <:Coco_Haah:724450363905671269>')

    @commands.command()
    async def spray(self, ctx):
        await self.consume_asacoco(ctx, 'sprayed', '')

    @commands.command()
    async def surgery(self, ctx):
        await self.consume_asacoco(ctx, 'replaced their kidney with', '')

    @commands.command()
    async def snort(self, ctx):
        await self.consume_asacoco(ctx, 'snorted', '')

    @commands.command()
    async def eat(self, ctx):
        await self.consume_asacoco(ctx, 'ate', '')

    @commands.command()
    async def plug(self, ctx):
        await self.consume_asacoco(ctx, 'plugged in', '<:ac_plug:695570159523463208>')

    @commands.command()
    async def furikake(self, ctx):
        await self.consume_asacoco(ctx, 'ate', '')
