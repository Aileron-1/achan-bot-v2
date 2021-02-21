from discord.ext import commands
from datetime import datetime
from random import randint
import asyncio

class Welcome(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.settings_tbl = self.db.get_table('Settings')
        self.welcomes_tbl = self.db.get_table('Welcomes')
        try:  # I know
            self.bans_tbl = self.db.get_table('Bans')
        except:
            self.bans_tbl = self.db.build_table('Bans', ['user_id INTEGER', 'server_id INTEGER', 'timestamp INTEGER'])

        self.guild_id = 660839081558933555  # hardcoded... 1 bot serves 1 server here

        self.raidmode = False  # Temp raidmode solution. this affects all server so.. fix later

    @commands.Cog.listener()
    async def on_message(self, msg):
        """ ***** Possible improvement: Store server data in memory to significantly reduce number of DB requests. Get data
        only on server startup, and update it only when required (i.e. when it's modified) ***** """

        # Don't reply to self or to bots or not DMs
        if msg.author == self.bot.user:
            return
        if msg.author.bot is True:
            return
        if msg.guild is not None:
            return
        # Check for DMs
        if msg.author != self.bot.user:
            try:
                print('DM from %s: %s'%(msg.author.id, msg.content))
            except:
                pass

            # Add the user to core role if they said WASSHOI and aren't already in
            ch = msg.channel
            if msg.content.lower().find('wasshoi') != -1:
                guild = self.bot.get_guild(self.guild_id)
                user = guild.get_member(msg.author.id)

                settings = self.settings_tbl.get_settings(guild.id)

                role = guild.get_role(settings['role_id'])

                # check if they are on the server - ignore for now, error will stop it (hack)

                # check if they are welcome-banned in the server
                result = self.bans_tbl.get_data(['user_id = %s' % msg.author.id, 'server_id = %s' % self.guild_id])
                if len(result) > 0 or self.raidmode:
                    await asyncio.sleep(1+randint(0, 2))
                    await ch.send('Sorry, new members are being limited at the moment. There may be another opportunity opening in the near future, good luck on securing a spot!')
                    return

                # check if they already have the role
                found = False
                for r in user.roles:
                    if r == role:
                        found = True
                        try:
                            print(r, role)
                        except:
                            print('found a role...')
                if found:
                    print('already have role')
                    return

                if msg.content.find('WASSHOI') != -1:
                    # Give them the role and announce it
                    print(settings)
                    print(role)
                    announce_channel = await self.bot.fetch_channel(settings['channel_id'])
                    await user.add_roles(role)
                    await ch.send('Done. Welcome to the Resistance!\nCome join us at %s'%announce_channel.mention)

                    # Send the announcement
                    await announce_channel.send(self.parse_text(settings['welcome_text'], user.mention, guild.name, user.name))

                    # Add them to the welcomed table
                    self.welcomes_tbl.new_welcome(guild.id, user.id)
                else:
                    # Check if they said it LOUD ENOUGH
                    await ch.send('I can\'t hear you! Say it LOUDER!')

    @commands.group(aliases=['w'])
    async def welcome(self, ctx):
        if not ctx.message.author.guild_permissions.administrator:
            # Stop if not admin
            return
        if ctx.invoked_subcommand is None:
            ch = ctx.message.channel
            settings = self.db.get_table('Settings').get_settings(ctx.message.guild.id)
            user = ctx.message.author

            try:
                target_ch = self.bot.get_channel(settings['channel_id']).mention
            except:
                target_ch = None

            role = ctx.message.guild.get_role(settings['role_id'])
            text = self.parse_text(settings['welcome_text'], user.mention, ctx.message.guild.name, user.name)

            await ch.send('''
Your current welcome settings are:
-----
**Welcome channel:** 
%s
-----
**Role to add:** 
%s
-----
**Welcome text:**
%s
-----
`w help` for more help.
            '''%(target_ch, role, text))

    @welcome.command()
    async def help(self, ctx):
        if not ctx.message.author.guild_permissions.administrator:
            # Stop if not admin
            return
        ch = ctx.message.channel
        await ch.send('''```
==Welcome Help==
(alias = w)
- w: Show your current welcome settings for this server.
- w channel <ch id>: Set the channel to send welcome announcements.
- w role <role id>: Set the role that will be added to the user.
- w text <text>: Set the text that appears when a user is added. Use the $MENTION$, $NAME$ and $SERVER$ tags for context-based text.
- w ban <user id>: Welcome-bans the user; user is blocked from getting a role from DMs. Make sure you ONLY USE USER ID.
- w unban <user id>: Undo a welcome-ban.
- w raidmode: Toggle raid mode. Essentially welcome-bans everybody temporarily. FYI, resets when the bot restarts.
```''')

    @welcome.command()
    async def channel(self, ctx, ch_id):
        """ Sets the target channel for joins.
            Takes in a channel ID
        """
        if not ctx.message.author.guild_permissions.administrator:
            # Stop if not admin
            return
        self.settings_tbl.update_server(ctx.message.guild.id, ch_id=int(ch_id))

        ch = ctx.message.channel
        await ch.send('Channel set')

    @welcome.command()
    async def role(self, ctx, role_id):
        """ Sets the role to give the user
        """
        if not ctx.message.author.guild_permissions.administrator:
            # Stop if not admin
            return
        self.settings_tbl.update_server(ctx.message.guild.id, role_id=int(role_id))

        ch = ctx.message.channel
        await ch.send('Role set')

    @staticmethod
    def parse_text(text, mention, guild, name):
        """ Parses text, replacing certain user with a user mention
        """
        text = text.replace('$MENTION$', mention)
        text = text.replace('$SERVER$', guild)
        text = text.replace('$NAME$', name)
        return text

    @welcome.command()
    async def text(self, ctx, *, text):
        """ Sets the welcome text that appears when a new member is added.
        """
        if not ctx.message.author.guild_permissions.administrator:
            # Stop if not admin
            return

        self.settings_tbl.update_server(ctx.message.guild.id, welcome_text=text)

        ch = ctx.message.channel
        await ch.send('Welcome text set. Example: ')
        await ch.send(self.parse_text(text, ctx.message.author.mention, ctx.message.guild.name, ctx.message.author.name))


    @welcome.command()
    async def ban(self, ctx, user_id):
        ch = ctx.message.channel
        server_id = ch.guild.id
        # Stop if not admin
        if not ctx.message.author.guild_permissions.administrator:
            return
        try:
            int(user_id)  # convert to int, to check if it's valid
        except:
            # return if input is not a valid number
            await ch.send('Please enter a user ID and NOT a mention or username *(numbers only)*.')
            return

        # if they aren't already banned, ban them
        result = self.bans_tbl.get_data(['user_id = %s' % user_id, 'server_id = %s' % server_id])
        if len(result) == 0:
            self.bans_tbl.insert_data({
                'user_id': user_id,
                'server_id': server_id,
                'timestamp': datetime.now().timestamp()
            })
            await ch.send('Welcome-banned `%s`. Begone!' % user_id)
            await ch.send('(Don\'t forget to remove their role if they still have it)')
        else: # else say they're already banned
            await ch.send('That user is already banned!')

    @welcome.command()
    async def unban(self, ctx, user_id):
        ch = ctx.message.channel
        server_id = ch.guild.id
        # Stop if not admin
        if not ctx.message.author.guild_permissions.administrator:
            return
        try:
            int(user_id)  # convert to int, to check if it's valid
        except:
            # return if input is not a valid number
            await ch.send('Please enter a user ID and NOT a mention or username *(numbers only)*.')
            return

        # if they're banned, then ban them
        result = self.bans_tbl.get_data(['user_id = %s' % user_id, 'server_id = %s' % server_id])
        if len(result) > 0:
            ''' 
                so it turned out there was no delete function in my supposedly CRUD API. Fix later
            '''
            timestamp = result[0][2]
            self.db.cursor.execute('delete from Bans where user_id = %s;' % user_id)
            self.db.connection.commit()
            await ch.send('Unbanning `%s`. They were banned at timestamp %s.' % (user_id, timestamp))
        else:
            await ch.send('That user isn\'t banned!')

    @welcome.command()
    async def list(self, ctx):
        ch = ctx.message.channel
        server_id = ch.guild.id
        result = self.bans_tbl.get_data(['server_id = %s' % server_id])
        print(result)
        await ch.send(result)


    @welcome.command()
    async def raidmode(self, ctx):
        ch = ctx.message.channel
        # Stop if not admin
        if not ctx.message.author.guild_permissions.administrator:
            return
        self.raidmode = not self.raidmode
        await ch.send('Raid mode set to: `%s`'%self.raidmode)