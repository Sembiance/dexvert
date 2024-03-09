from nifgen.formats.dds.imports import name_type_map
import io
import logging
import math

from nifgen.formats.base.compounds.PadAlign import get_padding_size
from nifgen.formats.dds.enums.D3D10ResourceDimension import D3D10ResourceDimension
from nifgen.formats.dds.enums.FourCC import FourCC
from nifgen.formats.dds.structs.Dxt10Header import Dxt10Header
from nifgen.formats.dds.structs.Header import Header
from nifgen.io import IoFile

LINE_BYTES = 256


class DdsContext(object):
    def __init__(self):
        self.version = 0
        self.user_version = 0

    def __repr__(self):
        return f"{self.version} | {self.user_version}"


class DdsFile(Header, IoFile):

    def __init__(self, ):
        super().__init__(DdsContext())
        self.header_string.data = b"DDS "

        # header flags
        self.flags.height = 1
        self.flags.width = 1
        self.flags.mipmap_count = 1
        self.flags.linear_size = 1

        # pixel format flags
        self.pixel_format.flags.four_c_c = 1
        self.pixel_format.four_c_c = FourCC.DX10

        self.dx_10 = Dxt10Header(self.context, 0, None)
        self.dx_10.resource_dimension = D3D10ResourceDimension.D3D10_RESOURCE_DIMENSION_TEXTURE2D
        self.dx_10.num_tiles = 1

        # caps 1
        self.caps_1.texture = 0

        # other stuff
        self.buffer = b""

    def load(self, filepath):
        with open(filepath, "rb") as stream:
            self.read_fields(stream, self)
            self.buffer = stream.read()

    def write(self, stream):
        self.write_fields(stream, self)
        stream.write(self.buffer)

    def save(self, filepath):
        with open(filepath, "wb") as stream:
            self.write(stream)

    def get_bytes_size(self, num_pixels):
        return int(round(num_pixels / self.pixels_per_byte))

    def pad_block(self, x):
        """Returns a pixel count padded to as many blocks as needed"""
        num_blocks = math.ceil(x / self.block_len_pixels_1d)
        return num_blocks * self.block_len_pixels_1d

    def calculate_mip_sizes(self):
        # logging.debug("Calculating mip map sizes")
        self.get_pixel_fmt()
        tiles = []
        for array_i in range(self.dx_10.num_tiles):
            tile_mips = []
            h = self.height
            w = self.width
            tiles.append(tile_mips)
            for mip_i in range(self.mipmap_count):
                # get pixels as represented by blocks, usually 4x4
                num_pixels = self.pad_block(h) * self.pad_block(w)
                num_bytes = self.get_bytes_size(num_pixels)
                # logging.debug(f"Tile {array_i} Mip {mip_i} with {num_pixels} pixels, {num_bytes} bytes")
                tile_mips.append((h, w, num_bytes))
                h //= 2
                w //= 2
                # don't allow any to become 0
                h = max(h, 1)
                w = max(w, 1)
        return tiles

    @property
    def compression_format(self):
        """Returns a string representing the compression format"""
        if self.pixel_format.four_c_c == FourCC.DX10:
            return self.dx_10.dxgi_format.name
        return self.pixel_format.four_c_c.name

    def get_pixel_fmt(self):
        # get compression type
        comp = self.compression_format
        # get bpp from compression type
        if "R8G8B8A8" in comp:
            self.pixels_per_byte = 0.25
            self.block_len_pixels_1d = 1
        # 64 bits for 16 pixels
        elif "BC1" in comp or "DXT1" in comp or "BC4" in comp:
            self.pixels_per_byte = 2
            self.block_len_pixels_1d = 4
        # 128 bits for 16 pixels
        else:
            self.pixels_per_byte = 1
            self.block_len_pixels_1d = 4
        # a block is the smallest usable unit, for dxt it is 4x4 px, for RGBA it is 1x1 px
        # get its byte count
        self.block_byte_size = int(round(self.block_len_pixels_1d * self.block_len_pixels_1d / self.pixels_per_byte))
        logging.debug(f"Compression: {comp}, "
                      f"pixels_per_byte: {self.pixels_per_byte}, "
                      f"block_len_pixels_1d: {self.block_len_pixels_1d}, "
                      f"block_byte_size: {self.block_byte_size}")

    # @classmethod
    def mip_pack_generator(self):
        """Yields data size to be read from stream + amount of padding applied for packed representation)"""
        tiles_per_mips = zip(*self.calculate_mip_sizes())
        for mip_i, tiles_per_mip in enumerate(tiles_per_mips):
            for tile_i, (height, width, tile_byte_size) in enumerate(tiles_per_mip):
                # get count of h slices, 1 block is 4x4 px, sub-block sizes require a whole block
                num_lines = self.pad_block(height) // self.block_len_pixels_1d
                bytes_per_line = tile_byte_size // num_lines
                logging.debug(f"tile {tile_i}, height {height}, width {width}, num_lines {num_lines}")
                # anything with less than LINE_BYTES gets padding
                padding_per_line = get_padding_size(bytes_per_line, alignment=LINE_BYTES)
                # logging.debug(
                #     f"tile_byte_size {tile_byte_size}, num_lines {num_lines}, bytes_per_line {bytes_per_line}, padding_per_line {padding_per_line}")
                # write the bytes for each line
                for _ in range(num_lines):
                    # get the bytes that represent the blocks of this line and fill the line with padding blocks
                    yield mip_i, tile_i, bytes_per_line, padding_per_line

                # add one fully blank line as padding for odd line counts (ie. last mip)
                if num_lines < 2:
                    yield mip_i, tile_i, 0, LINE_BYTES

    def get_packed_mips(self, mip_infos):
        """From a standard (non-array) DDS, return a list of all mip levels for a TEX, with padding if needed"""
        # logging.info("Packing all mip maps")
        dds = io.BytesIO(self.buffer)
        out = [[] for _ in mip_infos]
        for mip_info in mip_infos:
            mip_info.size_data = 0
        for mip_i, tile_i, data_size, padding_size in self.mip_pack_generator():
            # logging.debug(f"Reading mip {mip_i} {data_size} bytes at {dds.tell()}")
            data = dds.read(data_size)
            # note that this could fail if the levels are already bugged as any padding added to the end overrides the actual value
            # this is per scan line
            mip_infos[mip_i].size_scan = data_size + padding_size
            if data_size:
                mip_infos[mip_i].size_data += data_size + padding_size
            out[mip_i].append(data + b"\x00" * padding_size)
        return [b"".join(lines) for lines in out]

    def unpack_mips(self, trg_tile_i, tex_buffer_data):
        """Restore standard DDS mip stream, unpack the lower mip levels by discarding the padding"""
        logging.info("Unpacking mip maps")
        tex = io.BytesIO(tex_buffer_data)
        with io.BytesIO() as dds:
            for mip_i, tile_i, data_size, padding_size in self.mip_pack_generator():
                data = tex.read(data_size)
                assert len(data) == data_size, f"Tex buffer is shorter than expected, ends at {tex.tell()}"
                if trg_tile_i == tile_i:
                    # logging.debug(f"Writing mip {mip_i} {data_size} bytes at {dds.tell()}")
                    dds.write(data)
                padding = tex.read(padding_size)
                if padding != b"\x00" * len(padding):
                    logging.warning(f"Tex padding is non-zero at {tex.tell()-padding_size}, padding_size {padding_size}")
            return dds.getvalue()

    def pack_mips_pc(self, buffer_infos):
        """Grab the lower mip levels according to the count"""
        tiles_per_mips = list(zip(*self.calculate_mip_sizes()))
        mip_cuts = [self.mipmap_count - b.num_mips for b in buffer_infos]
        buffers = []
        for mip_0 in mip_cuts:
            # get the size for all tiles of the valid mip levels
            bytes_size = sum([tile[2] for mip in tiles_per_mips[mip_0:] for tile in mip])
            # print(mip_0, bytes_size, tile_sizes)
            buffers.append(self.buffer[-bytes_size:])
        return buffers


if __name__ == "__main__":
    m = DdsFile()
    print(m)
    # m.load("C:/Users/arnfi/Desktop/parrot/parrot.pbasecolourtexture.dds")
