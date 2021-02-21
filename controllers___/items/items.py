from discord.ext import commands
from discord import Embed
from discord import Colour
from ..misc import emote
from ..pagination import Pagination

class Items(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    def get_user_balance(self, user_id): # change later
        cred = self.db.get_currency('credits', user_id)
        ac = self.db.get_currency('asacoco', user_id)
        yubi = self.db.get_currency('yubi', user_id)
        return '**%s%s | %s%s | %s%s**'%(emote['credits'], cred, emote['asacoco'], ac, emote['yubi'], yubi)

    @commands.group(aliases=['i'])
    async def items(self, ctx):
        if ctx.invoked_subcommand is None:
            ch = ctx.message.channel
            author = ctx.message.author
            balance = self.get_user_balance(author.id)
            emb = Embed(title='%s\'s Items' % (author.name),
                        description='%s\nUse `a.items help` for more info.' % balance,
                        colour=Colour(1).blue())
            emb.add_field(name="Equipped Items", value="`Slot 1`: `None`\n`Slot 2`: `None`\n`Slot 3`: `None`", inline=False)
            emb.add_field(name="Inventory (%s/100)" % 0, value="`You don\'t have any items yet!`", inline=False)
            emb.set_footer(text='A-chan Items')
            await ch.send(embed=emb)

    @items.command(aliases=['h'])
    async def help(self, ctx):
        ch = ctx.message.channel
        emb = Embed(title='Items Help - Introduction',
                    description='Users can collect items through various means such as the shop, gacha, or rewards.\n\n'
                                'Up to 100 items can be stored, but the effects of the item are only granted when equipped. Only 3 items can be equipped at once.\n\n'
                                '*There are currently no items in circulation yet. Check back in a few weeks!*',
                    colour=Colour(1).blue())
        emb.set_footer(text='A-chan Items')
        await ch.send(embed=emb)


