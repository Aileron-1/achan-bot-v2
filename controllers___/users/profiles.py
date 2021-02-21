from discord.ext import commands
from discord import Embed
from discord import Colour
import asyncio
import datetime
import random
from .economy import Economy
from ..misc import emote
from ..misc import currency_names
from ..pagination import Pagination

class Profiles(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.ec = Economy(bot, db)

    @commands.command(aliases=['p', 'balance'])
    async def profile(self, ctx, *, user=None):
        ch = ctx.message.channel
        author = ctx.message.author
        user_name = author.display_name
        user_id = author.id
        target = author

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
        credit = self.db.get_currency(self.db.currency[0], user_id)
        asacoco = self.db.get_currency(self.db.currency[1], user_id)
        yubi = self.db.get_currency(self.db.currency[2], user_id)

        reg_score = self.db.get_janken_score(user_id, 'regular')
        boss_score = self.db.get_janken_score(user_id, 'boss')
        reg_total = (reg_score['win']+reg_score['draw']+reg_score['loss'])
        try:
            reg_percent = round(reg_score['win']/reg_total*100, 2)
            reg_loss_percent = round(reg_score['loss']/reg_total*100, 2)
        except:
            reg_percent = 'n/a'
            reg_loss_percent = 'n/a'
        boss_total = (boss_score['win']+boss_score['draw']+boss_score['loss'])
        try:
            boss_percent = round(boss_score['win']/boss_total*100, 2)
            boss_loss_percent = round(boss_score['loss']/boss_total*100, 2)
        except:
            boss_percent = 'n/a'
            boss_loss_percent = 'n/a'

        jk_gains = self.db.get_janken_gains(user_id, 'regular')
        boss_gains = self.db.get_janken_gains(user_id, 'boss')

        desc = '''__*Look forward to new and improved Profiles with user-submitted backgrounds, frames and more!*__'''
        main_page = Embed(title=user_name+"'s Profile", description=desc, colour=Colour(1).blue())
        main_page.set_thumbnail(url=target.avatar_url)
        main_page.add_field(name='**Currency**', value='''
%s`%s`  HoloCredits
%s`%s`  AsaCoco
%s`%s`  Yubi
            ''' % (emote['hololive'], credit, emote['asacoco'], str(asacoco), emote['yubi'], yubi))

        main_page.add_field(name='**Rank**', value='''
...
        ''')

        # Make janken page
        janken_page = Embed(title=user_name+"'s Profile", description=desc, colour=Colour(1).blue())
        janken_page.set_thumbnail(url=target.avatar_url)
        janken_page.add_field(name='**Regular Janken**', value='''
Played: **%s**
Win: **%s**%%
Loss: **%s**%%

Total winnings: %s`%s`
        ''' % (reg_total, reg_percent, reg_loss_percent, emote['asacoco'], jk_gains))
        janken_page.add_field(name='**Last Boss Janken**', value='''
Games: **%s**
Win: **%s**%%
Loss: **%s**%%

Total winnings: %s`%s`
        ''' % (boss_total, boss_percent, boss_loss_percent, emote['asacoco'], boss_gains))

        # Send pagination
        pages = [main_page, janken_page]
        pagination = Pagination(self.bot, ctx, pages)
        await pagination.start()

    #@commands.command(aliases=['t', 'timer'])
    #async def timers(self, ctx):


    @commands.command(aliases=['d'])
    async def daily(self, ctx):
        """ Claim your daily HoloCredits and AsaCoco. 20 hour cooldown.
        """
        ch = ctx.message.channel
        author = ctx.message.author
        user_id = author.id

        print('new user?: ', self.db.new_user(user_id))

        # Check user's last usage of Daily
        reset_time = 60 * 60 * 20

        last_daily = datetime.datetime.fromtimestamp(self.db.get_daily(user_id))
        since_last_daily = last_daily - datetime.datetime.now()
        if since_last_daily.total_seconds() < -reset_time:
            # Add currencies to user
            cred_amount = 1000 + (random.randint(0, 15)*10)
            ac_amount = 24 + random.randint(0, 4)
            yubi_amount = 1
            self.db.add_currency(self.db.currency[0],user_id, cred_amount)
            self.db.add_currency(self.db.currency[1],user_id, ac_amount)
            self.db.add_currency(self.db.currency[2],user_id, yubi_amount)
            self.db.update_daily(user_id, datetime.datetime.timestamp(datetime.datetime.now()))

            print(user_id, cred_amount, ac_amount)

            desc = '''
+%s`%s`  HoloCredits
+%s`%s`  AsaCoco
+%s`%s`  Yubi
                ''' % (emote['hololive'], cred_amount, emote['asacoco'], ac_amount, emote['yubi'], yubi_amount)

            emb = Embed(title=author.display_name + " just gained...", description=desc, colour=Colour(1).teal())
            emb.set_footer(text='Daily reward')
            await ch.send(embed=emb)
        else:
            # Convert seconds to formatted time
            time_until = reset_time + since_last_daily.total_seconds()
            datetime_until = str(datetime.timedelta(seconds=time_until))

            hours = datetime_until.split(':')[0]
            mins = datetime_until.split(':')[1]
            mins = str(int(mins))

            await ch.send('Next daily reset in **' + hours + 'h ' + mins + 'm**.')



    def rank_currency(self, ctx, currency):
        ranks = self.db.rank(currency)
        i = 0
        top_list = ''
        for u in ranks:
            i += 1
            if i > 10:
                break
            # Try guild display name, fall back to general name, then fall back to 'unknown'
            try:
                username = ctx.message.guild.get_member(int(u[0])).display_name
            except:
                try:
                    username = self.bot.get_user(int(u[0])).display_name
                except:
                    username = 'unknown user'
            amount = str(u[1])
            top_list += '**' + str(i) + '.** *' + emote[currency] + amount + '* | ' + username + '\n'
        top_list += ''

        title = 'Top 10 '+currency_names[currency]+':'
        emb = Embed(title=title, description=top_list, colour=Colour(1).dark_blue())
        emb.set_footer(text='Top 10')
        return emb

    def rank_janken(self, ctx):
        ranks = self.db.janken_rank('regular')
        i = 0
        top_list = ''
        for u in ranks:
            i += 1
            if i > 10:
                break
            try:
                username = ctx.message.guild.get_member(int(u[0])).display_name
            except:
                try:
                    username = self.bot.get_user(int(u[0])).display_name
                except:
                    username = 'unknown user'
            amount = str(u[1])
            top_list += '**%s.** *%s wins* | %s\n' % (str(i), amount, username)
        top_list += ''

        title = 'Top 10 Regular Janken Wins:'
        emb = Embed(title=title, description=top_list, colour=Colour(1).dark_blue())
        emb.set_footer(text='Top 10')
        return emb

    def rank_lost(self, ctx):
        ranks = self.db.rank_janken_gains(-1)
        ranks.reverse()
        i = 0
        top_list = ''
        for u in ranks:
            i += 1
            if i > 10:
                break
            try:
                username = ctx.message.guild.get_member(int(u[0])).display_name
            except:
                try:
                    username = self.bot.get_user(int(u[0])).display_name
                except:
                    username = 'unknown user'
            amount = str(u[1])
            top_list += '**%s.** %s*%s* | %s\n' % (str(i), emote['asacoco'], amount, username)
        top_list += ''

        title = 'Top 10 Janken Losses (Gross):'
        emb = Embed(title=title, description=top_list, colour=Colour(1).dark_blue())
        emb.set_footer(text='Top 10')
        return emb

    def rank_boss(self, ctx):
        ranks = self.db.janken_rank('boss')
        i = 0
        top_list = ''
        for u in ranks:
            i += 1
            if i > 10:
                break
            try:
                username = ctx.message.guild.get_member(int(u[0])).display_name
            except:
                try:
                    username = self.bot.get_user(int(u[0])).display_name
                except:
                    username = 'unknown user'
            amount = str(u[1])
            top_list += '**%s.** *%s wins* | %s\n' % (str(i), amount, username)
        top_list += ''

        title = 'Top 10 Last Boss Janken Wins:'
        emb = Embed(title=title, description=top_list, colour=Colour(1).dark_blue())
        emb.set_footer(text='Top 10')
        return emb

    def rank_earned(self, ctx):
        ranks = self.db.rank_janken_gains()
        i = 0
        top_list = ''
        for u in ranks:
            i += 1
            if i > 10:
                break
            try:
                username = ctx.message.guild.get_member(int(u[0])).display_name
            except:
                try:
                    username = self.bot.get_user(int(u[0])).display_name
                except:
                    username = 'unknown user'
            amount = str(u[1])
            top_list += '**%s.** %s*%s* | %s\n' % (str(i), emote['asacoco'], amount, username)
        top_list += ''

        title = 'Top 10 Janken Earnings (Gross):'
        emb = Embed(title=title, description=top_list, colour=Colour(1).dark_blue())
        emb.set_footer(text='Top 10')
        return emb


    def rank_simp_given(self, ctx):
        """ Ranks by superchats given.
            Ignores when sc self
        """
        ranks = self.db.simp_rank()
        i = 0
        top_list = ''
        for u in ranks:
            i += 1
            if i > 10:
                break
            # Try guild display name, fall back to general name, then fall back to 'unknown'
            try:
                username = ctx.message.guild.get_member(int(u[0])).display_name
            except:
                try:
                    username = self.bot.get_user(int(u[0])).display_name
                except:
                    username = 'unknown user'
            amount = str(u[1])
            top_list += '**%s.** %s*%s given* | %s\n' % (str(i), emote['credits'], amount, username)
        top_list += ''

        title = 'Top 10 Simps:'
        emb = Embed(title=title, description=top_list, colour=Colour(1).dark_red())
        emb.set_footer(text='Top 10')
        return emb

    def rank_simp_received(self, ctx):
        """ Ranks by superchats given.
            Ignores when sc self
        """
        ranks = self.db.simp_rank_received()
        i = 0
        top_list = ''
        for u in ranks:
            i += 1
            if i > 10:
                break
            # Try guild display name, fall back to general name, then fall back to 'unknown'
            try:
                username = ctx.message.guild.get_member(int(u[0])).display_name
            except:
                try:
                    username = self.bot.get_user(int(u[0])).display_name
                except:
                    username = 'unknown user'
            amount = str(u[1])
            top_list += '**%s.** %s*%s received* | %s\n' % (str(i), emote['credits'], amount, username)
        top_list += ''

        title = 'Top 10 Simped:'
        emb = Embed(title=title, description=top_list, colour=Colour(1).dark_red())
        emb.set_footer(text='Top 10')
        return emb



    async def make_pages(self, ctx):
        """ Returns a list of currency page functions that each return an embed.
        """
        pages = [
            self.rank_currency(ctx, 'credits'),
            self.rank_currency(ctx, 'asacoco'),
            self.rank_currency(ctx, 'yubi'),
            self.rank_janken(ctx),
            self.rank_boss(ctx),
            self.rank_earned(ctx),
            self.rank_lost(ctx),
            self.rank_simp_given(ctx),
            self.rank_simp_received(ctx)
        ]
        return pages

    @commands.group(aliases=['t'])
    async def top(self, ctx):
        if ctx.invoked_subcommand is None:
            pages = await self.make_pages(ctx)
            pagination = Pagination(self.bot, ctx, pages)
            await pagination.start()

    @top.command(aliases=['c'])
    async def credits(self, ctx):
        pages = await self.make_pages(ctx)
        pagination = Pagination(self.bot, ctx, pages)
        pagination.page_no = 0
        await pagination.start()

    @top.command(aliases=['a'])
    async def asacoco(self, ctx):
        pages = await self.make_pages(ctx)
        pagination = Pagination(self.bot, ctx, pages)
        pagination.page_no = 1
        await pagination.start()

    @top.command(aliases=['y'])
    async def yubi(self, ctx):
        pages = await self.make_pages(ctx)
        pagination = Pagination(self.bot, ctx, pages)
        pagination.page_no = 2
        await pagination.start()

    @top.command(aliases=['j'])
    async def janken(self, ctx):
        pages = await self.make_pages(ctx)
        pagination = Pagination(self.bot, ctx, pages)
        pagination.page_no = 3
        await pagination.start()

    @top.command(aliases=['lbj', 'boss'])
    async def lastbossjanken(self, ctx):
        pages = await self.make_pages(ctx)
        pagination = Pagination(self.bot, ctx, pages)
        pagination.page_no = 4
        await pagination.start()

    @top.command()
    async def earned(self, ctx):
        pages = await self.make_pages(ctx)
        pagination = Pagination(self.bot, ctx, pages)
        pagination.page_no = 5
        await pagination.start()

    @top.command(alias=['losses'])
    async def lost(self, ctx):
        pages = await self.make_pages(ctx)
        pagination = Pagination(self.bot, ctx, pages)
        pagination.page_no = 6
        await pagination.start()

    @top.command()
    async def simp(self, ctx):
        pages = await self.make_pages(ctx)
        pagination = Pagination(self.bot, ctx, pages)
        pagination.page_no = 7
        await pagination.start()

    @top.command()
    async def simped(self, ctx):
        pages = await self.make_pages(ctx)
        pagination = Pagination(self.bot, ctx, pages)
        pagination.page_no = 8
        await pagination.start()

    @commands.command()
    async def give(self, ctx):
        ch = ctx.message.channel
        await ch.send('Please specify the currency type to give, e.g. `a.asacoco give` or `a.yubi give`.')

    @commands.command()
    async def prize(self, ctx):
        ch = ctx.message.channel
        author = ctx.message.author
        # Stop if not admin and not in holores
        if not ctx.message.author.guild_permissions.administrator:
            return
        if not ctx.message.channel.guild.id == 660839081558933555:
            return

        # Prize name
        await ch.send('So you\'re sending out a prize. Please specify what this prize is for.'
                      '*(e.g. Art competition winners)*')
        def check(m):
            return m.channel == ch and m.author.id == author.id
        msg = await self.bot.wait_for('message', timeout=60.0, check=check)
        prize_name = msg.content

        ########################### add cancelling mid way

        # Users
        await ch.send('Now specify the recipient(s) of the prize by mentioning all of them in 1 message.')
        while True:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            users = msg.mentions
            # check all entries and see if they are users
            if len(users) > 50:
                await ch.send('Can\'t give prizes to more than 50 users.')
            elif len(users) > 0:
                break
            else:
                await ch.send('Error, try again!')

        # Holocredit amount
        await ch.send('Finally, let\'s specify the prizes. '
                      'How many HoloCredits is this prize worth?')
        while True:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            try:
                credits = int(msg.content)
                break
            except:
                await ch.send('That\'s not a valid number! Try again.')

        # Asacoco amount
        await ch.send('Great, that\'s %s HoloCredits. '
                      'How much Asacoco is this prize worth?' % credits)
        while True:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            try:
                asacoco = int(msg.content)
                break
            except:
                await ch.send('That\'s not a valid number! Try again.')


        # Yubi amount
        await ch.send('Great, that\'s %s Asacoco. '
                      'How many Yubi is this prize worth?' % asacoco)
        while True:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            try:
                yubi = int(msg.content)
                break
            except:
                await ch.send('That\'s not a valid number! Try again.')

        # Item id
        # Make user name display
        user_str = ''
        for u in users:
            user_str += u.name + ', '
        user_str = user_str[:-2]
        # Show confirmation
        combined_content = '`Prize name: %s\n' \
                           'Recipients: %s\n' \
                           'Credits: %s\n' \
                           'Asacoco: %s\n' \
                           'Yubi: %s`' % (prize_name, user_str, credits, asacoco, yubi)
        await ch.send(combined_content)
        # Accept, done
        await ch.send('If the above is correct, type **(Y/N)** to confirm and send the prize to the recipients now. ')
        def check_yn(m):
            return m.channel == ch and m.author == author and m.content.lower() == 'y' or m.content.lower() == 'n'
        try:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check_yn)
        except asyncio.TimeoutError:
            print('timed out') # look a an alternative later
            await ch.send('Timed out. Cancelled.')
            return
        else:
            if msg.content.lower() == 'n':
                await ch.send('Cancelled.')
                return
            else:
                pass
        # Create rewards string
        reward_str = ''
        if credits > 0:
            reward_str += '%s**%s**, ' % (emote['credits'], credits)
        if asacoco > 0:
            reward_str += '%s**%s**, ' % (emote['asacoco'], asacoco)
        if yubi > 0:
            reward_str += '%s**%s**, ' % (emote['yubi'], yubi)
        reward_str = reward_str[:-2]

        # Send dm to all, with 1sec delay
        for u in users:
            print('Sending to %s' % u.name)
            try:
                await u.send('Congratulations, you got a reward for `%s`. '
                             '+%s' % (prize_name, reward_str))
            except:
                await ch.send('Something went wrong. (type a. %s)' % u.id)
            try:
                if credits > 0:
                    self.db.add_currency('credits', u.id, credits)
                if asacoco > 0:
                    self.db.add_currency('asacoco', u.id, asacoco)
                if yubi > 0:
                    self.db.add_currency('yubi', u.id, yubi)
            except:
                await ch.send('Something went wrong. (type a. %s)' % u.id)
            # Have 1sec delay unless we're last user in list
            if u != users[-1]:
                await asyncio.sleep(1)
        await ch.send('Done!')

