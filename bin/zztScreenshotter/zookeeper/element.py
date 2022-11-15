from zookeeper import constants


class Element(object):
    def __init__(self, id, color=15, stat_idx=None, tile=None, character=None):
        try:
            base = constants.ZZT_ELEMENTS[id]
        except IndexError:
            base = constants.STUB_ELEMENT
        # Editing color_id, fg, or bg should adjust all three
        # plus fg/bg/color names

        self.id = base["id"]
        self.tile = tile
        self.name = base["name"]
        self.oop_name = base["oop_name"]
        self.character = base["character"] if character is None else character
        self.color_id = color
        self.foreground = color % 16
        self.background = color // 16
        self.foreground_name = constants.COLOR_NAMES[self.foreground]
        self.background_name = constants.COLOR_NAMES[self.background]
        self.stat_idx = stat_idx
        self._stat = None

        if self.background != 0:
            self.color_name = self.foreground_name + " on " + \
                self.background_name
        else:
            self.color_name = self.foreground_name

    @property
    def stat(self):
        return self._stat

    @stat.setter
    def stat(self, stat):
        self._stat = stat

    def __str__(self):
        return str(self.color_name) + " " + self.name
