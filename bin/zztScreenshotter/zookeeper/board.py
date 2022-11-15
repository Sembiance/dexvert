import hashlib
import os

import zookeeper.constants as constants
import zookeeper.limits as limits

from .element import Element
from .stat import Stat

try:
    from PIL import Image
    from PIL import ImageColor
    constants.IMAGE_SUPPORT = True
except ImportError:
    constants.IMAGE_SUPPORT = False


class Board(object):
    def __init__(self, title="Untitled", populate=False, can_fire=255,
        is_dark=False,
        board_north=0, board_south=0, board_west=0, board_east=0,
        zap=False, message="", enter_x=30, enter_y=12, time_limit=0
    ):
        self.start_address = None
        self.element_address = None
        self.stats_address = None
        self.size = 0
        self.title = title[:limits.BOARD_NAME_LENGTH]
        self.title_length = len(self.title)
        self.elements = []
        self.rle_elements = []
        self.can_fire = can_fire
        self.is_dark = is_dark
        self.board_north = board_north
        self.board_south = board_south
        self.board_west = board_west
        self.board_east = board_east
        self.zap = zap
        self.message = ""[:limits.MESSAGE_LENGTH]
        self.message_length = len(self.message)
        self.enter_x = enter_x
        self.enter_y = enter_y
        self.time_limit = 0
        self.unused = b""
        self.stat_count = 0
        self.stats = []

        # Charset
        if constants.IMAGE_SUPPORT:
            path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "charsets", "cp437.png"
                )
            self.charset = Image.open(path)

        if populate:
            # TODO: If populate is an Element(), populate with that element.
            for x in range(0, 1500):
                self.elements.append(Element(0, 0, x))

            # Add a player at (30,12)
            player = Element(4, 31, self.enter_x + (self.enter_y * 60))
            self.elements[689] = player
            # Add a stat for the player
            stat = Stat(0)
            stat.x = 30
            stat.y = 12
            stat.tile = self.enter_x + (self.enter_y * 60)
            self.stats.append(stat)


    """ Decorators """
    def has_pil(f, *args):
        def has_pil_decorator(self, *args, **kwargs):
            if constants.IMAGE_SUPPORT:
                return f(self, *args, **kwargs)
            else:
                raise Exception
        return has_pil_decorator
    """ End Decorators """

    def __str__(self):
        return str(self.title)

    @has_pil
    def get_tile(self, ch, fg, bg):
        # Calculate area of graphics with correct color
        (x, y) = (0, 0)
        x = fg * 128
        if x >= 1024:
            x -= 1024
            y += 224

        # Offset by character
        ch_x = (ch % 16) * 8
        ch_y = (ch // 16) * 14
        x += ch_x
        y += ch_y
        tile = Image.new("RGBA", (8, 14), color="#" + constants.COLORS[bg])
        temp = self.charset.crop((x, y, x + 8, y + 14))
        tile = Image.alpha_composite(tile, temp)
        return tile

    @has_pil
    def render(self, title_screen=False, format="RGB", dark=False):
        """
        Renders PNG of board and returns as an Image
        title_screen - Replaces the player with a black/black tile
        format - RGB by default or RGBA for alpha support
        dark - Renders board as if it were dark
        """
        image = Image.new(format, (480, 350), "black")

        if not self.elements:
            raise Exception

        monitor_tile = (self.stats[0].x - 1 + ((self.stats[0].y - 1) * 60))
        for idx in range(0, 1500):
            element = self.elements[idx]
            if not dark:
                # Render empties as black on black
                if element.id == 0:
                    tile = self.get_tile(element.character, 0, 0)
                elif title_screen and idx == monitor_tile:  # Hide player
                    tile = self.get_tile(element.character, 0, 0)
                else:
                    # TODO: Handle hi/low intensity backgrounds
                    tile = self.get_tile(element.character,
                                         element.foreground,
                                         element.background % 8)  # mod8 forces low
            else:
                # TODO: This should not be hard coded
                if element.id in [4, 6, 11]:
                    tile = self.get_tile(element.character,
                                     element.foreground,
                                     element.background % 8)  # mod8 forces low
                else:
                    tile = self.get_tile(176, 7, 0)
            image.paste(tile, ((idx % 60) * 8, (idx // 60) * 14))

        return image;

    @has_pil
    def screenshot(self, filename, title_screen=False, format="RGB", dark=False):
        """
        Saves PNG rendition of board
        filename - Output filename (sans extension)
        title_screen - Replaces the player with a black/black tile
        format - RGB by default or RGBA for alpha support
        dark - Renders board as if it were dark
        """
        image = self.render(title_screen, format, dark)
        image.save(filename + ".png")

    @has_pil
    def scroll(self, text, filename,
               type="code", expand=True, line=0, custom_name=None):
        """ Render text as a ZZT Scroll/Object message window
        type: scroll | object | code -- Determines window header,
        and whether or not ZZT-OOP is displayed
        expand: True | False -- Determines if the height of the image
        can be enlarged if it can't fit in the visible area
        line: The top line of text to start writing
        custom_name: Uses the given name instead of @object,
        Interaction, Scroll, etc. window must be 19 lines tall minimum.
        """
        lines = text.split("\n")
        # 2 for the extra dot rows | 4 more for the scroll header/footer rows
        line_count = len(lines) + 6
        if lines and lines[0] and lines[0][0] == "@" and type != "code":
            line_count -= 1

        height = max(266, line_count * 14) if expand else 266
        image = Image.new("RGB", (392, height), "black")

        # Top
        y = 0
        for x in range(0, 49):
            if x == 0:
                tile = self.get_tile(198, 15, 0)
            elif x == 1 or x == 47:
                tile = self.get_tile(209, 15, 0)
            elif x == 48:
                tile = self.get_tile(181, 15, 0)
            else:
                tile = self.get_tile(205, 15, 0)
            image.paste(tile, (x * 8, y * 14))

        # Name
        if custom_name:
            name = custom_name
        elif type == "code":
            name = "Edit Program"
        elif type == "scroll":
            name = "Scroll"
        elif type == "object":
            name = "Interaction" if lines[0][0] != "@" else lines[0][1:]

        name = self.center_text(name, "name")
        name = name + " " * 50
        name = "  " + (name + " " * 42)[:43]  # Padding
        (x, y) = (2, 1)
        for ch in name:
            cp437 = constants.UNICODE_TO_CP437.get(ord(ch), 63)
            tile = self.get_tile(cp437, 14, 1)
            image.paste(tile, (x * 8, y * 14))
            x += 1

        # Lower Top
        y = 2
        for x in range(2, 47):
            tile = self.get_tile(205, 15, 0)
            image.paste(tile, (x * 8, y * 14))

        # Bottom
        y = height // 14 - 1
        for x in range(0, 49):
            if x == 0:
                tile = self.get_tile(198, 15, 0)
            elif x == 1 or x == 47:
                tile = self.get_tile(207, 15, 0)
            elif x == 48:
                tile = self.get_tile(181, 15, 0)
            else:
                tile = self.get_tile(205, 15, 0)
            image.paste(tile, (x * 8, y * 14))

        # Sides
        for y in range(1, height // 14 - 1):
            if y != 2:
                tile = self.get_tile(179, 15, 0)
                image.paste(tile, (8, y * 14))
                image.paste(tile, (376, y * 14))
            else:
                tile = self.get_tile(198, 15, 0)
                image.paste(tile, (8, y * 14))
                tile = self.get_tile(181, 15, 0)
                image.paste(tile, (376, y * 14))

        # Body
        lines = ["  \u2022    \u2022    \u2022    \u2022    \u2022" +
                 "    \u2022    \u2022    \u2022    \u2022"] + lines \
            + ["  \u2022    \u2022    \u2022    \u2022    \u2022" +
               "    \u2022    \u2022    \u2022    \u2022"]
        y = 3
        for line in lines:
            x = 2
            hyperlink = False
            # Special lines
            color = 14  # Yellow
            if line and line[0] == "$":
                color = 15
                if len(line) % 2 != 0:
                    line = self.center_text(line[1:])
                else:
                    line = self.center_text(line[1:])
            elif line and line[0] == "!":
                hyperlink = True
                line = "  ►  " + line.split(";", 1)[-1]

            line = line + " " * 50
            line = "  " + (line + " " * 42)[:43]  # Padding
            for ch in line:
                if hyperlink:
                    if x == 6:
                        color = 13
                    else:
                        color = 15
                cp437 = constants.UNICODE_TO_CP437.get(ord(ch), 63)
                tile = self.get_tile(cp437, color, 1)
                image.paste(tile, (x * 8, y * 14))
                x += 1
            y += 1

        # Selected Line
        y = len(lines) // 2
        tile = self.get_tile(175, 12, 1)
        image.paste(tile, (2 * 8, y * 14))
        tile = self.get_tile(174, 12, 1)
        image.paste(tile, (46 * 8, y * 14))

        image.save(filename + ".png")

    def center_text(self, text, mode="text"):
        """ Returns a padded string centered for ZZT's windows """
        if mode == "text":
            maximum = 41
        elif mode == "name":
            maximum = 45
        while len(text) < 41:
            text = " " + text + " "
        if len(text) > 41:
            if mode == "text":
                text = text[1:]
            elif mode == "name":
                text = text[:-1]

        return text

    def get_element(self, query):
        """
            Returns a reference to an Element based on given query.
            query: Either a tuple (X,Y) from (1,1) to (60,25)
            or a tile index from 1-1500.
        """
        if isinstance(query, tuple):  # Coordinates
            return self.elements[query[0] - 1 + ((query[1] - 1) * 60)]
        elif isinstance(query, int):  # Tile idx
            query = max(1, min(1500, query))
            return self.elements[query]

    def export(self, filename):
        rle_string = self.encode()
        with open(filename + ".brd", "wb") as fh:
            fh.write(rle_string)
        return True

    def encode(self):
        rle = bytearray(b'\x00\x00')
        board_size = 0

        # Board title/length
        rle.append(len(self.title))
        title = (bytes(self.title, "utf-8") + b"\x00" * 50)[:50]
        for ch in title:
            rle.append(ch)

        # Use the original board RLE data if elements were never parsed
        if not self.elements:
            for element in self.rle_elements:
                for byte in element:
                    rle.append(byte)

            # Set board size
            rle[0] = (len(rle) - 2) % 256
            rle[1] = (len(rle) - 2) // 256
        else:
            last_element = None
            last_color = None
            quantity = 1
            debug_total = 0
            for element in self.elements:
                element_id = element.id
                if (element_id >= 47 and element_id <= 53):
                    color = element.character
                else:
                    color = element.color_id

                if (element_id, color) != (last_element, last_color) or quantity == 255:
                    if last_element is not None:  # Write the values
                        rle.append(quantity)
                        rle.append(last_element)
                        rle.append(last_color)
                        debug_total += quantity
                        quantity = 1
                else:
                    quantity += 1

                last_element = element_id
                last_color = color

            # Force the last set out
            rle.append(quantity)
            rle.append(element_id)
            rle.append(color)
            debug_total += quantity

        # Board details
        rle.append(self.can_fire)
        rle.append(self.is_dark)
        rle.append(self.board_north)
        rle.append(self.board_south)
        rle.append(self.board_west)
        rle.append(self.board_east)
        rle.append(self.zap)
        rle.append(self.message_length)
        message = (bytes(self.message, "utf-8") + b"\x00" * 58)[:58]
        for ch in message:
            rle.append(ch)
        rle.append(self.enter_x)
        rle.append(self.enter_y)
        rle.append(self.time_limit % 256)
        rle.append(self.time_limit // 256)
        for x in range(0, 16):  # 16 unused bytes
            rle.append(0)
        stat_count = len(self.stats) - 1
        rle.append(stat_count % 256)  # Ignore player
        rle.append(stat_count // 256)

        # Stat info
        for stat in self.stats:
            rle.append(stat.x)
            rle.append(stat.y)
            rle.append(stat.x_step % 256)
            rle.append(stat.x_step // 256)
            rle.append(stat.y_step % 256)
            rle.append(stat.y_step // 256)
            rle.append(stat.cycle % 256)
            rle.append(stat.cycle // 256)
            rle.append(stat.param1)
            rle.append(stat.param2)
            rle.append(stat.param3)
            rle.append(stat.follower % 256)
            rle.append(stat.follower // 256)
            rle.append(stat.leader % 256)
            rle.append(stat.leader // 256)
            rle.append(stat.under_id)
            rle.append(stat.under_color)
            for x in range(0, 4):
                rle.append(0)  # 4 unused bytes (pointer)
            rle.append(stat.current_instruction % 256)
            rle.append(stat.current_instruction // 256)

            if stat.oop_length > 32767:  # TODO: Pre-bound elements
                rle.append("X")
                rle.append("X")
            else:
                rle.append(stat.oop_length % 256)
                rle.append(stat.oop_length // 256)
            for x in range(0, 8):  # 8 unused bytes (padding)
                rle.append(0)

            if stat.oop_length:
                oop = bytes(stat.oop.replace("\n", "\r"), "cp437")
                for x in range(0, stat.oop_length):
                    rle.append(oop[x])

        # Set board size
        rle[0] = (len(rle) - 2) % 256
        rle[1] = (len(rle) - 2) // 256
        return rle
