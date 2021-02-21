from discord.ext import commands
from discord import Embed
from ..misc import emote
from ..misc import currency_names
from .products import Products
import asyncio
import datetime

class Shops(commands.Cog):
    def __init__(self, bot, db, shop_db):
        self.bot = bot
        self.db = db
        self.shop_db = shop_db
        self.bm_products = Products('Black market')
        self.shop_products = Products('Shop')

    @staticmethod
    def find_product_by_id(products, product_id):
        for product in products:
            if int(product.product_id) == int(product_id):
                return product

    def get_items(self, products, shop_id):
        items = []
        stocks = self.shop_db.get_stocks(shop_id)
        for s in stocks:
            new_item = self.find_product_by_id(products, s[2])
            new_item.id = s[0]
            new_item.shopfront = s[1]
            new_item.stock = s[3]
            new_item.markup = s[4]  # temporary, testing
            new_item.cost = s[5]
            new_item.product = s[6]
            items.append(new_item)
        return items

    def add_item_fields(self, emb, user, items):
        delta = datetime.timedelta(hours=1)
        now = datetime.datetime.now()
        next_hour = (now + delta).replace(microsecond=0, second=0, minute=0)
        time_til_next = round(((next_hour - now).seconds+30)/60)
        emb.clear_fields()

        # Add balance field
        cred = self.db.get_currency('credits', user.id)
        ac = self.db.get_currency('asacoco', user.id)
        yubi = self.db.get_currency('yubi', user.id)
        balance = '**%s%s | %s%s | %s%s**'%(emote['credits'], cred, emote['asacoco'], ac, emote['yubi'], yubi)
        emb.add_field(name='**Your Balance**',
                      value=balance,
                      inline=False)
        # Add item fields
        numbers = [
            0,
            emote['one'],
            emote['two'],
            emote['three'],
            4,
            5
        ]
        i = 1
        total_stock = 0
        for item in items:
            if item.stock != -1:  ## hack: changed from 0 to -1
                product_string = '%s**%s** %s' % (emote[item.product_type], item.product, currency_names[item.product_type])
                cost_string = '%s**%s**  %s' % (emote[item.cost_type], item.cost, currency_names[item.cost_type])
                emb.add_field(name='**%s** %s' % (numbers[i], item.name),
                              value='''
`Product:` %s
`Cost:` %s
`Stock:` **%s** left''' % (product_string, cost_string, item.stock),
                          inline=False)
            i += 1
            total_stock += item.stock
        # Show error if no stock
        if total_stock == 0:
            emb.add_field(name='No Stock!',
                          value='You\'ve bought me out brother. See you for the next restock.',
                          inline=False)

        emb.add_field(name='**Info**', value='The black market selection resets every **1** hour interval. \nNext reset: **%s mins**.' % time_til_next)

    @commands.command(aliases=['bm'])
    async def blackmarket(self, ctx):
        ch = ctx.message.channel
        author = ctx.message.author
        products = self.bm_products.generate_products()
        picked_products = self.bm_products.pick_few(2)

        # Create new storefront if has been more than an hour since last
        try:
            shop_id, last_shop = self.shop_db.get_latest_shop(author.id)
            print('it worked..?')
        except:
            shop_id = 0
            last_shop = 0
        rounded_down_to_last_hour = datetime.datetime.fromtimestamp(last_shop).replace(microsecond=0, second=0, minute=0)
        time_since_last = datetime.datetime.now()-rounded_down_to_last_hour
        threshold = 60*60
        if time_since_last.total_seconds() >= threshold or last_shop == 0:
            print('new hour, new shop!')
            # Create a new storefront for this hour, for this user
            self.shop_db.insert_data('Shopfronts', {
                'user_id': author.id,
                'type': '0',
                'time_created': datetime.datetime.now().timestamp()
            })
            shop_id = self.shop_db.get_latest_shop(author.id)[0]
            # Create the items for the storefront too
            i = 0
            for item in picked_products:
                print('stock',item.base_stock)
                self.shop_db.insert_data('Stock', {
                    'shopfront_id': shop_id,
                    'item_id': item.product_id,
                    'current_stock': item.base_stock,
                    'markup': author.id,  # temporarily borrowing this unused column, for test
                    'cost': item.cost,
                    'product': item.product
                })
                i += 1

        # Get all items related with this shop
        items = self.get_items(products, shop_id)
        for i in items:
            print(i.__dict__)

        # Create shop embed
        emb = Embed(title='Black Market for %s'%author.name,
                    description='*"Been a while hasn\'t it?"*\nThe shadowy figure pulls down their hood with a smile.\n*"I\'ve still gotta lay low, but I\'ll open up just for you."*',
                    colour=0x111111)
        emb.set_footer(text='Please select an item to purchase')
        emb.set_thumbnail(url='https://cdn.discordapp.com/attachments/694832333232275596/698716554925178950/maxresdefault3.jpg')

        # add item fields
        self.add_item_fields(emb, author, items)

        # send embed and reacts
        shop_message = await ch.send(author.mention, embed=emb)
        reacts = {emote['one']:0,
                  emote['two']:1#,
                  #emote['three']:2
                  }
        for r in reacts:
            await shop_message.add_reaction(r)

        # Check for reacts
        confirm_message = None
        while True:
            def react_check(reaction, user):
                return user == author and str(reaction.emoji) in reacts and reaction.message.id == shop_message.id
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=react_check)
            except asyncio.TimeoutError:
                await shop_message.clear_reactions()
                break
            else:
                # User reacts. ask for confirmation
                # Get item they want to buy
                item = items[reacts[str(reaction.emoji)]]

                # check if in stock
                item_stock = self.shop_db.get_value('current_stock', item.id)
                if item_stock > 0:
                    cost = '%s**%s** %s'%(emote[item.cost_type],item.cost, currency_names[item.cost_type])

                    # Delete the old message
                    if confirm_message is not None:
                        await confirm_message.delete()
                    confirm_message = await ch.send('%s *%s* costs %s. Continue?'%(author.mention, item.name, cost))
                    yesno = [emote['ok'],emote['no2']]
                    for r in yesno:
                        await confirm_message.add_reaction(r)
                    def react_check(reaction, user):
                        return user == author and str(reaction.emoji) in yesno and reaction.message.id == confirm_message.id
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=react_check)
                    except asyncio.TimeoutError:
                        await confirm_message.clear_reactions()
                        break
                    else:
                        if reaction.emoji == emote['ok']:
                            # check afford
                            afford = self.db.spend_currency(item.cost_type, author.id, item.cost)
                            if not afford:
                                await ch.send('%s, You can\'t afford this item! *Not enough %s*'%(author.mention, currency_names[item.cost_type]))
                            if afford:
                                # give out money
                                self.db.add_currency(item.product_type, author.id, item.product)
                                # decrement stock
                                print(item.id)
                                self.shop_db.add_value('current_stock', item.id, -1)
                                await confirm_message.edit(content='Purchased *%s* - thank you %s'%(item.name, emote['coco_smug']))
                                await confirm_message.clear_reactions()
                                # update old shop stock display
                                items = self.get_items(products, shop_id)
                                self.add_item_fields(emb, author, items)
                                await shop_message.edit(embed=emb)

                        if reaction.emoji == emote['no2']:
                            await confirm_message.edit(content='Purchase cancelled. Please pick another product instead.')
                            await confirm_message.clear_reactions()
                elif item_stock <= 0:
                    print('stockless', item_stock, self.shop_db.get_value('current_stock', item.id), items, shop_id)
                    await ch.send('*%s* has no stock left! *(Try opening a new blackmarket if this is an error)*'%item.name)
                else:
                    print('stockelse', item_stock, self.shop_db.get_value('current_stock', item.id))
                    await ch.send('`Error retrieving stock from db. Try opening a new blackmarket.`')






    '''@commands.command()
    async def destroydb(self, ctx):
        self.shop_db.build_table('Shopfronts', [
            'id INTEGER PRIMARY KEY',
            'user_id INTEGER',
            'type INTEGER',
            'time_created INTEGER'
        ])
        self.shop_db.build_table('Stock', [
            'id INTEGER PRIMARY KEY',
            'shopfront_id INTEGER',
            'item_id INTEGER',
            'current_stock INTEGER',
            'markup INTEGER',
            'cost INTEGER',
            'product INTEGER'
        ])
        ch = ctx.message.channel
        await ch.send('ok')

    @commands.command()
    async def shoptest(self, ctx):
        ch = ctx.message.channel
        author = ctx.message.author

        # Create shop embed
        emb = Embed(title='Shop for %s'%author.name,
                    description='*Coming soon:* upgrades and items!',
                    colour=0xfff2cc)
        emb.set_thumbnail(url='https://cdn.discordapp.com/attachments/696054651782692937/698048896773128232/yujina.jpg')
        await ch.send(embed=emb)'''

