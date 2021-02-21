""" Database API for controller->db use.
Review: not efficient, should have less db calls
"""
from cogs.database import Database
import datetime

class FarmAPI:
    def __init__(self, db):
        self.db = Database(db)
        self.farms = self.build_farms_table()
        self.plots = self.build_crops_table()
        self.actions = self.build_actions_table()
        self.default_farm_size = 1

    def build_farms_table(self):
        return self.db.build_table('Farms', [
            'id INTEGER PRIMARY KEY',
            'name TEXT',
            'user_id INTEGER',
            'time_created INTEGER',
            'size INTEGER',
            'xp INTEGER'
        ])

    def build_crops_table(self):
        return self.db.build_table('Plots', [
            'id INTEGER PRIMARY KEY',
            'farm_id INTEGER',
            'crop_id INTEGER',
            'time_planted INTEGER'
        ])

    def build_actions_table(self):
        """ The Actions table logs every farm-related transaction that is made.
        Track actions such as harvesting, growing, new farm, sells.
        """
        return self.db.build_table('Actions', [
            'id INTEGER PRIMARY KEY',
            'farm_id INTEGER',
            'plot_id INTEGER',
            'amount INTEGER',
            'note TEXT',
            'time INTEGER'
        ])

    def user_has_farm(self, user_id):
        check = self.get_farm(user_id)
        print('has farm?:', check is not None)
        if check is not None:
            return True
        else:
            return False

    def new_farmer(self, user_id):
        """ Checks if the user is a new farmer. Gives them a basic farm if so.
            Checks by checking whether the search is empty.
        """
        if not self.user_has_farm(user_id):
            # Make them a new farm
            return self.make_farm(user_id)

    def make_farm(self, user_id):
        """ Initialises a size 1 farm.
            Creates a plot to go with it using check_farm.
        """
        self.farms.insert_data({
            'user_id': int(user_id),
            'name': 'Farmstead',
            'time_created': datetime.datetime.now().timestamp(),
            'size': self.default_farm_size,
            'xp': 0
        })
        farm_id = self.get_farm(user_id)['id']
        self.add_transaction(farm_id, 'made farm')
        self.check_farm(farm_id)

    def make_plot(self, farm_id):
        """ Adds a plot to a farm.
        """
        self.plots.insert_data({
            'farm_id': farm_id,
            'crop_id': -1,
            'time_planted': -1
        })

    def check_farm(self, farm_id):
        """ Checks if a farm has enough plots to reach its max plots (size). If not, it will add a new one.
            If it finds a farm has more plots than its max plots, it will destroy the last one. (by setting its farm id to -1)
        """
        farm_plots =  self.plots.get_data({'farm_id': int(farm_id)})
        max_plots = self.farms.get_data({'id': int(farm_id)})[0]['size']
        # Add more plots if there are not enough
        while len(farm_plots) < max_plots:
            print('not enough plots. making more (%s/%s)'%(len(farm_plots), max_plots))
            self.make_plot(farm_id)
            farm_plots =  self.plots.get_data({'farm_id': int(farm_id)})
        if len(farm_plots) > max_plots:  # To do: disable plots that exceed limit
            print('plots over max!')

    def get_farm(self, user_id):
        """ Gets farm_id using user_id.
            Confirm if is farm row or just ID, later. This should really return a Farm obj
        """
        try:
            farm_id = self.farms.get_data({'user_id': int(user_id)})[0]
        except:
            farm_id = None
        return farm_id

    def get_plots(self, farm_id):
        """ Gets plots of a farm using farm_id.
            Gets an amount = to the farm's max plots.
        """
        self.check_farm(farm_id)
        farm_plots = self.plots.get_data({'farm_id': int(farm_id)})
        max_plots = self.farms.get_data({'id': int(farm_id)})[0]['size']
        limited_plots = []
        for i in range(max_plots):
            limited_plots.append(farm_plots[i])
        return farm_plots

    def get_plot(self, plot_id):
        """ Gets the row object of a specific plot.
        """
        if type(plot_id) != int:
            raise Exception('plot_id must be a integer!')
        try:
            return self.plots.get_data({'id': int(plot_id)})[0]
        except:
            return None

    def has_crop(self, plot_id):
        """ Checks if the plot has a crop or not.
        """
        plot = self.get_plot(plot_id)
        if plot['crop_id'] == -1:
            return False
        else:
            return True

    def plant_crop(self, plot_id, crop_id):
        """ Sets a plot's crop_id and initialises its plant_time.
            Errors if plot already has a crop.
        """
        plot = self.get_plot(plot_id)
        if not self.has_crop(plot_id):
            self.plots.update_value(plot_id, 'crop_id', crop_id)
            self.plots.update_value(plot_id, 'time_planted', datetime.datetime.now().timestamp())
            print('planted')
            self.add_transaction(plot['farm_id'], 'plant success', crop_id, plot_id=plot_id)
            return True
        else:
            self.add_transaction(plot['farm_id'], 'plant fail', crop_id, plot_id=plot_id)
            print('trying to plant on an occupied plot!')
            return False

    def harvest_crop(self, plot_id, reuse=False):
        """ Attempt to harvest a crop.
            Sets the plot's crop_id and crop_planted to -1 (none).
            Returns False if plot doesn't have a crop.
        """
        plot = self.get_plot(plot_id)
        if plot['crop_id'] != -1:
            # check if grown here. later
            # api has no access to crop data... which means grow_time and reusable is unavailable.... later
            # Don't reset if reusable
            if reuse:
                self.plots.update_value(plot_id, 'time_planted',  datetime.datetime.now().timestamp())
                self.add_transaction(plot['farm_id'], 'harvest reusable', plot['crop_id'], plot_id=plot_id)
                print('reusably harvested %s from %s' % (plot['crop_id'], plot['id']))
            else:
                self.plots.update_value(plot_id, 'crop_id', -1)
                self.plots.update_value(plot_id, 'time_planted', -1)
                self.add_transaction(plot['farm_id'], 'harvest consumable', plot['crop_id'], plot_id=plot_id)
                print('harvested %s from %s'%(plot['crop_id'], plot['id']))
            # Set farm's highest_harvested value if it's higher than before
            #if self.farms.get_data({'id': plot['farm_id']})[0]['highest_crop_harvested'] < plot['crop_id']:
            #    self.farms.update_value(plot['farm_id'], 'highest_crop_harvested', plot['crop_id'])
            return True
        else:
            print('trying to harvest empty crop')
            return False

    def remove_crop(self, plot_id):
        """ Sets target crop_id and time_planted to -1.
        """
        plot = self.get_plot(plot_id)
        if plot['crop_id'] != -1:
            # check if grown here.
            self.plots.update_value(plot_id, 'crop_id', -1)
            self.plots.update_value(plot_id, 'time_planted', -1)
            self.add_transaction(plot['farm_id'], 'sell crop', plot['crop_id'], plot_id=plot_id)
            print('removed crop of %s'%plot['id'])
        else:
            print('trying to harvest empty crop')

    def get_farm_and_plots(self, user_id):
        """ Returns a user's farm and plots.
        """
        farm = self.get_farm(user_id)
        plots = self.get_plots(farm['id'])
        return farm, plots

    def upgrade_farm(self, user_id):
        """ Increases a user's farm size.
        """
        print('Upgrading %s\'s farm.'%user_id)
        # Get the target farm and it's current size
        farm = self.get_farm(user_id)
        new_size = farm['size'] + 1
        # Add limits
        new_size = max(1, min(5, new_size))
        # Apply changes
        self.farms.update_value(farm['id'], 'size', new_size)
        self.check_farm(farm['id'])
        self.add_transaction(farm['id'], 'upgrade', new_size)

    def add_transaction(self, farm_id, note, amount=-1, *, plot_id=-1):
        self.actions.insert_data({
            'farm_id': farm_id,
            'note': note,
            'amount': amount,
            'plot_id': plot_id,
            'time': datetime.datetime.now().timestamp()
        })

    def check_if_farm_planted(self, farm_id, crop_id):
        """ Checks if a farm has planted a crop or not. Boolean.
        """
        query = "SELECT * FROM Actions WHERE note LIKE 'harvest%' AND farm_id = ? AND amount = ?;"
        params = [farm_id, crop_id]
        results = self.actions.query(query, params)
        if crop_id == 0:  # Return true if the crop is 0
            return True
        if len(results) > 0:
            return True
        else:
            return False

    def eligible_crops(self, crop_data, farm_id, ineligible=False):
        """ Get a list of a farm's eligible crops.
        Can also return ineligible ones
        """
        crops = []
        non_crops = []
        for c in crop_data:
            if self.check_if_farm_planted(farm_id, c.prerequisite):
                crops.append(c)
            else:
                non_crops.append(c)
        if ineligible:
            return non_crops
        else:
            return crops

    def will_unlock(self, crop_data, farm_id, crop_id):
        """ Returns the crops that growing a specific crop would unlock.
        """
        unlocks = []
        # For every crop
        for c in crop_data:
            # See if it's the crop being grown
            if c.prerequisite == crop_id:
                # Check if its prereq has been grown. if not, then add it

                # If it'll be the first time planting this crop, then this will unlock something
                if not self.check_if_farm_planted(farm_id, c.prerequisite):
                    unlocks.append(c)
        return unlocks

    def add_xp(self, farm_id, amount):
        self.farms.add_value('xp', farm_id, amount)

if __name__ == '__main__':
    db = Database('test.db')
    api = FarmAPI(db)
    usr = 12345
    usr2 = 12345

    # new user tests
    api.new_farmer(usr)
    farm, plots = api.get_farm_and_plots(usr)
    for f in farm.keys():
        print(f, farm[f])
    for p in plots:
        for v in p.keys():
            print(v, p[v])

    # test upgrading
    print(api.get_farm(usr)['size'])
    api.upgrade_farm(usr)
    print(api.get_farm(usr)['size'])

    # test growing
    farm, plots = api.get_farm_and_plots(usr)
    print(plots[1]['id'], plots[1]['crop_id'], plots[1]['time_planted'])
    api.plant_crop(plots[1]['id'], 2)
    farm, plots = api.get_farm_and_plots(usr)
    print(plots[1]['id'], plots[1]['crop_id'], plots[1]['time_planted'])

    for p in plots:
        for v in p.keys():
            print(v, p[v])

    # test growing on existing
    api.plant_crop(plots[1]['id'], 112)
    farm, plots = api.get_farm_and_plots(usr)
    print(plots[1]['id'], plots[1]['crop_id'], plots[1]['time_planted'])
    # test harvesting empty
    api.harvest_crop(plots[0]['id'])
    print(plots[0]['id'], plots[0]['crop_id'], plots[0]['time_planted'])
    # test harvest grown
    api.harvest_crop(plots[1]['id'])
    print(plots[1]['id'], plots[1]['crop_id'], plots[1]['time_planted'])



