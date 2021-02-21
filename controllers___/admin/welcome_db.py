import sqlite3
import datetime

class Database:
    def __init__(self, path):
        self.connection = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.cursor = self.connection.cursor()
        self.connection.row_factory = sqlite3.Row

    def build_table(self, table_name, columns):
        """ Takes a table name and list of columns to create a table """
        drop_table = "DROP TABLE IF EXISTS %s;" % table_name
        self.cursor.execute(drop_table)
        # create columns
        table_columns = ''
        for f in columns:
            table_columns += f+', '
        table_columns = table_columns[:-2]  # remove the final comma
        # create table
        create_table = "CREATE TABLE %s(%s); " % (table_name, table_columns)
        print(create_table)
        self.cursor.execute(create_table)
        self.connection.commit()

        return self.get_table(table_name)

    def get_table(self, table_name):
        self.cursor.execute('select * from %s' % table_name)
        rows = self.cursor.fetchall()
        table = Table(self, table_name, rows)
        return table


class Table:
    def __init__(self, db, table_name, rows):
        self.db = db
        self.table_name = table_name
        self.rows = rows
        self.columns = self.db.cursor.description  # safe or coincidence?

    def get_columns(self):
        return self.rows[0].keys()  # janky method?

    def get_data(self, where=None):
        """ Fetches data. Takes in a list of arguments to use with WHERE.
        """
        if where is None:
            where = []
        where_string = ''
        if len(where) > 0:
            where_string = ' WHERE 0=0'  # hack
            for s in where:
                where_string += ' AND %s'%s
        query = "SELECT * FROM %s%s;" % (self.table_name, where_string)
        self.db.cursor.execute(query)
        result = self.db.cursor.fetchall()
        return result

    def insert_data(self, data):
        """ Inserts a row from a dictionary object.
        """
        fields = ''
        values = ''
        for d in data:
            fields += ',%s' % str(d)
            values += ',\'%s\'' % str(data[d])
        fields = fields[1:]
        values = values[1:]
        sql_command = "INSERT INTO %s (%s) VALUES (%s);"%(self.table_name, fields, values)
        self.db.cursor.execute(sql_command)
        self.db.connection.commit()

    def get_value(self, val_type, item_id):
        sql_command = "SELECT %s,id FROM %s WHERE id = %s;" % (self.table_name, val_type, item_id)
        print(sql_command)
        self.db.cursor.execute(sql_command)
        current_value = self.db.cursor.fetchone()[0]
        return current_value

    def update_value(self, val_type, item_id, amount):
        sql_command = "UPDATE '%s' SET %s = ? WHERE id = ?;" % (self.table_name, val_type)
        print(sql_command)
        self.db.cursor.execute(sql_command, (amount, item_id))
        self.db.connection.commit()

    # adds an amount to value relative to current value
    def add_value(self, value_name, item_id, amount, *, minimum=0):
        # get current value
        item_id = int(item_id)
        current = self.get_value(value_name, item_id)
        new = current + amount
        # stop if it's below the minimum
        if minimum is not None:
            if new < minimum:
                new = minimum
        # set new value
        self.update_value(value_name, item_id, new)



    #...

    def new_server(self, server_id):
        """ Adds a new server with default settings if it doesn't already exist.
        """
        # Check if doesn't exist already
        res = self.get_data(['server_id = %s'%server_id])
        if len(res) > 0:
            print('server exists')
        else:
            print('server not exists')
            self.insert_data({
                'server_id': server_id,
                'channel_id': 0,
                'role_id': 0,
                'welcome_text': 'Default welcome message. Welcome **$NAME$**.',
                'phrase': 'WASSHOI'
            })

    def update_server(self, server_id, *, ch_id=None, role_id=None, welcome_text=None):
        self.new_server(server_id)
        print('updating server values', ch_id, role_id, welcome_text)
        server_item_id =  self.get_data(['server_id = %s'%server_id])[0][0]  # Get server row id
        if ch_id is not None:
            self.update_value('channel_id', server_item_id, ch_id)
        if role_id is not None:
            self.update_value('role_id', server_item_id, role_id)
        if welcome_text is not None:
            self.update_value('welcome_text', server_item_id, welcome_text)

    def get_settings(self, server_id):
        self.new_server(server_id)
        res = self.get_data(['server_id = %s' % server_id])[0]
        return {'channel_id': res[2], 'role_id': res[3], 'welcome_text': res[4]}

    def already_welcomed(self, server_id, user_id):
        """ Check if user has already been welcomed in this server.
        """
        # Check if doesn't exist already
        res = self.get_data(['user_id = %s'%user_id, 'server_id = %s'%server_id])
        if len(res) > 0:
            print('welcome exists', server_id, user_id)
            return True
        else:
            print('welcome not exists', server_id, user_id)
            return False

    def new_welcome(self, server_id, user_id):
        """ Make a new welcome using user id and server id.
        """
        self.insert_data({
            'server_id': server_id,
            'user_id': user_id,
            'timestamp': datetime.datetime.now().timestamp()
        })


if __name__ == '__main__':
    db = Database('test.db')
    # Shopfronts are unique instances of a Shop, tied to each player.
    db.build_table('Settings', [
        'id INTEGER PRIMARY KEY',
        'server_id INTEGER',
        'channel_id INTEGER',
        'role_id INTEGER',
        'welcome_text TEXT',
        'phrase TEXT'
    ])

    tbl = db.get_table('Settings')
    tbl.insert_data({
        'server_id': 123,
        'channel_id': 312312,
        'role_id': 1239090,
        'welcome_text': 'default stuff'
    })
    tbl.insert_data({
        'server_id': 345,
        'channel_id': 475745,
        'role_id': 987654231,
        'welcome_text': 'default2 stuff!!!!!'
    })
    print(tbl.get_data())
    tbl.new_server(987)
    print(tbl.get_data())
    tbl.update_server(987,ch_id=67676767)
    print(tbl.get_data(['channel_id=67676767']))
    print(tbl.get_data())
    print(tbl.get_settings(987))

    db.build_table('Welcomes', [
        'id INTEGER PRIMARY KEY',
        'user_id INTEGER',
        'server_id INTEGER',
        'timestamp INTEGER'
    ])
