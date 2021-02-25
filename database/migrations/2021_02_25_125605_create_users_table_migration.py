
class Migration():
    def __init__(self, db):
        self.db = db

    async def up(self):
        await self.db.create_table('users',[
            'uuid BIGINT UNSIGNED',
            'credits INTEGER',
            'asacoco INTEGER',
            'yubi INTEGER',
            'overdose INTEGER',
            'tests INTEGER',
            'regrows INTEGER'
            ])
        
    async def down(self):
        await self.db.drop_table('users')
        