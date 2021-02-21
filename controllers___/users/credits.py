from discord.ext import commands
from discord import Embed
from discord import Colour
from discord import File
import asyncio
import re
from .superchat import Superchat
from .economy import Economy
from ..misc import emote

class Credits(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.sc = Superchat()
        self.ec = Economy(bot, db)

    @commands.group(aliases=['c', 'credit'])
    async def credits(self, ctx):
        """ Display instruction and current HoloCredits
        """
        ch = ctx.message.channel
        author = ctx.message.author
        if ctx.invoked_subcommand is None:
            amt = self.db.get_currency('credits', author.id)
            desc = '''You have %s**%s** HoloCredits.
To give HoloCredits, use `a.c give <user> <amount>`.
To throw some HoloCredits on the floor, use `a.c throw <amount>`.
'''%(emote['credits'], amt)
            emb = Embed(description=desc, colour=Colour(1).dark_green())
            await ch.send(embed=emb)

    @credits.command(aliases=['g'])
    async def give(self, ctx, user=None, amount=1):
        instruction = '`a.c give <user> <amount>`'
        await self.ec.give_currency(ctx, 'credits', instruction, user, amount)

    @credits.command(aliases=['t'])
    async def throw(self, ctx, amount=1):
        instruction = '`a.c throw <amount>`'
        await self.ec.throw_currency(ctx, 'credits', instruction, amount)

    @commands.command(aliases=['sc', 'supacha'])
    async def superchat(self, ctx, user=None, amount=None, *, description=''):
        ch = ctx.message.channel
        author = ctx.message.author
        user_id = author.id

        # Input checking # may be redundant with 'error' below
        instruction = '`a.superchat <user> <amount> (optional: description)`'
        if user is None:
            await ch.send('Please specify a user! ' + instruction)
            return
        if amount is None:
            await ch.send('Please specify an amount to donate! ' + instruction)
            return
        if int(amount) <= 0:
            await ch.send('<:Coco_Bruh:724450363658469467>')
            return

        # Target search
        print('new user?: ', self.db.new_user(user_id))
        target = await self.ec.search_user(ctx, user)
        if target is None:
            await ch.send('Target user not found. Try putting their name in quotes or their user ID.')
        else:
            # Give the credits
            error = self.ec.give(author, 'credits', target, amount)
            if not error:
                self.db.new_transaction(author.id, target.id, 'credits', amount, 'superchat')
                # Download their profile image and create a superchat out of it
                print('prof URL',author.avatar_url)
                profile_img = await self.sc.get_from_url(author.avatar_url)
                sc_img = self.sc.create_superchat(author.display_name, profile_img, amount, description)
                path = self.sc.save(sc_img)
                print(path)
                image = open(path, 'r')
                to_upload = File(path, filename='superchat.png')
                image.close()
                await ch.send('%s just sent a superchat to %s!'%(author.mention, target.mention), file=to_upload)
            else:
                await ch.send(error)




