
class Migration():
    def __init__(self, db):
        self.db = db

    async def up(self):
        await self.db.create_table('shopfronts',[
            'user_id INTEGER',
            'type INTEGER',
            'time_created INTEGER'
            ])
        
    async def down(self):
        await self.db.drop_table('shopfronts')
        