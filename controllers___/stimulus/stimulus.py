from discord.ext import commands
import random
import re
from ..misc import emote

class Stimulus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_praise = 0

    # Checks how much time as passed
    @staticmethod
    def how_long_since(time1, time2):
        difference = time2 - time1
        seconds_since = difference.total_seconds()
        return seconds_since

    @commands.Cog.listener()
    async def on_message(self, msg):
        # Don't reply to self or to bots
        if msg.author == self.bot.user:
            return
        if msg.author.bot is True:
            return
        ch = msg.channel

        # rework whole stimulus thing to not be a hack

        r = re.compile(r'[\w]+')
        content = ' '.join(r.findall(msg.content.lower()))

        if content.find('unsub to sui') != -1 or content.find('don\'t sub to sui') != -1:
            print('unsub')
            emoji1 = '<:Suisei_Gun3:686289437637869568>'
            emoji2 = '<:Suisei_Gun2:686289419707088897>'
            emoji3 = '<:Suisei_Gun1:686289409943142443>'
            await msg.add_reaction(emoji1)
            await msg.add_reaction(emoji2)
            await msg.add_reaction(emoji3)
        elif content.find('sub to sui') != -1 and content.find('un') == -1:
            print('sub')
            emoji = '<:Suisei_Smile:724450405743984650>'
            if random.randint(0,1) == 1:
                emoji = '<:Hoshiyomi_of_worship:724450363058552873>'
            await msg.add_reaction(emoji)
        elif content.startswith('suichan wa'):
            await ch.send('<:kyoumo:724450363029061714><:kwaii:724450363389902969>')
        elif content.find('i removed your afk') != -1:
            print('in')
            for user in msg.mentions:
                print(user.id)
                if user.id == 190319413134753792:
                    await ch.send('konkeji!')
        elif content.startswith('praise sui'):
            send = 'https://media.discordapp.net/attachments/284659352151785472/696211653032673300/latest.png'
            if random.randint(0,15) == 1:
                send = 'https://cdn.discordapp.com/attachments/660859473056890909/696020919994286100/IMG_20200404_214233.png'
            await ch.send(send)
        elif content.startswith('sui cult'):
            send = 'Cult jyanai yo.'
            if random.randint(0,10) == 1:
                send = 'Cult... kamoshirenai...'
            await ch.send(send)
        elif content.startswith('watame wa') or content.startswith('watame ha'):
            send = 'warukunai yo ne '+emote['w_smug']
            await ch.send(send)
        elif content.startswith('moona wa') or content.startswith('moona ha'):
            if msg.author.id == 354867407698788354:
                send = 'ok zilf %s'%msg.author.mention
                await ch.send(send)
            else:
                send = 'warukunai yo ne'
                await ch.send(send)
'''
    @commands.command()
    async def lulu(self, ctx):
        ch = ctx.message.channel
        choices = [
            'https://media.discordapp.net/attachments/380994800825925642/691874779543633940/676231008093208577.gif',
            'https://media.discordapp.net/attachments/661504235464163349/694574007520854126/GMK_3O4EWFVOK460.gif',
        ]
        await ch.send(random.choice(choices))


    @commands.command()
    async def rosalyn(self, ctx):
        ch = ctx.message.channel
        msg = 'https://cdn.discordapp.com/attachments/660859473056890909/696346010871660564/rosayln.gif'
        await ch.send(msg)'''