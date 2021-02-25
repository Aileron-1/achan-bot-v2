
class Migration():
    def __init__(self, db):
        self.db = db

    async def up(self):
        await self.db.create_table('dailies',[
            'user_id BIGINT UNSIGNED',
            'credits INTEGER',
            'asacoco INTEGER',
            'yubi INTEGER',
            'timestamp INTEGER'
            ])
        
    async def down(self):
        await self.db.drop_table('dailies')
        