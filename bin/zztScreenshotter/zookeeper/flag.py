class Flag(object):
    def __init__(self, flag_name=""):
        self._name = flag_name
        self._length = len(flag_name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, flag_name):
        self._name = flag_name
        self._length = len(flag_name)

    def __str__(self):
        return str(self.name).encode("utf-8").decode("utf-8")
