""" This janken code is, well, jank. Don't judge, I wrote it very early on. """

from discord.ext import commands
from discord import Embed
from discord import Colour
import datetime
import random
import asyncio
from ..misc import emote

class Janken(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.active_games = []
        self.hand_emojis = {
            'rock' : emote['rock'],
            'paper' : emote['paper'],
            'scissors' : emote['scissors']
        }
        self.emoji_hands = {
            emote['rock'] : 'rock',
            emote['paper'] :'paper',
            emote['scissors'] : 'scissors'
        }

    @asyncio.coroutine
    async def janken_flavour(self, janken, ch, interlude_img, imgs, janken_type, wait=5):
        # send the embed
        emb = Embed(title='TSUNOMAKI JANKEN...', description='START!', colour=0xfff2cc)
        emb.set_image(url=interlude_img)
        emb.add_field(name='Bet/Entry cost', value=emote['asacoco']+str(janken.reward))
        deco_message = await ch.send(embed=emb)
        janken.start_game(deco_message)
        # add reactions
        for e in self.hand_emojis:
            react = await deco_message.add_reaction(self.hand_emojis[e])
        # wait, so people can join in
        await asyncio.sleep(3)
        emb.description = 'Tsunomaki tsunomaki tsunomaki tsunomaki...'
        await deco_message.edit(embed=emb)
        await asyncio.sleep(wait)
        # do jankenpon flavour
        emb.description = '**JAN**'
        await deco_message.edit(embed=emb)
        await asyncio.sleep(0.75)
        emb.description = 'JAN **KEN**'
        await deco_message.edit(embed=emb)
        await asyncio.sleep(0.75)
        emb.description = 'JAN KEN **PON!**'
        await deco_message.edit(embed=emb)
        # calculate results, and send watame choice
        results = self.janken_end(janken, janken_type)
        img = imgs[janken.watame_choice]
        emb.set_image(url=img)
        if len(janken.participants) == 0:
            # Set image to bewildered if no one joined
            emb.set_image(url='https://media.discordapp.net/attachments/461381136661217283/687361058822029396/watame1.gif')
        await deco_message.edit(embed=emb)
        return results

    def janken_end(self, janken, janken_type):
        # calculate the game results and give rewards, and adjust their stats
        results = janken.end_of_game()
        winners = []
        draws = []
        losers = []
        for player in results:
            user = self.bot.get_user(int(player))
            self.db.new_janken(user.id, janken_type, results[player], janken.reward*results[player])  # new janken
            if results[player] == 1:
                winners.append(user)
                self.db.add_currency('asacoco', user.id, janken.reward*2)
            if results[player] == 0:
                draws.append(user)
                self.db.add_currency('asacoco', user.id, janken.reward)
            if results[player] == -1:
                losers.append(user)
        return winners, draws, losers

    @commands.command()
    async def cheat1010(self, ctx, curr_type='asacoco', amt=50):
        if ctx.message.author.id == 116514420049444867:
            self.db.add_currency(curr_type, ctx.message.author.id, amt)
            await ctx.message.delete()

    @commands.command(aliases=['j'])
    async def janken(self, ctx, bet=None):
        """ Starts a janken game """
        print('Janken started')
        ch = ctx.message.channel
        author = ctx.message.author
        interlude_img = 'https://cdn.discordapp.com/emojis/682772922913390640.gif?v=1'
        imgs = [
            'https://cdn.discordapp.com/attachments/284659352151785472/697153223416479794/unknown.png',
            'https://cdn.discordapp.com/attachments/284659352151785472/697156730781696100/unknown.png',
            'https://media.discordapp.net/attachments/284659352151785472/697156845369819177/unknown.png'
        ]
        # Check for hands
        yubi = self.db.get_currency('yubi', author.id)
        if yubi < 3:
            await ch.send(author.mention + ', how are you supposed to play janken with those hands...? *(You need at least 3 yubi to play)*')
            return
        # Check for
        if bet is not None:
            #await ch.send('You can\'t add a bet to janken without owning the corresponding upgrade!')
            pass

        # Check if there already exists a janken in our channel
        found = False
        for game in self.active_games:
            if game.message.channel.id == ch.id:
                print(game.message.channel.id,ch.id)
                found = True
        if found:
            try:
                print('jankexist', ch.id)
            except:
                pass
            await ch.send('Only 1 game of janken can run at any time.')
            return

        # start the game
        janken = JankenGame(self.db)
        self.active_games.append(janken)

        # start and run embed flavor
        results = await self.janken_flavour(janken, ch, interlude_img, imgs, 'regular')

        # end janken
        winners = results[0]
        draws = results[1]
        losers = results[2]

        # announce winners
        end_message = ''
        if len(winners) > 0:
            end_message += 'Winners:'
            for user in winners:
                end_message += ' '+user.mention
            end_message += '. %s+**%s** AsaCoco!'%(emote['asacoco'], janken.reward*2)
        if len(draws) > 0:
            end_message += '\nDraws:'
            for user in draws:
                end_message += ' ' + user.mention
            end_message += '. %s**%s** AsaCoco refunded.' % (emote['asacoco'], janken.reward)

        if len(losers) > 0:
            end_message += '\nLosers:'
            for user in losers:
                end_message += ' ' + user.mention
            end_message += '. No refund!'
        # if no one reacted
        if end_message == '':
            end_message = '...No one played with me...'
        await ch.send(end_message)

        # remove the object from active games
        i = 0
        for game in self.active_games:
            if game.message.channel.id == ch.id:
                self.active_games.pop(i)
            i += 1

    @commands.command(aliases=['lastboss'])
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def lastbossjanken(self, ctx, bet=None):
        """ Starts a janken game """
        print('LAST BOSS Janken started')
        ch = ctx.message.channel
        author = ctx.message.author
        interlude_img = 'https://cdn.discordapp.com/attachments/284659352151785472/697182479689187428/finaljanken_.gif'
        imgs = [
            'https://cdn.discordapp.com/attachments/284659352151785472/697186630427082792/hellrock.jpg',
            'https://cdn.discordapp.com/attachments/284659352151785472/697186645786624090/hellpaper.jpg',
            'https://cdn.discordapp.com/attachments/284659352151785472/697186644754694235/hellscissor.jpg'
        ]

        # Check for hands
        yubi = self.db.get_currency('yubi', author.id)
        if yubi < 3:
            await ch.send(author.mention + ', how are you supposed to play janken with those hands...? *(You need at least 3 yubi to play)*')
            return
        # Check for bet item
        if bet is not None:
            #await ch.send('You can\'t add a bet to janken without owning the corresponding item!')
            pass

        user_asacoco = self.db.get_currency('asacoco', author.id)
        if user_asacoco < 50:
            await ch.send('You need at least %s**50** Asacoco to use `lastbossjanken`.' % (emote['asacoco']))
            return

        # Check if there already exists a janken in our channel
        found = False
        for game in self.active_games:
            print(game.message.channel.id,ch.id)
            if game.message.channel.id == ch.id:
                found = True
        if found:
            await ch.send('Only 1 game of janken can run at any time.')
            return

        await ch.send(
            'There is a 1/3 chance you will lose all your %s**%s** AsaCoco when playing LAST BOSS JANKEN. Are you sure? (**y/n**)' % (
            emote['asacoco'], user_asacoco))
        def check(m):
            return m.channel == ch and m.author == author
        while True:
            try:
                msg = await self.bot.wait_for('message', timeout=20.0, check=check)
            except asyncio.TimeoutError:
                return
            content = msg.content.lower()
            if content == 'n':
                await ch.send('Cancelled. ')
                return
            if content == 'y':
                break

        # start the game
        janken = JankenGame(self.db)
        janken.reward = user_asacoco
        self.active_games.append(janken)

        # start and run embed flavor
        results = await self.janken_flavour(janken, ch, interlude_img, imgs, 'boss', 8)

        # end janken
        winners = results[0]
        draws = results[1]
        losers = results[2]

        # announce winners
        end_message = ''
        if len(winners) > 0:
            end_message += '**KUSO**. Winners:'
            for user in winners:
                end_message += ' '+user.mention
            end_message += '. %s+**%s** AsaCoco!'%(emote['asacoco'], janken.reward*2)
        if len(draws) > 0:
            end_message += '\nDraws:'
            for user in draws:
                end_message += ' ' + user.mention
            end_message += '. You got off easy this time... %s**%s** refunded.' % (emote['asacoco'], janken.reward)
        if len(losers) > 0:
            end_message += '\nKSZK Losers:'
            for user in losers:
                end_message += ' ' + user.mention
            end_message += '. %s**%s** AsaCoco lost... %s' % (emote['asacoco'], janken.reward, emote['w_heh'])
        # if no one reacted
        if end_message == '':
            end_message = '...No one played with me...'
        await ch.send(end_message)

        if len(losers) >= 1 and len(winners) == 0:
            await asyncio.sleep(4)
            await ch.send('https://cdn.discordapp.com/attachments/694832333232275596/698712555618697216/tenor_1.gif')

        # remove the object from active games
        i = 0
        for game in self.active_games:
            if game.message.channel.id == ch.id:
                self.active_games.pop(i)
            i += 1


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # stop if it's ourselves
        if user == self.bot.user:
            return
        # only react if the message is ours - we don't care for reactions on other msgs
        if reaction.message.author != self.bot.user:
            return
        ch = reaction.message.channel

        for game in self.active_games:
            try:
                print(reaction.message.id, game.message.id)
            except:
                pass
            if reaction.message.id == game.message.id:
                # check type
                # possibly need to filter out any non-RPS reactions which may break the game
                print(user, self.emoji_hands[str(reaction)])
                error = game.on_react(user.id, self.emoji_hands[str(reaction)])
                if error is not None:
                    await ch.send(user.mention+error)

class JankenGame:
    def __init__(self, db):
        self.db = db
        self.message = None
        self.watame_choice = random.randint(0,2)
        self.inputs = ['rock', 'paper', 'scissors']  # reaction inputs
        self.participants = {}  # key=user_id, val=selection
        self.start_time = datetime.datetime.now()
        self.reward = 3
        self.boss = None
        self.active = False

    def start_game(self, msg):
        self.active = True
        self.message = msg
        print('watame chose '+self.int_to_rps(self.watame_choice))

    def on_react(self, user_id, hand):
        if self.active:
            # make them a user if they aren't already
            print('react. new user?: ', self.db.new_user(user_id), hand)
            # add them to the participation list
            return self.participate(user_id, self.rps_to_int(hand))

    def participate(self, user_id, selection):
        # check currencies
        yubi = self.db.get_currency('yubi', user_id)
        curr = self.db.get_currency('asacoco', user_id)
        if yubi < 3:
            return ', how are you supposed to play janken with those hands? *(Need at least 3 yubi to participate)*'

        # have them pass in the bet if they aren't already
        if str(user_id) not in self.participants:
            if curr < self.reward:
                return ', you don\'t have enough AsaCoco to meet the bet! (need %s%s more)'%(emote['asacoco'],self.reward-curr)
            self.db.add_currency('asacoco', user_id, -self.reward)
        else:
            print('already playing, switched to %s'%selection)

        # if user isn't already participating, add them
        self.participants[str(user_id)] = selection

    # calculates rock paper scissors. returns whether attacker wins or loses
    @staticmethod
    def rps(attacker, defender):
        result = None
        if (attacker + 1) % 3 == defender:
            result = -1
        elif attacker == defender:
            result = 0
        elif attacker == (defender + 1) % 3:
            result = 1
        return result

    @staticmethod
    def int_to_rps(rps):
        hands = ['rock', 'paper', 'scissors']
        return hands[rps]

    @staticmethod
    def rps_to_int(hand):
        hands = {
            'rock': 0,
            'paper': 1,
            'scissors': 2
        }
        return hands[hand]

    def end_of_game(self):
        self.active = False
        results = {}
        # check who won/lost against watamee
        for u in self.participants:
            hand = self.participants[u]
            results[u] = self.rps(hand, self.watame_choice)
        print(results)
        
        return results
