#!/usr/bin/python

# MIT License

# Copyright (c) 2020 Bernd Moeller

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import struct
import pprint
import argparse

try:
    from termcolor import colored
except ModuleNotFoundError:
    def colored(out, color):
        return out

global DEBUG
DEBUG = False

# The following website was used to get nearly all information
# about the LXO file format:
# https://modosdk.foundry.com/wiki/File_Formats

sENCODINGS = ['System Default', 'ANSI', 'UTF-8', 'Shift-JIS (Japanese)',
              'EUC-JP (Japanese)', 'EUC-KR (Korea KS C 5601)',
              'GB2312 (Simplified Chinese)', 'BIG5 (Traditional Chinese)']


class LXOLayer(object):
    def __init__(self, parent, name, subd_level, psub_level, id):
        self.__parent: LXOFile = parent
        self.name = name
        self.is_subd = False
        self.subd_level = subd_level
        self.psub_level = psub_level
        self.vert_count = 0
        self.poly_count = 0
        self.vmaps = None
        self.reference_id = id
        self.points = []
        self.polygons = []
        self.ptags = {}
        self.materials: dict[str, list] = {}
        self.uv_maps = {}
        self.uv_maps_disco = {}
        self.vertex_normals = {}
        self.vertex_normals_disco = {}

    @property
    def parent(self):
        return self.__parent

    def generate_materials(self):
        if 'MATR' not in self.ptags:
            return
        for data in self.ptags['MATR']:
            poly_index, tag_index = data
            material_name = self.parent.tagnames[tag_index]
            if material_name not in self.materials:
                self.materials[material_name] = []
            self.materials[material_name].append(poly_index)


class ActionLayer(object):
    def __init__(self, name, type, index):
        self.name = name
        self.type = type
        self.index = index
        self.__items: list[ActionLayerItem] = []

    def add_item(self, id):
        item = ActionLayerItem(id)
        self.__items.append(item)
        return item

    def item_iter(self):
        for item in self.__items:
            yield (item.id, item.CHAN, item.string_channels)


class ActionLayerItem(object):
    def __init__(self, id):
        self.id = id
        self.CHAN = []
        self.GRAD = []
        self.string_channels = []


class LXOItem(object):
    def __init__(self, name, id, typename):
        self.id = id
        self.name = name
        self.vname = None
        self.typename = typename
        self.channel = {}
        self.GRAD = []
        # self.stringChannels = []
        self.CHNL = []
        self.CHNV = {}
        self.item_tags = []
        self.packages = []
        self.UCHN = []
        self.CHNC = []
        self.CLNK = []
        self.graph_links = {}
        self.LAYR = None


class LXOFile(object):
    def __init__(self):
        self.version = None
        self.appversion = None
        self.encoding = None
        self.size = 0
        self.type = None
        self.description = None
        self.__items: list[LXOItem] = []
        self.__layers: list[LXOLayer] = []
        self.__action_layers: list[ActionLayer] = []
        self.channel_names = None
        self.data = []
        self.tagnames = None
        self.IASS = dict()

    def add_layer(self, name, subd_level, psub_level, id):
        layer = LXOLayer(self, name, subd_level, psub_level, id)
        self.__layers.append(layer)
        return layer

    def add_action_layer(self, name, type, index):
        action_layer = ActionLayer(name, type, index)
        self.__action_layers.append(action_layer)
        return action_layer

    def add_item(self, name, id, typename):
        item = LXOItem(name, id, typename)
        self.__items.append(item)
        return item

    @property
    def items(self):
        for item in self.__items:
            yield item

    @property
    def layers(self):
        for layer in self.__layers:
            yield layer

    @property
    def action_layers(self):
        for layer in self.__action_layers:
            yield layer

    def pprint(self):
        for key, val in list(vars(self).items()):
            if key == 'channelNames' or key.startswith('_LXOFile_'):
                continue
            print(key, val)

        print('Layers: name polyCount')
        for layer in self.__layers:
            print(layer.name, layer.poly_count)

        print('action layers')
        for actl in self.__action_layers:
            print(actl.name)
            for it in actl.item_iter():
                pprint.pprint(it)

        for item in self.__items:
            print(item.name, item.vname, item.typename)
            for ch, value in item.channel.items():
                print(" ", ch, value)
            for ch in item.GRAD:
                print(" ", ch)
            # for ch in item.stringChannels:
            #     print(" ", ch)
            for ch in item.CHNL:
                print(" ", ch)
            for ch, val in item.CHNV.items():
                print(" ", ch, val)
            for ch in item.item_tags:
                print(" ", ch)
            for ch, val in item.graph_links.items():
                print(" ", ch, val)


class LXOReader(object):
    def __init__(self):
        self.file = None
        self.mod_size = 0
        self.tags_to_read = set()

    def read_id4(self):
        # 4-byte identifier encapsulated in a long.
        # This is usually a string of ASCII values, which can be generated with
        # some bit-shifting and bitwise or'ing like so:
        # ('T' << 24 | 'E' << 16 | 'S' << 8 | 'T').
        self.mod_size -= 4
        val = struct.unpack(">1l", self.file.read(4))[0]
        return (chr(val >> 24) + chr(val >> 16 & 255) +
                chr(val >> 8 & 255) + chr(val & 255))

    def read_u1(self):
        self.mod_size -= 1
        return struct.unpack(">1B", self.file.read(1))[0]

    def read_u14(self):
        self.mod_size -= 4
        return [struct.unpack(">1B", self.file.read(1))[0] for _ in range(4)]

    def read_u1s(self):
        size = self.mod_size
        self.mod_size = 0
        return struct.unpack(">%ss" % size, self.file.read(size))[0]

    def read_u2(self):
        # unsigned short
        self.mod_size -= 2
        return struct.unpack(">1H", self.file.read(2))[0]

    def read_u4(self):
        # unsigned long
        self.mod_size -= 4
        return struct.unpack(">1L", self.file.read(4))[0]

    def read_vx(self):
        # U2 if smaller than 0xFF00 otherwise U4
        val = self.file.read(2)
        out = struct.unpack(">1H", val)[0]
        if out < int('FF00', 16):
            self.mod_size -= 2
            return out
        else:
            val += self.file.read(2)
            val = b'\x00' + val[1:]  # discard first byte, feels hacky...
            self.mod_size -= 4
            return struct.unpack(">1L", val)[0]

    def read_i2(self):
        self.mod_size -= 2
        return struct.unpack(">1h", self.file.read(2))[0]

    def read_i4(self):
        self.mod_size -= 4
        return struct.unpack(">1l", self.file.read(4))[0]

    def read_f4(self):
        self.mod_size -= 4
        return struct.unpack(">1f", self.file.read(4))[0]

    def read_s0(self):
        # NULL-terminated ASCII string. The string is padded to an even number
        # of bytes with a NULL where necessary.
        s0: bytes = b''
        while True:
            s0 += struct.unpack(">1s", self.file.read(1))[0]
            self.mod_size -= 1
            if len(s0) % 2 == 0 and s0.endswith(b'\0'):
                s0 = s0.rstrip(b'\0')
                return s0.decode("utf-8", "ignore")

    def read_int(self):
        self.mod_size -= 4
        return struct.unpack(">1i", self.file.read(4))[0]

    def read_float(self):
        return self.read_f4()

    def read_vec12(self):
        vec = [self.read_f4() for _ in range(3)]
        return vec

    def readblob(self, size=None) -> bytes:
        if size is None:
            raise Exception('need blob size')
        self.mod_size -= size
        cc = b''
        for _ in range(size):
            cc += struct.unpack(">1c", self.file.read(1))[0]
        return cc

    def read_value(self, datatype):
        datatype = int(datatype) & ~0x20  # 33, 34, 35 exist as well...
        if datatype == 1 or datatype == 17:  # integer
            value = self.read_int()
        elif datatype == 2 or datatype == 18:  # float
            value = self.read_float()
        # String representing an integer text hint.
        elif datatype == 3 or datatype == 19:
            value = self.read_s0()
        else:
            raise Exception("unknown datatype")
            # blobsize = subchunkSize - (subsizeSnap - self.modSize)
            # value = self.readblob(blobsize)
        return value

    def read_from_file(self, filepath, load_lights: bool = True, load_meshes: bool = True, load_materials: bool = True, load_cameras: bool = True) -> LXOFile:
        if not filepath or not os.path.isfile(filepath):
            raise Exception('not a file')
        file_size = os.stat(filepath).st_size
        if DEBUG:
            print(file_size)
        lxo_file = LXOFile()
        with open(filepath, 'rb') as srcfile:
            self.file = srcfile
            # read main FORM chunkID and size
            form = struct.unpack(">4s", self.file.read(4))[0]
            size = struct.unpack(">1L", self.file.read(4))[0]
            self.mod_size = size
            scene_type = self.read_id4()
            # throw an error if it's not FORM
            if form != b'FORM':
                raise Exception('not a valid file')

            lxo_file.size = size
            lxo_file.type = scene_type

            self.__read_chunks(lxo_file)
            self.file = None
        return lxo_file

    def __read_chunks(self, lxo_file: LXOFile):
        # read all other chunks
        current_layer = None
        while self.mod_size > 0:
            chunk_id = self.read_id4()
            chunk_size = self.read_u4()
            size_snap = self.mod_size

            # only read the tags specified
            if self.tags_to_read and chunk_id not in self.tags_to_read:
                self.mod_size -= chunk_size
                self.file.seek(chunk_size, 1)
                continue

            if DEBUG:
                print(colored(chunk_id, 'green'), end=" ")

            if chunk_id == 'DESC':
                preset_type = self.read_s0()
                preset_description = self.read_s0()
                if DEBUG:
                    print(preset_type, preset_description)
            elif chunk_id == 'VRSN':
                major = self.read_u4()
                minor = self.read_u4()
                app = self.read_s0()
                lxo_file.version = major
                lxo_file.appversion = app
                if DEBUG:
                    print(major, minor, app)
            elif chunk_id == 'APPV':
                major = self.read_u4()
                minor = self.read_u4()
                unknown = self.read_u4()
                build = self.read_u4()
                level = self.read_s0()
                if DEBUG:
                    print(major, minor, unknown, build, level)
            elif chunk_id == 'ENCO':
                encoding = self.read_u4()
                lxo_file.encoding = encoding
                if DEBUG:
                    print(sENCODINGS[encoding])
            elif chunk_id == 'TAGS':
                tags = []
                while (size_snap - self.mod_size) < chunk_size:
                    tags.append(self.read_s0())
                lxo_file.tagnames = tags
                if DEBUG:
                    print(tags)
            elif chunk_id == 'CHNM':
                count = self.read_u4()
                names = []
                for _ in range(count):
                    names.append(self.read_s0())
                lxo_file.channel_names = names
                if DEBUG:
                    print(names)
            elif chunk_id == 'LAYR':
                index_legacy = self.read_u2()
                flags = self.read_u2()
                rot_pivot = self.read_vec12()
                name = self.read_s0()
                parent_legacy = self.read_i2()
                refine_subd = self.read_f4()
                refine_crvs = self.read_f4()
                scl_pivot = self.read_vec12()
                for i in range(6):
                    unused = self.read_u4()
                item_reference = self.read_u4()
                refine_spl_ptch = self.read_u2()
                for i in range(4):
                    unused = self.read_u2()
                cc_renderlvl = self.read_u2()
                cc_previewlvl = self.read_u2()
                subd_renderlvl = self.read_u2()
                blobsize = chunk_size - (size_snap - self.mod_size)
                blob = self.readblob(blobsize)
                # add layer to lxoFile
                # TODO: add all properties to layer
                current_layer = lxo_file.add_layer(name, refine_subd,
                                                cc_previewlvl,
                                                item_reference)
                if DEBUG:
                    print("", name, item_reference)
            elif chunk_id == 'POLS':
                poly_type = self.read_id4()
                if poly_type in ['SUBD', 'PSUB']:
                    current_layer.is_subd = True
                # TODO figure this out
                if poly_type in ['FACE', 'SUBD', 'PSUB']:
                    poly_count = 0
                    while (size_snap - self.mod_size) < chunk_size:
                        # TODO make this proper code
                        vert_count = self.read_u2()
                        poly_points = []
                        for i in range(vert_count):
                            vert_index = self.read_vx()
                            poly_points.append(vert_index)
                        current_layer.polygons.append(poly_points)
                    current_layer.poly_count += poly_count
                else:
                    blobsize = chunk_size - (size_snap - self.mod_size)
                    polygons = self.readblob(blobsize)
                if DEBUG:
                    print(poly_type, poly_count)
            elif chunk_id == 'PNTS':
                points = []
                while (size_snap - self.mod_size) < chunk_size:
                    points.append(self.read_vec12())
                current_layer.points = points
                if DEBUG:
                    print(len(points))
            elif chunk_id == 'VMAP':
                map_type = self.read_id4()
                dimension = self.read_u2()
                name = self.read_s0()
                values = {}
                while (size_snap - self.mod_size) < chunk_size:
                    index = self.read_vx()
                    vv = []
                    for _ in range(dimension):
                        vv.append(self.read_float())
                    values[index] = vv
                if map_type == 'TXUV':
                    current_layer.uv_maps[name] = values
                elif map_type == 'NORM':
                    current_layer.vertex_normals[name] = values
                if DEBUG:
                    print(map_type, dimension, name, len(values))
            elif chunk_id == 'VMAD':
                map_type = self.read_id4()
                dimension = self.read_u2()
                name = self.read_s0()
                values = {}
                while (size_snap - self.mod_size) < chunk_size:
                    vert_index = self.read_vx()
                    poly_index = self.read_vx()
                    vv = []
                    for _ in range(dimension):
                        vv.append(self.read_float())
                    if poly_index in values:
                        values[poly_index][vert_index] = vv
                    else:
                        values[poly_index] = {vert_index: vv}
                if map_type == 'TXUV':
                    current_layer.uv_maps_disco[name] = values
                elif map_type == 'NORM':
                    current_layer.vertex_normals_disco[name] = values
                if DEBUG:
                    print(map_type, dimension, name, len(values))
            elif chunk_id == 'PTAG':
                # MATR, PART, PICK, FONT, JUST, TEXT, SMGP
                tag_type = self.read_id4()
                ptags = []
                while (size_snap - self.mod_size) < chunk_size:
                    pols_index = self.read_vx()
                    tags_index = self.read_u2()
                    ptags.append((pols_index, tags_index))
                current_layer.ptags[tag_type] = ptags
                if DEBUG:
                    print(tag_type, ptags)
            elif chunk_id == 'ENVL':
                index = self.read_vx()
                envl_type = self.read_u4()
                blobsize = chunk_size - (size_snap - self.mod_size)
                subchunks = self.readblob(blobsize)  # TODO
                if DEBUG:
                    print(index, envl_type)
            elif chunk_id == 'BBOX':
                min_xyz = self.read_vec12()
                max_xyz = self.read_vec12()
                if DEBUG:
                    print(min_xyz, max_xyz)
            elif chunk_id == 'ITEM':
                typename = self.read_s0()
                name = self.read_s0()
                reference_id = self.read_u4()
                item = lxo_file.add_item(name, reference_id, typename)

                if DEBUG:
                    print(typename, name, reference_id)

                while (size_snap - self.mod_size) < chunk_size:
                    subchunk_id = self.read_id4()
                    subchunk_size = self.read_u2()
                    subsize_snap = self.mod_size

                    # only read the tags specified
                    if (self.tags_to_read and
                            chunk_id + subchunk_id not in self.tags_to_read):
                        self.mod_size -= subchunk_size
                        self.file.seek(subchunk_size, 1)
                        continue

                    if DEBUG:
                        print("", colored(subchunk_id, 'yellow'), end=" ")

                    if subchunk_id == 'PAKG':
                        package_name = self.read_s0()
                        reserved = self.read_u4()
                        item.packages.append(package_name)
                        if DEBUG:
                            print(package_name, reserved)
                    elif subchunk_id == 'XREF':
                        index_sub_scene = self.read_u4()
                        filename = self.read_s0()
                        item_id = self.read_s0()
                        if DEBUG:
                            print(index_sub_scene, filename, item_id)
                    elif subchunk_id == 'LAYR':
                        index = self.read_u4()
                        flags = self.read_u4()
                        rgbs = self.read_u14()
                        item.LAYR = (index, flags, rgbs)
                        if DEBUG:
                            print(index, flags, rgbs)
                    elif subchunk_id == 'LINK':
                        graphname = self.read_s0()
                        item_index = self.read_i4()
                        link_index = self.read_i4()
                        # TODO handle properly
                        if graphname not in item.graph_links:
                            item.graph_links[graphname] = (item_index, link_index)
                        else:
                            if DEBUG:
                                print(colored("ERROR duplicate graph link",
                                              'red'),)
                                print(graphname, item_index, link_index)
                        if DEBUG:
                            print(graphname, item_index, link_index)
                    elif subchunk_id == 'CHNL':
                        name = self.read_s0()
                        datatype = self.read_u2()
                        value = self.read_value(datatype)
                        item.CHNL.append((name, datatype, value))
                        if DEBUG:
                            print(name, datatype, value)
                    elif False and subchunk_id == 'GRAD':
                        # TODO:
                        blobsize = subchunk_size - (subsize_snap - self.mod_size)
                        blob = self.readblob(blobsize)
                        item.GRAD.append(blob)
                    elif False and subchunk_id == 'CLNK':
                        # TODO:
                        blobsize = subchunk_size - (subsize_snap - self.mod_size)
                        blob = self.readblob(blobsize)
                        item.CLNK.append(blob)
                    elif False and subchunk_id == 'UCHN':
                        # TODO:
                        blobsize = subchunk_size - (subsize_snap - self.mod_size)
                        blob = self.readblob(blobsize)
                        item.CLNK.append(blob)
                    elif subchunk_id == 'CHNS':
                        name = self.read_s0()
                        value = self.read_s0()
                        item.channel[name] = value
                        if DEBUG:
                            print(name, value)
                    elif subchunk_id == 'CHAN':
                        index = self.read_vx()
                        datatype = self.read_u2()
                        value = self.read_value(datatype)
                        item.channel[lxo_file.channel_names[index]] = value
                        if DEBUG:
                            print(lxo_file.channel_names[index], datatype, value)
                    elif subchunk_id == 'CHNV':
                        name = self.read_s0()
                        datatype = self.read_u2()
                        vectorcount = self.read_u2()
                        vec = []
                        for i in range(vectorcount):
                            cname = self.read_s0()
                            value = self.read_value(datatype)
                            vec.append((cname, value))
                        item.CHNV[name] = vec  # datatype?
                        if DEBUG:
                            print(name, vec)
                    elif subchunk_id == 'ITAG':
                        itag_type = self.read_id4()
                        value = self.read_s0()
                        item.item_tags.append((itag_type, value))
                        if DEBUG:
                            print(itag_type, value)
                    elif subchunk_id == 'VNAM':
                        name = self.read_s0()
                        item.vname = name
                        if DEBUG:
                            print(name)
                    elif subchunk_id == 'UNIQ':
                        identifier = self.read_s0()
                        if DEBUG:
                            print(identifier)
                    elif subchunk_id == 'UIDX':
                        index = self.read_u4()
                        if DEBUG:
                            print(index)
                    elif subchunk_id == 'CHNC':
                        size = self.read_u2()
                        data = ""
                        for i in range(size):
                            data += self.read_u1()
                        item.CHNC.append(data)
                        if size % 2:
                            # if uneven length read one more byte
                            self.read_u1()
                        if DEBUG:
                            print(data)
                    elif subchunk_id == 'BCHN':
                        operation_type = self.read_s0()
                        data = self.read_u4()
                        if DEBUG:
                            print(operation_type, data)
                    else:
                        blobsize = subchunk_size - (subsize_snap - self.mod_size)
                        blob = self.readblob(blobsize)
                        if DEBUG:
                            print(colored("BLOB", "red"), blob)
            elif chunk_id == 'ACTN':  # action layers: edit, scene, setup
                self.__read_actn(lxo_file, size_snap, chunk_size)
            else:
                self.mod_size -= chunk_size
                self.file.seek(chunk_size, 1)  # skipping chunk
                if DEBUG:
                    print(colored("BLOB skipped", "red"))

    def __read_actn(self, lxo_file: LXOFile, size_snnap, chunk_size):
        actionlayername = self.read_s0()
        actionlayertype = self.read_s0()
        actionlayerindex = self.read_u4()
        action_layer = lxo_file.add_action_layer(actionlayername,
                                             actionlayertype,
                                             actionlayerindex)
        current_action_item = None

        if DEBUG:
            print(actionlayername, actionlayertype, actionlayerindex)

        while (size_snnap - self.mod_size) < chunk_size:
            subchunk_id = self.read_id4()
            subchunk_size = self.read_u2()
            subsize_snap = self.mod_size

            if (self.tags_to_read and
                    chunk_id + subchunk_id not in self.tags_to_read):
                self.mod_size -= subchunk_size
                self.file.seek(subchunk_size, 1)
                continue

            if DEBUG:
                print("", colored(subchunk_id, 'yellow'), end=" ")

            if subchunk_id == 'ITEM':
                item_reference_id = self.read_u4()
                current_action_item = action_layer.add_item(item_reference_id)
                if DEBUG:
                    print(item_reference_id)
            elif subchunk_id == 'CHAN':
                index = self.read_vx()
                datatype = self.read_u2()
                index_envl = self.read_vx()
                value = self.read_value(datatype)
                data = (lxo_file.channel_names[index], datatype, index_envl,
                        value)
                current_action_item.CHAN.append(data)
                if DEBUG:
                    print(lxo_file.channel_names[index], datatype,
                          index_envl, value)
            elif subchunk_id == 'GRAD':
                # TODO:
                blobsize = subchunk_size - (subsize_snap - self.mod_size)
                blob = self.readblob(blobsize)
                current_action_item.GRAD.append(blob)
                if DEBUG:
                    print(blob)
            elif subchunk_id == 'CHNS':
                name = self.read_s0()
                index = self.read_vx()
                value = self.read_s0()
                data = (name, lxo_file.channel_names[index], value)
                current_action_item.string_channels.append(data)
                if DEBUG:
                    print(lxo_file.channel_names[index], value, name)
            else:
                # TODO figure out what PRNT subchunk is for
                blobsize = subchunk_size - (subsize_snap - self.mod_size)
                blob = self.readblob(blobsize)
                if DEBUG:
                    print(colored("BLOB", "red"), blob)


if __name__ == '__main__':
    desc = 'Read (specific) stuff from LXO.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("--source-file", dest="source_file", help="source FILE", metavar="FILE")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-p", "--pretty-print", dest="pretty_print", action="store_true")

    args = parser.parse_args()
    if args.debug:
        print('enabled DEBUG print')
        DEBUG = True

    lxoRead = LXOReader()
    # lxoRead.tagsToRead = []

    lxo = lxoRead.read_from_file(args.source_file)

    if args.pretty_print:
        print('### pprint ###')
        lxo.pprint()
