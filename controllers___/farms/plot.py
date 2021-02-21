import datetime

class Plot:
    """ Controller abstraction of a plot in a farm.
        Contains a Crop, and must be in 1 Farmstead.
    """
    def __init__(self, p_id, time_planted, crop=None):
        self.farm = None
        self.id = p_id
        self.time_planted = time_planted # The time it was planted/the last time it was harvested, as timestamp
        self.crop = crop # The type of crop in the plot. Can be None

    def since_last_harvest(self):
        if self.time_planted:
            return datetime.datetime.now() - datetime.datetime.fromtimestamp(self.time_planted)

    def time_until_ready(self):
        return self.crop.grow_time - self.since_last_harvest().total_seconds()

    def ready(self):
        """ Checks whether this crop has grown and is ready to harvest.
        """
        if self.crop is None:
            print('checking nonexistent crop')
            return None
        else:
            return self.time_until_ready() <= 0

    def get_current_emote(self):
        if self.crop is not None:
            if self.ready():
                return self.crop.emoji[2]
            else:
                return self.crop.emoji[0]
        else:
            return '<:chi:702467355288010802>'

    def plant(self, crop):
        """ Plants a new crop on this plot.
            Updates the farms_db entry after the changes.
        """
        self.crop = crop
        self.time_planted = datetime.datetime.now().timestamp()

    def harvest(self):
        """ Attempt to harvest the crop on this plot.
            Returns whether it succeeded or not.
        """
        if self.ready():
            # if crop is not reusable, reset the self.crop to None
            if self.crop.reusable:
                self.time_planted = datetime.datetime.now().timestamp()
            else:
                self.fallow()
            return True
        else:
            return False

    def fallow(self):
        """ Reset crop on this plot.
        """
        self.crop = None
        self.time_planted = -1
        return True

