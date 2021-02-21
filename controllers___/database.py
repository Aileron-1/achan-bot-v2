import sqlite3
import datetime

class Database:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def build_table(self, table_name, columns):
        """ Takes a table name and list of columns to create a table
        """
        # create columns
        table_columns = ''
        for f in columns:
            table_columns += f+', '
        table_columns = table_columns[:-2]  # remove the final comma
        # create table
        create_table = "CREATE TABLE IF NOT EXISTS %s(%s); " % (table_name, table_columns)
        self.cursor.execute(create_table)
        self.connection.commit()
        return self.get_table(table_name)

    def reset_table(self, table_name):
        """ Simply drops the table.
        """
        print('Dropping table %s!'%table_name)
        drop_table = "DROP TABLE IF EXISTS %s;" % table_name
        self.cursor.execute(drop_table)

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
        self.columns = self.db.cursor.description  # safe or coincidence? # what's this doing here anyway?

    def get_columns(self):
        return self.rows[0].keys()  # janky method?
        # "PRAGMA table_info(table_name);" works without rows

    def get_data(self, where=None):
        """ Fetches data. Takes in a list of arguments to use with WHERE.
            If WHERE isn't a list, wrap it inside one.
        """
        if where is None:
            where = {}
        self.db.connection.row_factory = sqlite3.Row
        # only supports = operator for now
        # Error on non dict
        if type(where) != dict:
            raise Exception('Search object must be a dict.')
        # Create the query list and parameters
        where_string = ''
        params = []
        for s in where:
            where_string += ' AND %s = ?'%s
            params.append(where[s])
        query = "SELECT * FROM %s WHERE 0 = 0%s;" % (self.table_name, where_string)
        self.db.cursor.execute(query, params)
        result = self.db.cursor.fetchall()
        return result

    def query(self, query, params=[]):
        self.db.cursor.execute(query, params)
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

    def get_value(self, value_name, item_id):  # this is stupid
        sql_command = "SELECT %s, id FROM %s WHERE id = %s;" % (value_name, self.table_name, item_id)
        self.db.cursor.execute(sql_command)
        current_value = self.db.cursor.fetchone()[0]
        return current_value

    def update_value(self, item_id, val_type, amount):
        sql_command = "UPDATE '%s' SET '%s' = ? WHERE id = ?;" % (self.table_name, val_type)  # can this be entirely '?' style?
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
        self.update_value(item_id, value_name, new)

if __name__ == '__main__':
    db = Database('test.db')
    db.reset_table('Farms')
    db.build_table('Farms', [
        'id INTEGER PRIMARY KEY',
        'name TEXT',
        'user_id INTEGER',
        'time_created INTEGER'
    ])
    tbl = db.get_table('Farms')
    tbl.insert_data({
        'user_id': 12345,
        'time_created': datetime.datetime.now().timestamp()
    })
    tbl.insert_data({
        'user_id': 54321,
        'time_created': datetime.datetime.now().timestamp()
    })
    print(tbl.get_data())


    db.reset_table('Plots')
    db.build_table('Plots', [
        'id INTEGER PRIMARY KEY',
        'farm_id INTEGER',
        'crop_id INTEGER',
        'crop_planted INTEGER'
    ])

    tbl = db.get_table('Plots')
    tbl.insert_data({
        'farm_id': 1,
        'crop_id': 3,
        'crop_planted': datetime.datetime.now().timestamp()
    })
    tbl = db.get_table('Plots')
    tbl.insert_data({
        'farm_id': 1,
        'crop_id': 2,
        'crop_planted': datetime.datetime.now().timestamp()
    })
    tbl = db.get_table('Plots')
    tbl.insert_data({
        'farm_id': 2,
        'crop_id': 1,
        'crop_planted': datetime.datetime.now().timestamp()
    })
    print(tbl.get_data())
    print(type(tbl.get_data()))


