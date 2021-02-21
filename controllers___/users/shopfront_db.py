import sqlite3

class Database:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

    def build_table(self, table_name, fields):
        """ Takes a table name and list of fields to create a table """
        drop_table = "DROP TABLE IF EXISTS %s;" % table_name
        self.cursor.execute(drop_table)
        # create fields
        table_fields = ''
        for f in fields:
            table_fields += f+', '
        table_fields = table_fields[:-2]  # remove the final comma
        # create table
        create_table = "CREATE TABLE %s(%s); " % (table_name, table_fields)
        print(create_table)
        self.cursor.execute(create_table)
        self.connection.commit()

    def show_data(self, table_name):
        self.cursor.execute("SELECT * FROM %s;" % table_name)
        result = self.cursor.fetchall()
        return result

    def insert_data(self, table_name, data):
        """ Inserts a row from a dictionary object. """
        fields = ''
        values = ''
        for d in data:
            fields += ','+str(d)
            values += ','+str(data[d])
        fields = fields[1:]
        values = values[1:]
        sql_command = "INSERT INTO %s (%s) VALUES (%s);"%(table_name, fields, values)
        self.cursor.execute(sql_command)
        self.connection.commit()

    # returns current value of 1 Stock
    def get_value(self, val_type, item_id):
        self.cursor.execute("SELECT %s,id FROM Stock WHERE id = %s;" % (val_type, item_id))
        current_value = self.cursor.fetchone()[0]
        return current_value

    # changes value value for 1 user
    def update_value(self, val_type, item_id, amount):
        sql_command = "UPDATE Stock SET %s = %s WHERE id = %d;" % (val_type, amount, item_id)
        self.cursor.execute(sql_command)
        self.connection.commit()

    # adds an amount to value relative to current value
    def add_value(self, value_name, item_id, amount):
        # get current value
        item_id = int(item_id)
        current = self.get_value(value_name, item_id)
        new = current + amount

        # if it's negative, make it 0
        if new < 0:
            new = 0

        # set new value
        self.update_value(value_name, item_id, new)





    def get_latest_shop(self, user_id):
        """ Gets the users latest shopfront ID. """
        self.cursor.execute("SELECT id, time_created FROM Shopfronts WHERE user_id == %s ORDER BY id DESC;" % user_id)
        result = self.cursor.fetchone()
        return result

    def get_stocks(self, shop_id):
        self.cursor.execute("SELECT * FROM Stock WHERE shopfront_id == %s;" % shop_id)
        result = self.cursor.fetchall()
        return result



if __name__ == '__main__':
    db = Database('economy.db')
    # Shopfronts are unique instances of a Shop, tied to each player.
    db.build_table('Shopfronts', [
        'id INTEGER PRIMARY KEY',
        'user_id INTEGER',
        'type INTEGER',
        'time_created INTEGER'
    ])
    # Stock are tied to a Shopfront and represent the Stock of each item in the shop.
    db.build_table('Stock', [
        'id INTEGER PRIMARY KEY',
        'shopfront_id INTEGER',
        'item_id INTEGER',
        'current_stock INTEGER',
        'markup INTEGER',
        'cost INTEGER',
        'product INTEGER'
    ])
    '''
    db.insert_data('Shopfronts', {
        'user_id': '12345',
        'type': '0',
        'time_created': 1512123012.123
    })
    db.insert_data('Stock', {
        'shopfront_id': '12345',
        'markup': '0',
        'stock': 1512123012.123
    })'''