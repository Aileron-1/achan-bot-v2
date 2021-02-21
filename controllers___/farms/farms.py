""" Farms will be an experiment in making a better database interface than whatever I'm using now.
"""
from discord.ext import commands
from discord import Embed
from discord import Colour
import asyncio
from ..misc import emote
from ..pagination import Pagination
from .crops import fetch_crops
from math import floor
from math import ceil
from .farmstead import Farmstead
from .plot import Plot
from .farm_display import FarmDisplay
from .farm_misc import display_price
from .farm_misc import convert_price
from .farm_misc import generate_crop_info
from ..xp import calculate_level

class Farms(commands.Cog):
    def __init__(self, bot, db, farm_db):
        self.bot = bot
        self.db = db
        self.api = farm_db
        self.crop_data = fetch_crops('Crops')
        self.active_displays = []
        self.upgrade_costs = [
            (5000, 3),  # cost, level
            (10000, 10),
            (20000, 25),
            #(50000, 50)
        ]

    @asyncio.coroutine
    async def show_farm(self, ch, author, mode='build'):
        """ Destroy other displays that this user owns and make a new display instance
        """
        # Search for and stop old displays for this author
        to_remove = []
        for d in self.active_displays:
            if d.author == author:
                to_remove.append(d)
        for d in to_remove:
            await d.stop()
            self.active_displays.remove(d)
        # Make the display
        display = FarmDisplay(self.api, self.db, author, ch, self.crop_data, self.bot, mode)
        self.active_displays.append(display)
        await display.start()

    @asyncio.coroutine
    async def build_farm(self, ch, user):
        """ Prompts user whether they want to build a farm.
        """
        user_id = user.id
        current_credits = self.db.get_currency('credits', user_id)
        cost = 10000
        desc = """Cheap land for sale - a great opportunity to release your past burdens and start anew.
Work the land for produce or build yourself a home. Secure an honest, hard-working life NOW!

*Only %s**%s** HoloCredits!*

`Your HoloCredits:` %s**%s** 
Purchase land? Type Y or N.""" % (emote['credits'], cost, emote['credits'], current_credits)
        emb = Embed(title='Real estate ad', description=desc)
        emb.set_thumbnail(url='https://cdn.discordapp.com/attachments/284659352151785472/742861909048688651/chi_urichi.png')
        confirm_message = await ch.send(embed=emb)

        # Wait for user send y or n
        while True:
            def check(m):
                return m.channel == ch and m.author.id == user_id
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            msg_ctx = await self.bot.get_context(msg)
            if msg_ctx.valid:
                await confirm_message.add_reaction(emote['no'])
                return
            elif msg.content.lower() == 'y':
                break
            elif msg.content.lower() == 'n':
                await msg.add_reaction(emote['no'])
                return
        # Check if they can afford
        if self.db.spend_currency('credits', user.id, cost):
            # Make the farm!
            self.api.new_farmer(user_id)
            await ch.send('*(Farmland purchased, %s**%s**)*\nCongratulations on your new land, %s. Use `a.farm` to check it out!' % (emote['credits'],-cost,user.mention))
        else:
            await ch.send('I\'m afraid you won\'t get any land with that paltry sum of cash, %s...' % user.mention)


    @commands.group(aliases=['f', 'farms'])
    async def farm(self, ctx):
        if ctx.invoked_subcommand is None:
            ch = ctx.message.channel
            author = ctx.message.author

            if self.api.user_has_farm(author.id):
                '''await ch.send("""%s
This is your farm! Use `a.farm help` for more commands.""" % author.mention)'''
                await self.show_farm(ch, author)
            else:
                await self.build_farm(ch, author)


    @farm.command(aliases=['h'])
    async def help(self, ctx):
        intro = """
Welcome to Farms! Use your land to earn money and resources. Build crops, collect resources, and prosper!

A farm has "plots" which you can grow crops on. You can interact with these plots by clicking on the respective reaction (1,2,3...).
"""
        cmds = """
`a.farm` - Shows your farm. Collect and build using this interface.
`a.farm crops` - Shows a list of crops available for you to build. 
`a.farm upgrade` - Upgrade the size of your farm (more slots). 
`a.farm sell <plot #>` - Sell a crop early for 1/3rd of the price.
`a.farm help` - Shows this message.

**(with farm open)**
`refresh` or `r` - Refreshes the farm view.
*`(1,2,3...)`* - Set the crop type you want to build.

*You can shorthand commands with letters, like `farm crops` with `f c`.*
"""
        costs = ''
        i = 2
        for s in self.upgrade_costs:
            costs += '\nSize %s - %s**%s**, level **%s**'%(i,emote['credits'], s[0], s[1])
            i += 1

        upgrading = """
Collecting crops gives XP. A longer grow time gives more XP. Non-reusable crops also give more XP when collected. 

Farm size increases # of plots. There is a level prerequisite per size. 
%s

You can upgrade using `a.farms upgrade`.
""" % costs
        page1 = Embed(title='Farms Help - Introduction', colour=Colour(1).green())
        page1.add_field(name='Intro', value=intro, inline=False)
        page1.add_field(name='Commands', value=cmds, inline=False)

        page3 = Embed(title='Farms Help - Levels and Upgrading', colour=Colour(1).green())
        page3.add_field(name='Upgrading your farm', value=upgrading, inline=False)

        page5 = Embed(title='Farms Help - Tutorial', description='Each react (1,2,3...) corresponds to a plot, i.e. `1` corresponds to plot #1. ', colour=Colour(1).green())
        page5.add_field(name='Building a crop', value='1) Open your farm with `a.f`.\n2) Select a crop by typing the ID of the crop you want to build. \n3) Click on a reaction and to build your crop on the respective plot!', inline=False)
        page5.add_field(name='Collecting a crop', value='1) Open your farm with `a.f`.\n2) Click on a reaction (plot) that has fully grown to harvest it. Profit!', inline=False)

        pagination = Pagination(self.bot, ctx, [page1, page5, page3])
        pagination.timeout = 180.0
        await pagination.start()

    @farm.command(aliases=['s'])
    async def sell(self, ctx, choice=None):
        ch = ctx.message.channel
        author = ctx.message.author
        # Get the player's farm. move this to api later
        farm_data, plot_data = self.api.get_farm_and_plots(author.id)
        if farm_data is None:
            await ch.send('You don\'t have a farm yet!')
        if choice is None:
            instruction = 'You must specify the plot # to sell from. \na.farm sell <plot #>'
            await ch.send('`%s`' % instruction)
            return  # change this later
        else:
            farm = Farmstead(farm_data['id'], farm_data['user_id'], farm_data['name'], farm_data['size'], farm_data['xp'])  # is generating the whole farm necessary?...later
            for p in plot_data:
                # Search for matching crop id
                crop = None
                for c in self.crop_data:
                    if c.id == p['crop_id']:
                        crop = c
                farm.add_plot(Plot(p['id'], p['time_planted'], crop))
        # Get sell price from base cost
        try:
            choice_index = int(choice)-1
            if choice_index < 0:
                # Cancel
                raise Exception()
            selected_plot = farm.plots[choice_index]
        except:
            await ch.send('Invalid plot # to sell.')
            return
        crop = selected_plot.crop
        if not crop:
            await ch.send('There\'s no crop there to sell.')
            return
        credits_reward, asacoco_reward, yubi_reward = convert_price(crop.cost)
        credits_reward = ceil(credits_reward / 3)
        asacoco_reward = ceil(asacoco_reward / 3)
        yubi_reward = floor(yubi_reward / 3)
        sell_price = display_price((credits_reward, asacoco_reward, yubi_reward))
        await ch.send('Are you sure you want to sell %s for %s? (**Y/N**)'%(crop.name, sell_price))

        # Wait for user to type y
        def check(m):
            return m.channel == ch and m.author == author and m.content.lower() == 'y' or m.content.lower() == 'n'
        try:
            m = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            print('timed out') # look a an alternative later
        else:
            if m.content.lower() == 'y':
                # Remove crop then add currency
                self.api.remove_crop(selected_plot.id)
                selected_plot.fallow()
                print('sold')
                if credits_reward:
                    self.db.add_currency('credits', author.id, credits_reward)
                if asacoco_reward:
                    self.db.add_currency('asacoco', author.id, asacoco_reward)
                if yubi_reward:
                    self.db.add_currency('yubi', author.id, yubi_reward)
                await ch.send('Sold **%s** for **%s**.' % (crop.name, sell_price))

                # Set the display's farm to this, if it exists
                for d in self.active_displays:
                    if d.farm:
                        if d.farm.id == farm.id:
                            d.farm = farm
                            await d.render()
            else:
                await ch.send('Sell cancelled.')

    @farm.command(aliases=['crop', 'c'])
    async def crops(self, ctx):
        author = ctx.message.author
        # Get the crops the user is eligible to plant and ineligible
        farm = self.api.get_farm(author.id)
        unlocked_crops = self.api.eligible_crops(self.crop_data, farm['id'])
        locked_crops = self.api.eligible_crops(self.crop_data, farm['id'], True)
        # Split them into pages of 6, while keeping whether the crop was unlocked
        item_limit = 6
        all_crops = []  # List of lists
        page = []  # List of up to 6 (crops, whether crop is unlocked)
        # Loop through unlocked and locked crops,
        for c in unlocked_crops:
            page.append((c, True))
            if len(page) >= item_limit:
                all_crops.append(page)
                page = []
        for c in locked_crops:
            page.append((c, False))
            if len(page) >= item_limit:
                all_crops.append(page)
                page = []
        if len(page) > 0:
            all_crops.append(page)
        # Generate unlocked crops pages
        pages = []
        for p in all_crops:
            # Each list inside all_crops is a page
            emb = Embed(title='%s\'s Crop List' % author.name, description='These are your crops. You can plant them using the `a.f` display!', colour=Colour(1).green())
            for crop in p:
                c = crop[0]
                unlocked = crop[1]
                if unlocked:
                    info = generate_crop_info(self.crop_data, c, False)
                    emb.add_field(name='%s #**%s**: %s'%(c.emoji[-1], c.id, c.name), value=info)
                else:
                    req = '__Unlock: #%s__\n' % c.prerequisite
                    info = req + generate_crop_info(self.crop_data, c, False)
                    emb.add_field(name='%s ~~#**%s**: %s~~'%(c.emoji[-1], c.id, c.name), value=info)
            pages.append(emb)
        # Show pagination embed
        pagination = Pagination(self.bot, ctx, pages)
        pagination.timeout = 120.0
        await pagination.start()

    @farm.command(aliases=['u'])
    async def upgrade(self, ctx):
        ch = ctx.message.channel
        author = ctx.message.author
        farm = self.api.get_farm(author.id)
        size = farm['size']
        level = calculate_level(farm['xp'])

        if size is not None:
            if size < 4:
                req_level = self.upgrade_costs[size-1][1]
                cost = self.upgrade_costs[size-1][0]
                if level >= req_level:
                    confirm_message = await ch.send('Your current farm size is **%s**. Upgrading will increase its size to **%s**, costing %s**%s** HoloCredits. Upgrade? **(Y/N)**'%(size, size+1, emote['credits'], cost))
                    while True:
                        def check(m):
                            return m.channel == confirm_message.channel and m.author == author
                        msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                        msg_ctx = await self.bot.get_context(msg)
                        if msg_ctx.valid:
                            await confirm_message.add_reaction(emote['no'])
                            return
                        elif msg.content.lower() == 'y':
                            break
                        elif msg.content.lower() == 'n':
                            await msg.add_reaction(emote['no'])
                            return
                    # Check if they can afford
                    if self.db.spend_currency('credits', author.id, cost):
                        # Upgrade
                        self.api.upgrade_farm(author.id)
                        await ch.send('**-%s%s** HoloCredits. Congratulations, your farm is now size **%s**! \n'
                                      'Open a new farm to see your plots!'%(emote['credits'],cost, size+1))
                    else:
                        await ch.send('%s, you don\'t have enough HoloCredits to upgrade!' % author.mention)
                else:
                    await ch.send('You need to be at least level **%s** to upgrade your farm to size %s! You are currently level **%s**.' % (req_level, size+1, level))
            else:
                await ch.send('You already have the maximum farm size!')
        else:
            await ch.send('You don\'t have a farm to upgrade at all!')

    @commands.Cog.listener()
    async def on_message(self, message):
        # for each display, run their message event
        for d in self.active_displays:
            asyncio.create_task(d.on_message(message))  # maybe lags if many messages and loops?

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # for each display, run their on_react event
        for d in self.active_displays:
            asyncio.create_task(d.on_react(reaction, user))


