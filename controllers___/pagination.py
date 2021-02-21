import asyncio
from .misc import emote

class Pagination:
    def __init__(self, bot, ctx, pages):
        self.bot = bot
        self.ctx = ctx
        self.pages = pages
        self.page_no = 0
        self.page_max = len(pages)
        self.embed_message = None
        self.timeout = 60.0

    async def start(self):
        """Starts the messages and listening for reactions
        """
        ch = self.ctx.message.channel
        # Send page message
        emb = self.get_page()
        self.embed_message = await ch.send(embed=emb)

        # Add reactions
        reacts = [emote['left'],emote['right']]
        for r in reacts:
            await self.embed_message.add_reaction(r)

        while True:
            def react_check(reaction, user):
                if user == self.embed_message.author:
                    return
                return str(reaction.emoji) in reacts and reaction.message.id == self.embed_message.id
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=self.timeout, check=react_check)
            except asyncio.TimeoutError:
                await self.embed_message.clear_reactions()
                break
            else:
                if str(reaction.emoji) == emote['left']:
                    await self.paginate(-1)
                if str(reaction.emoji) == emote['right']:
                    await self.paginate(1)

    def get_page(self):
        emb = self.pages[self.page_no]
        emb.set_footer(text='Page %s/%s'%(self.page_no+1, self.page_max))
        return emb

    async def paginate(self, amount):
        self.page_no += amount
        # modulo the page so it stays within range
        self.page_no = self.page_no % self.page_max
        emb = self.get_page()
        await self.embed_message.edit(embed=emb)