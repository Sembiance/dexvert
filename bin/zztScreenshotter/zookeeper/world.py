import zookeeper.constants as constants
import zookeeper.exceptions as exceptions
import zookeeper.limits as limits

from .flag import Flag


class World(object):
    def __init__(
        self, engine="ZZT",
        health=100, ammo=0, torches=0, gems=0, score=0,
        keys={"Blue": False, "Green": False, "Cyan": False,
              "Red": False, "Purple": False, "Yellow": False,
              "White": False},
        torch_cycles=0, energizer_cycles=0,
        time_passed=0, time_passed_ticks=0,
        name="NEWWORLD",
        saved_game = False
    ):
        self.engine = engine
        self.identifier = constants.IDENTIFIERS[engine]

        self._non_title_boards = 0
        self._total_boards = 1
        self.ammo = ammo
        self.gems = gems
        self.keys = keys
        self.health = health
        self.current_board = 0
        self.torches = torches
        self.torch_cycles = torch_cycles
        self.energizer_cycles = energizer_cycles
        self.unused = 0
        self.score = score
        self._world_name = name[:limits.WORLD_NAME_LENGTH]
        self._world_name_length = len(self._world_name)

        self.flags = (Flag(), Flag(), Flag(), Flag(), Flag(),
                      Flag(), Flag(), Flag(), Flag(), Flag()
                      )
        self.time_passed = time_passed
        self.time_passed_ticks = time_passed_ticks
        self.saved_game = saved_game

    @property
    def non_title_boards(self):
        return self._non_title_boards

    @property
    def total_boards(self):
        return self._total_boards

    @property
    def world_name(self):
        return self._world_name

    @world_name.setter
    def world_name(self, name):
        self._world_name = name
        self._world_name_length = len(name)

    def encode(self):
        """ Encode the world header as a bytearray """
        output = bytearray()
        output.append(self.identifier % 256)
        output.append(self.identifier // 256)
        # TODO: This should come from the length of the boards array
        output.append((self.total_boards - 1) % 256)
        output.append((self.total_boards - 1) // 256)
        output.append(self.ammo % 256)
        output.append(self.ammo // 256)
        output.append(self.gems % 256)
        output.append(self.gems // 256)
        for k in ["Blue", "Green", "Cyan", "Red", "Purple", "Yellow", "White"]:
            output.append(255 if self.keys.get(k, False) else 0)
        output.append(self.health % 256)
        output.append(self.health // 256)
        output.append(self.current_board % 256)
        output.append(self.current_board // 256)

        output.append(self.torches % 256)
        output.append(self.torches // 256)
        output.append(self.torch_cycles % 256)
        output.append(self.torch_cycles // 256)
        output.append(self.energizer_cycles % 256)
        output.append(self.energizer_cycles // 256)
        output.append(0)
        output.append(0)
        output.append(self.score % 256)
        output.append(self.score // 256)
        output.append(self._world_name_length)
        world_name = (bytes(self.world_name, "utf-8") + b"\x00" * 20)[:20]
        for ch in world_name:
            output.append(ch)

        # Flags
        for idx in range(0, 10):
            output.append(len(self.flags[idx].name))
            flag_name = (bytes(self.flags[idx].name, "utf-8") +
                         b"\x00" * 20)[:20]
            for ch in flag_name:
                output.append(ch)

        output.append(self.time_passed % 256)
        output.append(self.time_passed // 256)
        output.append(self.time_passed_ticks % 256)
        output.append(self.time_passed_ticks // 256)

        output.append(self.saved_game)

        while len(output) < 512:
            output.append(0)

        return output

    def __str__(self):
        return str(self.world_name)
