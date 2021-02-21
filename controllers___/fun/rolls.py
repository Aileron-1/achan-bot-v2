from discord.ext import commands
import random
import asyncio
from math import ceil
from ..misc import emote
from ..misc import currency_names
from ..timers import time_til_next_hour
from ..timers import time_til_next_third_hr

class Rolls(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.emotes = [
            '<:Suisei_Pog:724463389849681941>',
            '<:Suisei_Wink:724463390667571232>',
            '<:Suisei_Smug:724463390319181825>',
            '<:Suisei_Think:724463390327832597>',
            '<:Suisei_Smile:724463390650662973>',
            '<:Suisei_Gun:724463390092689429>',
            '<:Suisei_Shookt:724463390038425702>',
            '<:Hoshimachi_Suisip:724464578511110214>'
            ]

    @commands.Cog.listener()
    async def on_ready(self):
        asyncio.create_task(self.start_reset_tri())
        asyncio.create_task(self.start_reset_hourlies())

    @asyncio.coroutine
    async def start_reset_hourlies(self):
        """ Wait until the next o'clock time, then start resetting
        """
        wait_seconds = time_til_next_hour()
        # Wait the number of seconds then run the task
        print('I\'m going to wait '+str(wait_seconds)+' seconds.')
        await asyncio.sleep(wait_seconds)
        print('ok, waited. starting Hourly')
        loop = asyncio.get_event_loop()
        loop.create_task(self.hourly())

    @asyncio.coroutine
    async def start_reset_tri(self):
        """ Wait until the next third hour, then start resetting
        """
        wait_seconds = time_til_next_third_hr()
        # Wait the number of seconds then run the task
        print('I\'m going to wait '+str(wait_seconds)+' seconds for tri.')
        await asyncio.sleep(wait_seconds)
        print('ok, waited. starting Trily')
        loop = asyncio.get_event_loop()
        loop.create_task(self.trily())

    async def hourly(self):
        while True:
            # Reset tests, then repeat after 1 hr
            print('resetting tests')
            self.db.set_all('tests', '0')
            self.db.set_all('factory', '0')
            await asyncio.sleep(60*60)

    async def trily(self):
        while True:
            # Reset regrows, then repeat after 3 hr
            print('resetting grows')
            self.db.set_all('regrows', '0')  # hack for now. use a separate cog that takes in Tasks to run, later
            await asyncio.sleep(60*60*3)

    # Gets a random emote string from a selection
    def random_emote(self):
        return random.choice(self.emotes)

    def roll_emote(self):
        emote = self.random_emote()
        random_int = min(random.randint(1, 10), random.randint(1, 10))
        emote = emote * random_int
        return emote, random_int

    @staticmethod
    def get_encounter():
        """ Replace the roll with a random encounter """
        encounters = [
            Encounter(True, 'You found some pills on the side of the road!', ':pill:', 'asacoco', (3,7)),
            Encounter(True, 'You found some pills on the side of the road!', ':pill:', 'asacoco', (3,7)),
            Encounter(True, 'You found some pills on the side of the road!', ':pill:', 'asacoco', (3,7)),
            Encounter(True, 'You found some pills on the side of the road!', ':pill:', 'asacoco', (3,7)),
            Encounter(True, 'You found some pills on the side of the road!', ':pill:', 'asacoco', (3,7)),
            Encounter(True, 'You found a bunch of white wool!', emote['ovo'], 'credits', (80,200)),
            Encounter(True, 'You found a present!', ':gift:', 'asacoco', (10,19)),
            Encounter(True, 'You found a present!', ':gift:', 'asacoco', (10,19)),
            Encounter(True, 'You found a shooting star!', emote['comet'], 'credits', (700,999)),
            Encounter(True, 'You found someone\'s air canister!', emote['ac_tank'], 'asacoco', (30,50)),
            Encounter(True, 'You found a literal disembodied finger on the floor...', emote['yubi'], 'yubi', (1,1))
        ]
        return random.choice(encounters)

    @commands.command(aliases=['r', 'test'])
    async def roll(self, ctx, roll_all=''):
        """ Roll for HoloCredits and a chance to win random prizes. """
        ch = ctx.message.channel
        author = ctx.message.author
        user_name = author.mention
        user_id = author.id
        encounter_chance = 18

        # Check if user has rolls left
        current_tests = self.db.get_currency('tests', user_id)
        max_tests = 7  # unique max rolls tbd
        print(current_tests)
        if roll_all.lower() == 'all':
            # If the user wants to roll all
            times = max_tests-current_tests
        else:
            times = 1

        # Check for pre-conditions
        yubi = self.db.get_currency('yubi', user_id)
        if yubi <= 0:
            await ch.send(user_name+', how are you supposed to do anything without fingers...? *(0 Yubi)*')
            return
        # input filtering
        if not isinstance(times, int):
            times = 1

        if current_tests < max_tests:
            self.db.add_currency('tests', user_id, times)  # increment # of tests this hr
            emotes = ''
            messages = ''
            total_emotes = 0
            total_credits = 0
            total_asacoco = 0
            total_yubi = 0
            for i in range(times):
                print(i)
                ind_string = '`%s:` '%(i+1)
                # see if we get a random encounter this roll
                if random.randint(0,encounter_chance) == 0:
                    # then get exactly what encounter it was
                    encounter = self.get_encounter()

                    reward, currency, flav_text = encounter.get_reward()
                    emotes += encounter.emote+'\n'
                    messages += '\n'+ind_string+flav_text
                    self.db.add_currency(currency, user_id, reward)

                    if currency == 'credits':
                        total_credits += reward
                    if currency == 'asacoco':
                        total_asacoco += reward
                    if currency == 'yubi':
                        total_yubi += reward
                else:
                    # normal roll
                    roll, amount = self.roll_emote()
                    emotes += roll+'\n'
                    total_emotes += amount
                    # if exceptional...
                    bonus = 0
                    if amount == 8:
                        bonus = 25
                        messages += '\n%sGreat! *8* Suiseis. *Bonus* %s+**%s**'%(ind_string, emote['credits'], bonus)
                    if amount == 9:
                        bonus = 50
                        messages += '\n%sNice! That\'s *9* Suiseis! *Bonus* %s+**%s**'%(ind_string, emote['credits'], bonus)
                    if amount == 10:
                        bonus = 1000
                        messages += '\n%sWOW! You got max *10* Suiseis! *Bonus* %s+**%s**'%(ind_string, emote['credits'], bonus)
                    if bonus > 0:
                        total_credits += bonus
                        self.db.add_currency('credits', user_id, bonus)

            if total_emotes > 0:
                messages += '\nGot %s+**%s** from %s emotes.' %(emote['credits'], total_emotes, total_emotes)
                total_credits += total_emotes
                self.db.add_currency('credits', user_id, total_emotes)
            if times > 1:
                messages += '\n%s`Total:` **%s+%s**'%('',emote['credits'],total_credits)
                if total_asacoco > 0:
                    messages += ',** %s+%s**'%(emote['asacoco'],total_asacoco)
                if total_yubi > 0:
                    messages += ',** %s+%s**'%(emote['yubi'],total_yubi)
            await ch.send(emotes)
            print('roll charcount:',len(emotes))
            await ch.send(messages)
        else:
            # convert wait seconds to hour:minute format
            wait_seconds = time_til_next_hour()
            hr_only = wait_seconds//(60*60)
            min_only = ceil(wait_seconds%(60*60)/60)
            await ch.send('**%s**, `roll` is limited to %s uses per hour. Next reset is in **%sh %sm**.'%(user_name, max_tests, hr_only, min_only))


    @commands.command()
    async def percent(self, ctx):
        ch = ctx.message.channel
        author = ctx.message.author
        user_name = author.mention
        user_id = author.id
        emote = self.random_emote()
        random_int = random.randint(0,100)

        # Check for pre-conditions
        yubi = self.db.get_currency('yubi', user_id)
        if yubi <= 0:
            # not enough yub
            ch.send(user_name+', how are you supposed to do anything without fingers...? Current yubi: '+yubi)
            return

        numbers = [
            'zero',
            'one',
            'two',
            'three',
            'four',
            'five',
            'six',
            'seven',
            'eight',
            'nine'
        ]
        # splits the int into digits and converts each digit to an emote
        str_int = str(random_int)
        emotes = ''
        for char in str_int:
            word = numbers[int(char)]
            emotes += ':'+word+':'

        print('percent', author, ctx.message.content, str_int)
        await ch.send(emote+' '+emotes)
        return emote+' '+emotes


    @commands.command()
    @commands.cooldown(1, 11, commands.BucketType.user)
    async def beg(self, ctx):
        ch = ctx.message.channel
        author = ctx.message.author
        rand = random.randint(0,45)

        if rand == 1:
            amount = random.randint(1,10)
            currency = random.choice(['asacoco', 'credits'])
            drop_message = await ch.send('%s just threw %s**%s** %s on the floor! *(React to pick up)*' % (
            self.bot.user.mention, emote[currency], amount, currency_names[currency]))
            await drop_message.add_reaction(emote[currency])

            # Check for pick up
            def react_check(reaction, user):
                if user == drop_message.author:
                    return
                return str(reaction.emoji) == emote[currency] and reaction.message.id == drop_message.id
            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=8.0, check=react_check)
                except asyncio.TimeoutError:
                    await drop_message.delete()
                    break
                else:
                    if self.db.get_currency('yubi', user.id) <= 0:
                        await ch.send('%s, you can\'t pick things up without fingers! *(0 Yubi)*'%user.mention)
                    else:
                        await drop_message.edit(content='%s picked up %s\'s %s**%s** %s.' % (
                        user.mention, self.bot.user.mention, emote[currency], amount, currency_names[currency]))
                        self.db.add_currency(currency, user.id, int(amount))
                        print('pick up by %s' % user.id)
                        break
        elif rand == 2:
            # Penalty react
            amount = -1
            currency = 'yubi'
            drop_message = await ch.send('%s just threw a bomb on the floor! *(React to pick up)*' % (
            self.bot.user.mention))
            await drop_message.add_reaction('\U0001F4A3')

            # Check for pick up
            def react_check(reaction, user):
                if user == drop_message.author:
                    return
                return str(reaction.emoji) == '\U0001F4A3' and reaction.message.id == drop_message.id
            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=8.0, check=react_check)
                except asyncio.TimeoutError:
                    await drop_message.delete()
                    break
                else:
                        if self.db.get_currency('yubi', user.id) <= 0:
                            await ch.send('%s, you can\'t pick things up without fingers! *(0 Yubi)*'%user.mention)
                        else:
                            await drop_message.edit(content='%s picked up a bomb.\nIt exploded! *(-1 Yubi)*' % (
                            user.mention))
                            self.db.add_currency(currency, user.id, int(amount))
                            print('pick up bomb by %s' % user.id)
                            break
        elif 3 <= rand <= 10:
            # Penalty react
            drop_message = await ch.send('%s just threw some trash at %s!' % (
            self.bot.user.mention, author.mention))
            await drop_message.add_reaction('\U0001F5D1')

            # Check for pick up
            def react_check(reaction, user):
                if user == drop_message.author:
                    return
                return str(reaction.emoji) == '\U0001F5D1' and reaction.message.id == drop_message.id
            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=8.0, check=react_check)
                except asyncio.TimeoutError:
                    await drop_message.delete()
                    break
                else:
                    if self.db.get_currency('yubi', user.id) <= 0:
                        await ch.send('%s, you can\'t pick things up without fingers! *(0 Yubi)*'%user.mention)
                    else:
                        if random.randint(0,4) == 1:
                            await drop_message.edit(
                                content='%s picked up some trash. It has a faint taste of AsaCoco! *(%s+1 AsaCoco)*' % (user.mention, emote['asacoco']))
                            self.db.add_currency('AsaCoco', user.id, 1)
                        else:
                            await drop_message.edit(content='%s picked up some trash. It tastes bad. *(%s-1 HoloCredits)*' % (user.mention, emote['credits']))
                            self.db.add_currency('credits', user.id, -1)

                        print('pick up trash by %s' % user.id)
                        break
        else:
            await ch.send('...')

    @beg.error
    async def mine_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = 'Try that again in **{:.2f}s**.'.format(error.retry_after)
            await ctx.send(msg)
        else:
            raise error

class Encounter:
    def __init__(self, positive, flavour, emoji, currency, reward_range):
        self.flavour = flavour
        if positive:
            self.emote = ':sparkles:%s:sparkles: '%emoji
        else:
            self.emote = emote['nothing']+emoji+emote['nothing']
        self.currency = currency
        self.reward_range = reward_range

    def get_reward(self):
        reward = random.randint(self.reward_range[0], self.reward_range[1])
        currency = self.currency
        flav_text = '%s %s+**%s**'%(self.flavour, emote[self.currency], reward)
        return reward, currency, flav_text

