class Meta(object):
    def __init__(self):
        self.file_name = None
        self.full_path = None

    def __str__(self):
        return self.file_name + "\n" + self.full_path
