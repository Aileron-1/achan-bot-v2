import asyncio
import re
from ..misc import emote
from ..misc import currency_names

class Economy:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @asyncio.coroutine
    async def search_user(self, ctx, user):
        try:
            target = ctx.message.guild.get_member_named(user)
        except:
            target = None
        print(user, target)
        if user is not None and target is None:
            print('in')
            # If that fails, then it might be a mention
            # Get user ID from mention (hack)
            r = re.compile(r'[0-9]*')
            result = r.findall(user)
            while '' in result:
                result.remove('')
            try:
                target_id = result[0]
                print(target_id)
                # Grab target
                target = await ctx.message.guild.fetch_member(target_id)
            except:
                return None
        return target

    def give(self, user, currency, target, amount):
        # Input checking
        if user is None:
            return 'Please specify a user! '
        if amount is None:
            return 'Please specify an amount! '
        if int(amount) <= 0:
            return '<:Coco_Bruh:702897259171282994>'
        # Check if afford
        afforded = self.db.spend_currency(currency, user.id, int(amount))
        if not afforded:
            return '%s, you don\'t have enough %s%s!' % (user.mention, emote[currency], currency_names[currency])
        # Increase target currency, after making their account
        print('new user?: ', self.db.new_user(target.id))
        self.db.add_currency(currency, target.id, int(amount))

        return None

    @asyncio.coroutine
    async def give_currency(self, ctx, currency=None, instruction='', user=None, amount=None):
        ch = ctx.message.channel
        author = ctx.message.author
        # Search target
        target = await self.search_user(ctx, user)
        print(target)
        if target is None:
            await ch.send('`User not found.`')
            return False
        # Give to target
        error = self.give(author, currency, target, amount)
        self.db.new_transaction(author.id, target.id, currency, amount, 'give_currency')
        if error is not None:
            await ch.send(error+' '+instruction)
            return False
        # Announce
        await ch.send('%s gave %s**%s** %s to %s!'%(author.mention, emote[currency], amount, currency_names[currency], target.mention))
        return target

    @asyncio.coroutine
    async def get_currency(self, ctx, currency, user):
        ch = ctx.message.channel
        author = ctx.message.author
        user_id = author.id

        if user is not None:
            # Search user
            target = await self.ec.search_user(ctx, user)
            print(target)

            if target is None:
                await ch.send('`User not found.`')
                return
            else:
                user_name = target.display_name
                user_id = target.id

        print('new user?: ', self.db.new_user(user_id))
        amount = self.db.get_currency(currency, user_id)
        return amount


    @asyncio.coroutine
    async def throw_currency(self, ctx, currency=None, instruction='', amount=None):
        """ 'Throw' a currency, sending a message which players can react to for a bonus.
        """
        ch = ctx.message.channel
        author = ctx.message.author
        user_id = author.id
        print('new user?: ', self.db.new_user(user_id))

        # Input checking
        if amount is None:
            await ch.send('Please specify an amount to donate! '+instruction)
            return
        if int(amount) <= 0:
            await ch.send('<:Coco_Bruh:702897259171282994>')
            return
        # Spend - check if afford
        afforded = self.db.spend_currency(currency, user_id, int(amount))
        if not afforded:
            await ch.send('%s, you don\'t have enough %s%s!' % (author.mention, emote[currency], currency_names[currency]))
            return

        drop_message = await ch.send('%s just threw %s**%s** %s on the floor! *(React to pick up)*'%(author.mention, emote[currency], amount, currency_names[currency]))
        await drop_message.add_reaction(emote[currency])

        # Check for pick up
        def react_check(reaction, user):
            if user == drop_message.author:
                return
            return str(reaction.emoji) == emote[currency] and reaction.message.id == drop_message.id
        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=react_check)
            except asyncio.TimeoutError:
                await drop_message.edit(content='No one picked it up... *(%s %s refunded)*'%(amount, currency_names[currency]))
                self.db.add_currency(currency, author.id, int(amount))
                break
            else:
                if self.db.get_currency('yubi', user.id) <= 0:
                    await ch.send('%s, you can\'t pick things up without fingers! *(0 Yubi)*'%user.mention)
                else:
                    await drop_message.edit(content='%s picked up %s\'s %s**%s** %s.'%(user.mention, author.mention, emote[currency], amount, currency_names[currency]))
                    self.db.add_currency(currency, user.id, int(amount))
                    self.db.new_transaction(author.id, user.id, currency, amount, 'pickup')
                    print('pick up by %s'%user.id)
                    break

