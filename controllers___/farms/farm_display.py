from discord import Embed
from discord import Colour
from discord import NotFound
import asyncio
from ..misc import emote
from .farmstead import Farmstead
from .plot import Plot
from .farm_misc import display_price
from .farm_misc import convert_price
from .farm_misc import generate_crop_info
from .farm_misc import seconds_to_hm
from ..xp import generate_xp_bar
from ..xp import calculate_level
from ..xp import to_next_level
from ..xp import calculate_xp_breakpoint

class FarmDisplay:
    """ A class for handling state changes of a given farm front end.
        Wasn't entirely necessary
    """
    def __init__(self, api, db, author, ch, crop_data, bot, mode):
        self.selected_crop = None
        self.farm = None
        self.emb = None
        self.mode = mode
        self.bot = bot
        self.author = author
        self.ch = ch
        self.api = api
        self.crop_data = crop_data
        self.db = db
        self.display_message = None#''
        self.log_message = ''
        self.farm_message = None
        self.farm = None
        self.reacts = {
            emote['one']: 0,
            emote['two']: 1,
            emote['three']: 2,
            emote['four']: 3,
            emote['five']: 4
            }
        self.msg_listen = None
        self.react_list = None

    def get_user_balance(self, user_id): # change later
        cred = self.db.get_currency('credits', user_id)
        ac = self.db.get_currency('asacoco', user_id)
        yubi = self.db.get_currency('yubi', user_id)
        return '**%s%s | %s%s | %s%s**'%(emote['credits'], cred, emote['asacoco'], ac, emote['yubi'], yubi)

    def generate_farm_embed(self):
        # Get player's currency
        balance = self.get_user_balance(self.author.id)
        # Get player's XP bar
        level = calculate_level(self.farm.xp)
        base_xp = calculate_xp_breakpoint(level)
        relative_xp = self.farm.xp - base_xp
        to_next = to_next_level(level)

        xp_bar = '%s*%s/%s xp*'%(generate_xp_bar(relative_xp, to_next), relative_xp, to_next)
        # Generate embed text, showing all plots
        instruction = 'Use `a.farm help` for help.'
        if level <= 1:
            instruction = '''Use `a.farm help` for more help.
            
**Tips:**
a) Select a crop by typing `1`.
b) Then, click an empty plot to build it. 
c) Click on a crop when it's grown to harvest it.'''
        emb = Embed(title='%s\'s Farm (Level %s)' % (self.author.name, level), description='%s\n%s\n%s'%(balance, xp_bar, instruction), colour=Colour(1).green())
        emb.set_footer(text='Farms Beta. "a.farm help"')
        crop_text = ''
        index = 1
        for p in self.farm.plots:
            crop = '`Plot #%s:` ' % index
            if p.crop is None:
                crop += '*Empty*'
            else:
                time = seconds_to_hm(p.time_until_ready())
                if p.time_until_ready() > 0:
                    crop += p.crop.name + ' - Time left: __%s__' % time
                else:
                    crop += p.crop.name + ' - \U00002728 Ready! \U00002728'
            crop_text += crop+'\n'
            index += 1
        emb.add_field(name='Plots:', value=crop_text)
        if self.mode == 'build':
            if self.selected_crop is None:
                crop_info = '*None selected. Type a crop ID to select one. Use `a.f crops` to show buildable crops.*'
            else:
                # calculate cost and reward
                crop_info = self.selected_crop.emoji[-1]+' '+generate_crop_info(self.crop_data, self.selected_crop)
            emb.add_field(name='Crop to Build:', value=crop_info, inline=False)
        if self.log_message:
            emb.add_field(name='\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\___Log__\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_', value=self.log_message, inline=False)  # lol
        return emb

    @asyncio.coroutine
    async def render(self):
        """ Updates all values to refresh the display.
        """
        # Update farm and currency
        print('rendering')
        if self.farm_message:
            await self.farm_message.edit(content=self.farm.get_emote(), embed=self.generate_farm_embed())

    @asyncio.coroutine
    async def start(self):
        # Get the player's farm
        farm_data, plot_data = self.api.get_farm_and_plots(self.author.id)
        if farm_data is None:
            await self.ch.send('You don\'t have a farm yet!')
            return  # change this later
        else:
            self.farm = Farmstead(farm_data['id'], farm_data['user_id'], farm_data['name'], farm_data['size'], farm_data['xp'])
            for p in plot_data:
                # Search for matching crop id
                crop = None
                for c in self.crop_data:
                    if c.id == p['crop_id']:
                        crop = c
                self.farm.add_plot(Plot(p['id'], p['time_planted'], crop))
        # Display the farm
        emb = self.generate_farm_embed()
        self.farm_message = await self.ch.send(self.farm.get_emote(), embed=emb)
        # Add reactions per each farm plot
        i = 0
        for r in self.reacts:
            if i < len(self.farm.plots):
                asyncio.create_task(self.farm_message.add_reaction(r))
            i += 1

    @asyncio.coroutine
    async def stop(self):
        print('stopping')
        if self.display_message:
            try:
                await self.display_message.delete()
            except NotFound:
                print('Display msg not found')
        if self.farm_message:
            try:
                await self.farm_message.delete()
            except NotFound:
                print('Farm msg not found')
        if self.msg_listen:
            self.msg_listen.cancel()
        if self.react_list:
            self.react_list.cancel()

    @asyncio.coroutine
    async def on_message(self, message):
        """ For use on message event. Checks if the message is a command, then run it.
        """
        # Only run if same author and same channel as display
        if message.author == self.author and  message.channel == self.ch:
            content = message.content.lower()
            # Set selected_crop if digit
            if content.isdigit():
                # Try if the ID is valid. Remember we are +1 for the front-facing ID (no id 0)
                await message.delete()  # Delete message to save space.
                try:
                    num = int(content)-1
                    to_select = self.crop_data[num]
                except:
                    await self.update_display_message('Invalid crop ID.')
                    await self.render()
                    return
                if to_select in self.api.eligible_crops(self.crop_data, self.farm.id):
                    self.selected_crop = to_select
                    await self.update_display_message('Selected *%s*. Now click an empty plot to build it!' % (self.selected_crop.name))
                else:
                    await self.update_display_message('You can\'t build that!/Invalid ID.')
                await self.render()
            # Check for other commands
            async def refresh():
                await self.update_display_message('Refreshed display.')
                await self.render()
            async def xp():
                self.farm.xp += 250
                self.api.add_xp(self.farm.id, 250)
                await self.update_display_message('cheated +250 xp.')
                await self.render()

            cmds = { 'refresh': refresh }
            for c in cmds:
                if len(content) > 0:
                    if content == c or content[0] == c[0]:
                        await cmds[c]()
                        break

    @asyncio.coroutine
    async def on_react(self, reaction, user):
        """ Called when a react on a farm is pressed
        """
        # fulfil conditions
        if str(reaction.emoji) in self.reacts \
                and reaction.message.id == self.farm_message.id \
                and user == self.author:
            print('REACT ACTUALLY PRESSED')
            # Chose a reaction
            choice = self.reacts[str(reaction.emoji)]
            selected_plot = self.farm.plots[choice]
            # If plot is empty
            if selected_plot.ready() is None:
                # If there is a crop selected
                if self.selected_crop is not None:
                    # convert costs into creds, ac, yubi
                    credits_cost, asacoco_cost, yubi_cost = convert_price(self.selected_crop.cost)
                    # if can afford, spend money then plant crop on plot
                    afford_credits = self.db.enough_currency('credits', self.author.id, credits_cost)
                    afford_asacoco = self.db.enough_currency('asacoco', self.author.id, asacoco_cost)
                    afford_yubi = self.db.enough_currency('yubi', self.author.id, yubi_cost)
                    if afford_credits and afford_asacoco and afford_yubi:
                        self.db.spend_currency('credits', self.author.id, credits_cost)
                        self.db.spend_currency('asacoco', self.author.id, asacoco_cost)
                        self.db.spend_currency('yubi', self.author.id, yubi_cost)
                        selected_plot.plant(self.selected_crop)
                        self.api.plant_crop(selected_plot.id, self.selected_crop.id)
                        price = display_price((credits_cost, asacoco_cost, yubi_cost))
                        display_string = '-**%s**. Planted %s in plot %s.' % (price, self.selected_crop.name, choice+1)
                    else:
                        display_string = 'You can\'t afford this crop!'
                else:
                    display_string = 'You haven\'t selected a crop type to build yet.'
            # If the plot is ready
            elif selected_plot.ready():
                # Crop ready
                crop = selected_plot.crop
                credits_reward, asacoco_reward, yubi_reward = convert_price(crop.product)
                prev_level = calculate_level(self.farm.xp)
                unlocks = self.api.will_unlock(self.crop_data, self.farm.id, crop.id)
                if selected_plot.harvest():
                    self.api.harvest_crop(selected_plot.id, crop.reusable)
                    if credits_reward:
                        self.db.add_currency('credits', self.author.id, credits_reward)
                    if asacoco_reward:
                        self.db.add_currency('asacoco', self.author.id, asacoco_reward)
                    if yubi_reward:
                        self.db.add_currency('yubi', self.author.id, yubi_reward)
                    self.api.add_xp(self.farm.id, crop.xp)
                    self.farm.xp += crop.xp
                display_string = 'Collected %s in plot %s. +**%s**! +%s xp.' % (
                    crop.name,
                    choice+1,
                    display_price(convert_price(crop.product)),
                    crop.xp
                )
                # Display unlock if this harvest will unlock something.
                if len(unlocks):
                    unlock_str = ''
                    for c in unlocks:
                        unlock_str += '**%s**, ' % c.name
                    display_string += '\nUnlocked %s.' % unlock_str[:-2]
                # Display level up if the level changed since harvesting
                new_level = calculate_level(self.farm.xp)
                if new_level > prev_level:
                    # Award 50 asacoco on level up
                    amount = 50 + new_level * 10
                    self.db.add_currency('asacoco', self.author.id, amount)
                    display_string += '\n*Congratulations! Your farm is now level **%s**.* \nReward: **%s**' % (new_level, display_price((0,amount,0)))
            # Plot crop isn't ready
            else:
                display_string = '*%s* will not be ready to collect for another: **%s**' % (
                selected_plot.crop.name, seconds_to_hm(selected_plot.time_until_ready()))
            # Update display message and farm
            await self.update_display_message(display_string)
            await self.render()

    @asyncio.coroutine
    async def update_display_message(self, message):
        self.log_message = message
        '''if self.display_message is None:
            self.display_message = await self.ch.send(message)
        else:
            await self.display_message.edit(content=message)'''

