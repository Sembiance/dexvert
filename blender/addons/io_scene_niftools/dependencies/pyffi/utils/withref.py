# adapted from http://pypi.python.org/pypi/withref

class ref(object):
    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        return self.obj

    def __exit__(self, _type, value, traceback):
        return False
