
class Migration():
    def __init__(self, db):
        self.db = db

    async def up(self):
        await self.db.create_table('stock',[
            'shopfront_id INTEGER',
            'item_id INTEGER',
            'current_stock INTEGER',
            'markup INTEGER',
            'cost INTEGER',
            'product INTEGER'
            ])
        
    async def down(self):
        await self.db.drop_table('stock')
        