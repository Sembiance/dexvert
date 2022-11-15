import os
import struct
import time  # DEBUG

import zookeeper.settings as settings
import zookeeper.constants as constants
import zookeeper.exceptions as exceptions

from .meta import Meta
from .world import World
from .board import Board
from .element import Element
from .stat import Stat
from .flag import Flag

try:
    from PIL import Image
    from PIL import ImageColor
    from PIL import ImageOps
    constants.IMAGE_SUPPORT = True
except ImportError:
    constants.IMAGE_SUPPORT = False


class Zookeeper(object):
    def __init__(self, file=None):

        self.fh = None
        self.meta = Meta()
        self.world = World()
        self.boards = []

        if constants.IMAGE_SUPPORT:
            # Palette settings
            self.load_palette()

            # Charset settings
            self.load_charset()

        if file:
            self.load_file(file)
            if file[-4:].lower() in [".zzt", ".sav"]:
                self.parse_file()

    """ Decorators """
    def has_file(f, *args):
        def has_file_decorator(self, *args, **kwargs):
            if self.fh:
                return f(self, *args, **kwargs)
            else:
                raise exceptions.FileNotLoadedError

        return has_file_decorator

    def has_pil(f, *args):
        def has_pil_decorator(self, *args, **kwargs):
            if constants.IMAGE_SUPPORT:
                return f(self, *args, **kwargs)
            else:
                raise exceptions.PILNotLoadedError
        return has_pil_decorator
    """ End Decorators """

    """ Helper functions """
    @has_file
    def read_bytes(self, num, format="int", *args, **kwargs):
        """ Read <num> bytes of the file and return the data as <format> """
        raw = os.read(self.fh, num)
        output = ""

        if format == "int":
            if num == 0:
                return 0
            try:
                if len(raw) == 1:
                    output = struct.unpack("B", raw)[0]
                elif len(raw) == 2:
                    output = struct.unpack("H", raw)[0]
                else:
                    output = 0
            except:
                print("ERROR PARSING BYTES")
                return 0
        elif format == "string":
            output = ""
            if num == 0:
                return output

            return raw.decode("cp437")
        return output

    """ End Helper functions """

    @has_pil
    def load_palette(self, path="auto"):
        """ Loads a DAT file representing a graphical palette """
        if path is None:
            self.palette = None
            self.palette_name = "None"
            return True

        if path == "auto":
            path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "palettes", "ega.dat"
            )

        self.palette = []
        self.charset_name = os.path.splitext(os.path.basename(path))[0]

        with open(path) as fh:
            for line in fh.readlines():
                if line:
                    self.palette.append(line.strip().split(";")[0])
        return True

    @has_pil
    def load_charset(self, path="auto"):
        """ Loads a PNG file representing a charset's characters """
        # TODO: Make charset a class
        if path is None:
            self.charset = None
            self.charset_name = "None"
            return True

        if path == "auto":
            path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "charsets", "cp437.png"
            )

        try:
            mini_charset = Image.open(path)
            self.charset_name = os.path.splitext(os.path.basename(path))[0]
        except FileNotFoundError:
            self.charset = None
            self.charset_name = "None"
            # TODO: Warn user charset loading failed
            return False

        # Expand the charset with the palette
        self.charset = Image.new("RGBA", (1024, 448), (0, 0, 0, 0))

        x, y = (0, 0)
        for color in self.palette:
            dye = Image.new("RGB", (128, 224), color)
            mini_charset.paste(dye, mask=mini_charset)
            self.charset.paste(mini_charset, (x, y))
            x += 128
            if x >= 1024:
                x = 0
                y += 224

        end_time = time.time()
        return True

    def load_file(self, file):
        """ Load a file to be parsed """
        self.meta.file_name = os.path.basename(file)
        self.meta.full_path = file

        flags = os.O_RDONLY
        if hasattr(os, 'O_BINARY'):
            flags = flags | os.O_BINARY
        self.fh = os.open(file, flags)
        return True

    def close_file(self):
        os.close(self.fh)
        self.fh = None
        self.meta = Meta()

    @has_file
    def parse_file(self):
        """ Convenience function to parse an entire file with one function """
        os.lseek(self.fh, 0, os.SEEK_SET)  # Jump to start of file
        self.parse_world()
        self.parse_boards()
        self.parse_elements()
        return True

    @has_file
    def parse_world(self):
        """ Parse a ZZT file's world header """
        self.world.identifier = self.read_bytes(2)
        self.world.engine = constants.ENGINES.get(
            self.world.identifier, "UNKNOWN"
        )
        self.world._non_title_boards = self.read_bytes(2)
        self.world._total_boards = self.world.non_title_boards + 1
        self.world.ammo = self.read_bytes(2)
        self.world.gems = self.read_bytes(2)

        self.world.keys = {
            "Blue": True if self.read_bytes(1) != 0 else False,
            "Green": True if self.read_bytes(1) != 0 else False,
            "Cyan": True if self.read_bytes(1) != 0 else False,
            "Red": True if self.read_bytes(1) != 0 else False,
            "Purple": True if self.read_bytes(1) != 0 else False,
            "Yellow": True if self.read_bytes(1) != 0 else False,
            "White": True if self.read_bytes(1) != 0 else False
        }

        self.world.health = self.read_bytes(2)
        self.world.current_board = self.read_bytes(2)
        self.world.torches = self.read_bytes(2)
        self.world.torch_cycles = self.read_bytes(2)
        self.world.energizer_cycles = self.read_bytes(2)
        self.world.unused = self.read_bytes(2)
        self.world.score = self.read_bytes(2)
        self.world.world_name_length = self.read_bytes(1)
        self.world.world_name = self.read_bytes(
            20, "string"
        )[:self.world.world_name_length]

        for idx in range(0, 10):
            length = self.read_bytes(1)
            self.world.flags[idx].length = length
            self.world.flags[idx].name = self.read_bytes(20, "string")[:length]

        self.world.time_passed = self.read_bytes(2)
        # Only used during runtime. Set to 0 on save.
        self.world.time_passed_ticks = self.read_bytes(2)
        save_temp = self.read_bytes(1)
        self.world.saved_game = True if save_temp != 0 else False

        return True

    @has_file
    def parse_boards(self):
        """ Parse a ZZT file's boards """
        # TODO: Support for .BRD files
        board_offset = 512
        boards = range(0, self.world.total_boards)

        for board_idx in boards:
            board = Board()
            board.start_address = board_offset
            board.element_address = board_offset + 53
            board.stats_address = board.element_address

            # Get the Zookeeper's charset image
            board.charset = self.charset

            os.lseek(self.fh, board_offset, os.SEEK_SET)
            board.size = self.read_bytes(2)
            board.title_length = self.read_bytes(1)
            board.title = self.read_bytes(50, "string")[:board.title_length]

            # Elements
            parsed_elements = 0
            board.rle_elements = []
            while (parsed_elements < 1500):
                quantity = self.read_bytes(1)

                # This may be a placeholder (see Darkmarth #335)
                if quantity == 0:
                    quantity = 1500

                element_id = self.read_bytes(1)
                color = self.read_bytes(1)
                board.rle_elements.append([quantity, element_id, color])
                parsed_elements += quantity
                board.stats_address += 3

            # Board details
            board.can_fire = self.read_bytes(1)
            board.is_dark = True if self.read_bytes(1) != 0 else False
            board.board_north = self.read_bytes(1)
            board.board_south = self.read_bytes(1)
            board.board_west = self.read_bytes(1)
            board.board_east = self.read_bytes(1)
            board.zap = True if self.read_bytes(1) != 0 else False
            board.message_length = self.read_bytes(1)
            board.message = self.read_bytes(58, "string")
            board.message = board.message[:board.message_length]
            board.enter_x = self.read_bytes(1)
            board.enter_y = self.read_bytes(1)
            board.time_limit = self.read_bytes(2)
            board.unused = self.read_bytes(16, "string")
            board.stat_count = self.read_bytes(2)  # Not counting player
            board.stats = []
            board.stats_address += 88

            # Parse Stats
            parsed_stats = 0
            while parsed_stats <= board.stat_count:
                stat = Stat(parsed_stats)

                stat.x = self.read_bytes(1)
                stat.y = self.read_bytes(1)
                stat.tile = (stat.x - 1) + ((stat.y - 1) * 60)
                stat.x_step = self.read_bytes(2)
                stat.y_step = self.read_bytes(2)
                stat.cycle = self.read_bytes(2)
                stat.param1 = self.read_bytes(1)
                stat.param2 = self.read_bytes(1)
                stat.param3 = self.read_bytes(1)
                stat.follower = self.read_bytes(2)
                stat.leader = self.read_bytes(2)
                stat.under_id = self.read_bytes(1)
                stat.under_color = self.read_bytes(1)
                stat.pointer = self.read_bytes(4)
                stat.current_instruction = self.read_bytes(2)

                stat.bound_idx = None
                stat.oop_length = self.read_bytes(2)
                stat.padding = self.read_bytes(8, "string")

                if stat.oop_length > 32767:  # Pre-bound element
                    stat.oop_length = 0
                    stat.bound_idx = stat.oop_length - 32768

                if stat.oop_length:
                    stat.oop = self.read_bytes(stat.oop_length, "string")

                if settings.LINE_BREAK != "\r":
                    stat.oop = stat.oop.replace("\r", settings.LINE_BREAK)

                board.stats.append(stat)
                parsed_stats += 1

            # Check for corrupt board
            """
            // Jump to the start of the next board in file (for corrupt boards)
            var manual_idx = (start_idx + board.size * 2) + 4;
            if (world.idx != manual_idx)
            {
                board.corrupt = true;
                world.idx = manual_idx;
            }
            """

            # Append board to list
            board_offset += board.size + 2
            self.boards.append(board)
        return True

    @has_file
    def parse_elements(self, board_num=None):
        """ Parse the elements on every board """
        # TODO: Allow parsing elements per board
        for board_idx in range(0, self.world.total_boards):
            self.boards[board_idx].elements = []

            stat_tiles = {}
            stat_idx = 0
            for stat in self.boards[board_idx].stats:
                stat_tiles[stat.tile] = stat_idx
                stat_idx += 1

            tile_idx = 0
            for qty, id, color in self.boards[board_idx].rle_elements:
                for _ in range(0, qty):
                    # Text (color is used for character)
                    if (id >= 47 and id <= 53):
                        if id != 53:
                            text_color = ((id - 46) * 16 + 15)
                        else:
                            text_color = 15
                        element = Element(id, text_color, tile=tile_idx,
                                          stat_idx=stat_tiles
                                          .get(tile_idx, None),
                                          character=color)
                    # Invisible Walls
                    elif (id == 28 and settings.INVISIBLE_MODE != constants.INVISIBLE_INVISIBLE):
                        if settings.INVISIBLE_MODE == constants.INVISIBLE_EDITOR:
                            element = Element(id, color, tile=tile_idx,
                                              stat_idx=stat_tiles
                                              .get(tile_idx, None),
                                              character=176)
                        elif settings.INVISIBLE_MODE == constants.INVISIBLE_REVEALED:
                            element = Element(id, color, tile=tile_idx,
                                              stat_idx=stat_tiles
                                              .get(tile_idx, None),
                                              character=178)
                    # Objects
                    elif (id == 36 and stat_tiles.get(tile_idx, None)
                            is not None):
                        element = Element(id, color, tile=tile_idx,
                                          stat_idx=stat_tiles
                                          .get(tile_idx, None),
                                          character=self.boards[board_idx]
                                          .stats[stat_tiles[tile_idx]]
                                          .param1)
                    # Pushers
                    elif (id == 40 and stat_tiles.get(tile_idx, None)
                            is not None):
                        stat = self.boards[board_idx].stats[
                            stat_tiles[tile_idx]]
                        if stat.x_step > 32767:
                            pusher_char = 17
                        elif stat.x_step > 0:
                            pusher_char = 16
                        elif stat.y_step > 32767:
                            pusher_char = 30
                        elif stat.y_step > 0:
                            pusher_char = 31
                        if stat.x_step == 0 and stat.y_step == 0:
                            pusher_char = 31
                        element = Element(id, color, tile=tile_idx,
                                          stat_idx=stat_tiles
                                          .get(tile_idx, None),
                                          character=pusher_char)
                    # Transporters
                    elif (id == 30 and stat_tiles.get(tile_idx, None)
                          is not None):
                        stat = self.boards[board_idx] \
                            .stats[stat_tiles[tile_idx]]
                        if stat.x_step > 32767:
                            transporter_char = 60
                        elif stat.x_step > 0:
                            transporter_char = 62
                        elif stat.y_step > 32767:
                            transporter_char = 94
                        elif stat.y_step > 0:
                            transporter_char = 118
                        if stat.x_step == 0 and stat.y_step == 0:
                            transporter_char = 94
                        element = Element(id, color, tile=tile_idx,
                                          stat_idx=stat_tiles
                                          .get(tile_idx, None),
                                          character=transporter_char)
                    # ACE on the title screen should be replaced with a monitor
                    elif (settings.TITLE_SCREEN_MONITOR and board_idx == 0 and
                          self.boards[board_idx].stats[0].tile ==
                          tile_idx):
                        element = Element(3, 0, tile=tile_idx,
                                          stat_idx=stat_tiles
                                          .get(tile_idx, None))
                    # Default handler
                    else:
                        element = Element(id, color, tile=tile_idx,
                                          stat_idx=stat_tiles
                                          .get(tile_idx, None))

                    if element.stat_idx is not None:
                        element.stat = self.boards[board_idx] \
                            .stats[element.stat_idx]
                    self.boards[board_idx].elements.append(element)
                    tile_idx += 1

            # Update line walls
            for tile_idx in range(0, 1500):
                if self.boards[board_idx].elements[tile_idx].id == 31:
                    x = tile_idx % 60
                    y = tile_idx // 60
                    line_key = ""

                    if y == 0:  # Top side of board
                        line_key += "1"
                    else:
                        line_key += ("1" if self.boards[board_idx]
                                     .elements[tile_idx - 60].id == 31
                                     else "0")

                    if y == 24:  # Bottom side of board
                        line_key += "1"
                    else:
                        line_key += ("1" if self.boards[board_idx]
                                     .elements[tile_idx + 60].id == 31
                                     else "0")

                    if x == 59:  # Right side of board
                        line_key += "1"
                    else:
                        line_key += ("1" if self.boards[board_idx]
                                     .elements[tile_idx + 1].id == 31
                                     else "0")

                    if x == 0:  # Left side of board
                        line_key += "1"
                    else:
                        line_key += ("1" if self.boards[board_idx]
                                     .elements[tile_idx - 1].id == 31
                                     else "0")
                    self.boards[board_idx].elements[tile_idx].character = \
                        constants.LINE_CHARACTERS.get(line_key, 33)

    def export_font(self, file, new_filename=None, colors=1):
        """ Exports the provided font's charmap rendered as a PNG """
        # Colors may be 1 for just white, or 16 for all foregrounds
        # TODO: There's no reason for this to share self.fh
        if colors not in [1, 16]:
            raise Exception

        filename = os.path.basename(file)

        if new_filename is None:
            new_filename = os.path.splitext(filename)[0] + ".png"

        self.load_file(file)
        # Verify Font Mania .com font
        os.lseek(self.fh, 8, os.SEEK_SET)
        fm_check = self.read_bytes(10, "string")
        if fm_check != "FONT MANIA":
            print("File is not a Font Mania .com file!")
            print("Read:", fm_check)
            raise Exception

        # Prepare graphics file for writing
        if colors == 16:
            image = Image.new("RGBA", (1024, 448))
            color_list = range(0, 16)
        elif colors == 1:
            image = Image.new("RGBA", (128, 224))
            color_list = [15]
        im = image.load()
        x, y = (0, 0)
        color_idx = 0

        # Colors
        for color_idx in color_list:
            if colors == 16:
                if color_idx < 8:
                    x = color_idx * 16 * 8
                    y = 0
                else:
                    x = (color_idx - 8) * 16 * 8
                    y = 224
            else:
                x = 0
                y = 0

            os.lseek(self.fh, 1442, os.SEEK_SET)  # Jump to start of font data
            rgb_tuple = ImageColor.getrgb("#" + constants.COLORS[color_idx])
            rgba_tuple = (rgb_tuple[0], rgb_tuple[1], rgb_tuple[2], 255)

            # Characters
            for char_idx in range(0, 256):
                y_offset = 0
                if char_idx and char_idx % 16 == 0:  # Next line
                    y += 14
                    x -= (8 * 16)

                # Rows
                for row_idx in range(0, 14):
                    x_offset = 0
                    raw = self.read_bytes(1)
                    bits = ("00000000" + str(bin(raw))[2:])[-8:]

                    # Columns
                    for bit in bits:
                        if bit == "1":
                            im[x + x_offset, y + y_offset] = rgba_tuple
                        x_offset += 1
                    y_offset += 1

                x += 8

        image = image.save(new_filename)
        return True

    def save(self, filename=None):
        """
            Writes a .ZZT file

            filename: Uses loaded filename if none is provided
        """

        # Write world header
        output = self.world.encode()

        # Write board data
        for board in self.boards:
            encoded_board = board.encode()
            output += encoded_board

        # Save
        if filename is None:
            filename = self.meta.full_path
        with open(filename, "wb") as fh:
            fh.write(output)
        return True

    def new_world(self, *args, **kwargs):
        # Clear existing data
        if self.fh:
            os.close(self.fh)
        self.fh = None

        self.meta = Meta()
        self.world = World(*args, **kwargs)
        self.boards = [Board(populate=True, title="Title screen")]
        return True
