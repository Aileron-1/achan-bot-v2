import asyncio
import aiomysql
import datetime

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    async def connect(self, *, loop, host, user, port=3306, password, database):
        self.connection = await aiomysql.connect(
            loop=loop,
            host=host,
            port=port,
            user=user, 
            password=password,
            db=database
            )
        self.cursor = await self.connection.cursor()
        return self.connection

    async def create_table(self, table_name, columns):
        """ Takes a table name and list of columns to create a table
        """
        # create columns
        table_columns = 'id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT'
        for f in columns:
            table_columns += ', '+f
        table_columns = table_columns
        # create table
        statement = "CREATE TABLE IF NOT EXISTS %s(%s); " % (table_name, table_columns)
        await self.cursor.execute(statement)
        await self.connection.commit()
        return await self.get_table(table_name)

    async def reset_table(self, table_name):
        """ Simply drops the table if it exists.
        """
        print('Dropping table %s!'%table_name)
        drop_table = "DROP TABLE IF EXISTS %s;" % table_name
        await self.cursor.execute(drop_table)

    async def get_table(self, table_name):
        table = Table(self, table_name)
        return table


class Table:
    def __init__(self, db, table_name):
        self.db = db
        self.table_name = table_name
        self.columns = self.db.cursor.description  # safe or coincidence? # what's this doing here anyway?

    async def columns(self):
        return self.rows[0].keys()  # janky method?
        # "PRAGMA table_info(table_name);" works without rows

    async def find(self, item_id):
        """ Gets a row by id 
        """
        return self.get('id', item_id)

    async def get(self, where={}):
        """ Fetches data. Takes in a list of arguments to use with WHERE.
        """
        print('getting data from %s' % self.table_name)
        # only supports = operator for now
        # Error on non dict
        if type(where) != dict:
            raise Exception('Search object must be a dict.')
        # Create the query list and parameters
        where_string = ''
        params = []
        if where:
            where_string = ' WHERE 0 = 0'
            for s in where:
                where_string += ' AND %s = %s' % (s, '%s')
                params.append(where[s])
        query = "SELECT * FROM %s%s;" % (self.table_name, where_string)
        await self.db.cursor.execute(query, params)
        result = await self.db.cursor.fetchall()
        print(params, query)
        return result

    async def query(self, query, params=[]):
        await self.db.cursor.execute(query, params)
        result = await self.db.cursor.fetchall()
        return result

    async def insert(self, data):
        """ Inserts a row from a dictionary object.
        """
        fields = ''
        values = ''
        params = []
        for d in data:
            fields += ',%s' % str(d)
            values += ',%s'
            params.append(str(data[d]))
        print(params)
        fields = fields[1:]  # Remove first comma
        values = values[1:] 
        sql_command = "INSERT INTO %s (%s) VALUES (%s);"%(self.table_name, fields, values)
        print(sql_command)
        await self.db.cursor.execute(sql_command, params)
        await self.db.connection.commit()

    async def insert_many(self, datas):
        for data in datas:
            await self.insert(data)

                    # this should be part of model

    async def update(self, item_id, val_type, amount):
        sql_command = "UPDATE %s SET %s = %s WHERE id = %s;" % (self.table_name, val_type, '%s', '%s')
        print(sql_command)
        await self.db.cursor.execute(sql_command, (amount, item_id))
        await self.db.connection.commit()


                    # this should be part of model

    # adds an amount to value relative to current value
    async def add_value(self, value_name, item_id, amount, *, minimum=0):
        # get current value
        item_id = int(item_id)
        current = await self.get_value(value_name, item_id)
        new = current + amount
        # stop if it's below the minimum
        if minimum is not None:
            if new < minimum:
                new = minimum
        # set new value
        await self.update_value(item_id, value_name, new)

if __name__ == '__main__':
    async def test(loop):
        db = Database()
        await db.connect(
            loop=loop,
            host='165.22.243.124',
            user='achan',
            password='Adk5+P5L@p&dy^G^',
            database='HoloRes'
            )
        print(db)

        await db.reset_table('testable')
        ttb = await db.create_table('testable',[
            'user BIGINT UNSIGNED',
            'words TEXT'
            ])
        ts = await ttb.insert({
            'user': 1919191919,
            'words': 'test words here'
            })
        await ttb.insert_many([
                {
                'user': 1919191912,
                'words': 'ljkasfkljafklj'
                },{
                'user': 1919191913,
                'words': 'words here test'
                },{
                'user': 1919191914,
                'words': 'itolife'
                },
            ])
        
        res = await ttb.get()

        print(res)

        await ttb.update(1, 'words','updated words')

        print(res)

        print(await ttb.get({'user': 1919191919}))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test(loop))