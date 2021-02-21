class Farmstead:
    """ Controller abstraction of a player's farm.
        Has one owner(user_id), contains many plots.
    """
    def __init__(self, f_id, user_id, name, size, xp):
        self.id = f_id
        self.owner = user_id
        self.name = name
        self.size = size
        self.xp = xp
        self.plots = []

    def add_plot(self, plot):
        """ Adds a plot object to this farm.
            Also sets the owner of the plot to this farm.
        """
        self.plots.append(plot)
        plot.farm = self

    def get_emote(self, selection=None):
        side1 = '<:side_L:702525671234338838>'
        side2 = '<:side_R:702525649717559348>'
        s = side1+''
        i = 0
        for p in self.plots:
            if i == selection:
                s += ''#' '
            s += p.get_current_emote()
            if i == selection:
                s += ''#' '
            i += 1
        s += side2
        return s
