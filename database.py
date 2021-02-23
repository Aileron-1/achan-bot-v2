import mysql.connector
import datetime

class Database:
    def __init__(self, *, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user, 
            password=password,
            database=database
            )
        self.cursor = self.connection.cursor(dictionary=True)

    def create_table(self, table_name, columns):
        """ Takes a table name and list of columns to create a table
        """
        # create columns
        table_columns = 'id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT'
        for f in columns:
            table_columns += ', '+f
        table_columns = table_columns
        # create table
        statement = "CREATE TABLE IF NOT EXISTS %s(%s); " % (table_name, table_columns)
        self.cursor.execute(statement)
        self.connection.commit()
        return self.get_table(table_name)

    def reset_table(self, table_name):
        """ Simply drops the table if it exists.
        """
        print('Dropping table %s!'%table_name)
        drop_table = "DROP TABLE IF EXISTS %s;" % table_name
        self.cursor.execute(drop_table)

    def get_table(self, table_name):
        table = Table(self, table_name)
        return table


class Table:
    def __init__(self, db, table_name):
        self.db = db
        self.table_name = table_name
        self.columns = self.db.cursor.description  # safe or coincidence? # what's this doing here anyway?

    def columns(self):
        return self.rows[0].keys()  # janky method?
        # "PRAGMA table_info(table_name);" works without rows

    def find(self, item_id):
        """ Gets a row by id 
        """
        return self.get('id', item_id)

    def get(self, where={}):
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
        self.db.cursor.execute(query, params)
        result = self.db.cursor.fetchall()
        print(params, query)
        return result

    def query(self, query, params=[]):
        self.db.cursor.execute(query, params)
        result = self.db.cursor.fetchall()
        return result

    def insert(self, data):
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
        self.db.cursor.execute(sql_command, params)
        self.db.connection.commit()

    def insert_many(self, datas):
        for data in datas:
            self.insert(data)

                    # this should be part of model

    def update(self, item_id, val_type, amount):
        sql_command = "UPDATE '%s' SET '%s' = %s WHERE id = %s;" % (self.table_name, val_type, '%s', '%s')
        self.db.cursor.execute(sql_command, (amount, item_id))
        self.db.connection.commit()


                    # this should be part of model

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

    db = Database(
        host='128.199.153.229',
        user='achan',
        password='Adk5+P5L@p&dy^G^',
        database='achan'
        )
    print(db)

    db.reset_table('testable')
    ttb = db.create_table('testable',[
        'user BIGINT UNSIGNED',
        'words TEXT'
        ])
    ts = ttb.insert({
        'user': 1919191919,
        'words': 'test words here'
        })
    ttb.insert_many([
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

    print(ttb.get())

    print(ttb.get({'user': 1919191919}))
