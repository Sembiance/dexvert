class Stat(object):
    def __init__(self, idx):
        self.idx = None
        self.x = 1
        self.y = 1
        self.tile = (self.x - 1) + ((self.y - 1) * 60)
        self.x_step = 0
        self.y_step = 0
        self.cycle = 1
        self.param1 = 0
        self.param2 = 0
        self.param3 = 0
        self.follower = 0
        self.leader = 0
        self.under_id = 0
        self.under_color = 0
        self.pointer = 0
        self.current_instruction = 0
        self.bound_idx = 0
        self.oop_length = 0
        self.padding = ""
        self.oop = ""
