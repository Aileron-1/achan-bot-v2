import sqlite3
from datetime import datetime

class Database:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()
        self.default_asacoco = 0
        self.default_yubi = 10
        self.default_credits = 0
        self.currency = ['credits', 'asacoco', 'yubi']

        self.build_transactions()  # temp

    #creating table
    def rebuild_table(self):
        # drop table
        drop_table = "DROP TABLE IF EXISTS Users;"
        self.cursor.execute(drop_table)
        # create table
        create_table = """
        CREATE TABLE Users(
        uuid INTEGER PRIMARY KEY,
        credits INTEGER,
        asacoco INTEGER,
        yubi INTEGER,
        overdose INTEGER,
        factory INTEGER,
        lastdaily INTEGER
        ); """
        self.cursor.execute(create_table)
        self.connection.commit()

    def add_column(self, col_name, col_type):
        query = "ALTER TABLE Users ADD COLUMN %s %s"%(col_name, col_type)
        self.cursor.execute(query)
        self.connection.commit()

    def set_all(self, col_name, col_value):
        sql_command = "UPDATE Users SET %s = %s;" % (col_name, col_value)
        self.cursor.execute(sql_command)
        self.connection.commit()

    # for adding a new user to table
    def user_exists(self, user_id):
        self.cursor.execute("SELECT * FROM Users WHERE uuid = %s;" % user_id)
        result =  self.cursor.fetchall()
        if len(result) > 0:
            return True
        else:
            return False

    # checks if user exists, if not then add them
    def new_user(self, user_id):
        if not self.user_exists(user_id):
            user = [user_id, self.default_credits, self.default_asacoco, self.default_yubi, 0, 0, 0, 0, 0]
            sql_command = "INSERT INTO Users (uuid, credits, asacoco, yubi, overdose, factory, lastdaily, tests, regrows) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"
            print(sql_command)
            self.cursor.execute(sql_command, user)
            self.connection.commit()
            return True
        else:
            return False

    # returns current daily status of 1 user
    def get_daily(self, user_id):
        self.new_user(user_id)
        self.cursor.execute("SELECT lastdaily FROM Users WHERE uuid = %s;" % user_id)
        daily = self.cursor.fetchone()[0]
        return daily

    # set daily status
    def update_daily(self, user_id, timestamp):
        self.new_user(user_id)
        sql_command = "UPDATE Users SET lastdaily = %s WHERE uuid = %d;" % (timestamp, user_id)
        self.cursor.execute(sql_command)
        self.connection.commit()
    
    #showing table data
    def show_data(self):
        self.cursor.execute("SELECT * FROM Users;")
        result = self.cursor.fetchall()
        return result

    # returns current currency of 1 user
    def get_currency(self, curr_type, user_id):
        self.new_user(user_id)
        self.cursor.execute("SELECT %s FROM Users WHERE uuid = %s;" % (curr_type, user_id))
        current_currency = self.cursor.fetchone()[0]
        return current_currency

    # changes currency value for 1 user
    def update_currency(self, curr_type, user_id, amount):
        sql_command = "UPDATE Users SET %s = %s WHERE uuid = %d;" % (curr_type, amount, user_id)
        self.cursor.execute(sql_command)
        self.connection.commit()

    # adds an amount to currency relative to current currency
    def add_currency(self, curr_type, user_id, amount):
        # first, make them into a new user if they aren't already
        self.new_user(user_id)

        # get current currency
        user_id = int(user_id)
        current = self.get_currency(curr_type, user_id)
        new = current + amount

        # if it's negative, make it 0
        if new < 0:
            new = 0

        # set new currency
        self.update_currency(curr_type, user_id, new)

    def enough_currency(self, curr_type, user_id, amount):
        current = self.get_currency(curr_type, user_id)
        if current >= amount >= 0:
            return True
        else:
            return False

    def spend_currency(self, curr_type, user_id, amount):
        self.new_user(user_id)
        if self.enough_currency(curr_type, user_id, amount):
            self.add_currency(curr_type, user_id, 0-amount)
            return True
        else:
            return False

    def rank(self, curr_type):
        self.cursor.execute("SELECT uuid, %s FROM Users ORDER BY %s DESC;" % (curr_type, curr_type))
        result = self.cursor.fetchall()
        return result


    #creating janken table
    def make_janken(self):
        drop_table = "DROP TABLE IF EXISTS Janken;"
        self.cursor.execute(drop_table)
        # create table
        create_table = """
        CREATE TABLE Janken (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            type TEXT,
            result INTEGER,
            amount INTEGER,
            timestamp INTEGER
        ); """
        self.cursor.execute(create_table)
        self.connection.commit()

    # adds a janken entry for a user
    def new_janken(self, user_id, janken_type, result, amount):
        # first, make them into a new user if they aren't already
        #self.new_user(user_id)

        # add to table
        timestamp = datetime.now().timestamp()
        sql_command = "INSERT INTO Janken (user_id, type, result, amount, timestamp) VALUES (?,?,?,?,?);"
        self.cursor.execute(sql_command, [user_id, janken_type, result, amount, timestamp])
        self.connection.commit()

    # gets the score stats of a user
    def get_janken_score(self, user_id, janken_type):
        score = {'loss':0, 'draw':0, 'win':0}
        i = -1
        for s in score:
            sql_command = "SELECT COUNT(*) FROM Janken WHERE user_id = %s AND type = \'%s\' AND result = %s;"%(user_id, janken_type, i)
            self.cursor.execute(sql_command)
            result = self.cursor.fetchone()[0]
            print(result)
            score[s] = result
            i += 1
        return score

    # get the total amount amount gained (not ) for user
    def get_janken_gains(self, user_id, janken_type='regular'):
        sql_command = "SELECT SUM(amount) FROM Janken WHERE user_id = %s AND type = \'%s\' AND result = 1"%(user_id, janken_type)
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()[0]

    def rank_janken_gains(self, winloss=1):
        sql_command = "SELECT user_id, SUM(amount) FROM Janken WHERE result = %s GROUP BY user_id ORDER BY SUM(amount) DESC"%winloss
        self.cursor.execute(sql_command)
        return self.cursor.fetchall()

    # rank by number of wins
    def janken_rank(self, janken_type):
        sql_command = "SELECT user_id, COUNT(*) FROM Janken WHERE type = \'%s\' AND result = 1 GROUP BY user_id ORDER BY COUNT(*) DESC"%janken_type
        self.cursor.execute(sql_command)
        return self.cursor.fetchall()

    # rank by superchats given, but not when they send to themselves
    def simp_rank(self):
        # select rows which are superchats and aren't to self
        sql_command = "SELECT from_user, SUM(amount) FROM Transactions WHERE note = 'superchat' AND to_user != from_user GROUP BY from_user ORDER BY SUM(amount) DESC"
        self.cursor.execute(sql_command)
        results = self.cursor.fetchall()
        return results

    # rank by superchats received, but not when they send to themselves
    def simp_rank_received(self):
        # select rows which are superchats and aren't to self
        sql_command = "SELECT to_user, SUM(amount) FROM Transactions WHERE note = 'superchat' AND to_user != from_user GROUP BY to_user ORDER BY SUM(amount) DESC"
        self.cursor.execute(sql_command)
        results = self.cursor.fetchall()
        return results


    # Transactions
    def build_transactions(self):
        # create table
        create_table = """
        CREATE TABLE IF NOT EXISTS Transactions(
            from_user INTEGER,
            to_user INTEGER,
            type TEXT,
            amount INTEGER,
            timestamp INTEGER,
            note TEXT
        ); """
        self.cursor.execute(create_table)
        self.connection.commit()

    def new_transaction(self, from_user, to_user, curr_type, amount, note):
        # add to table
        print(from_user, to_user, curr_type, amount, note)
        timestamp = datetime.now().timestamp()
        sql_command = "INSERT INTO Transactions (from_user, to_user, type, amount, timestamp, note) VALUES (?,?,?,?,?,?);"
        self.cursor.execute(sql_command, [from_user, to_user, curr_type, amount, timestamp, note])
        self.connection.commit()



if __name__ == '__main__':
    db = Database('users.db')
    db.make_janken()
    '''
    db.new_janken(1234, 0, -1, -200)
    db.new_janken(1234, 0, -1, -200)
    db.new_janken(1234, 0, 0, 200)
    db.new_janken(1234, 0, 1, 200)
    db.new_janken(1234, 0, -1, -200)
    db.new_janken(1234, 0, 1, 200)
    print(db.get_janken_score(1234, 0))
    print(db.get_janken_gains(1234, 0))'''



