#!/usr/bin/python3
# by Joric, https://github.com/joric/io_scene_b3d

import os
import struct

class B3DParser:
    def __init__(self):
        self.fp = None

    def gets(self):
        s = b''
        while True:
            c = self.fp.read(1)
            if c == b'\x00':
                return s.decode(errors='ignore')
            s += c

    def i(self,n):
        return struct.unpack(n*'i', self.fp.read(n*4))

    def f(self,n):
        return struct.unpack(n*'f', self.fp.read(n*4))

    def next_chunk(self):
        pos = self.fp.tell()
        s1,s2,s3,s4, size = struct.unpack('4ci', self.fp.read(8))
        chunk = ''.join([chr(ord(x)) for x in (s1,s2,s3,s4)])
        next = pos + size + 8
        return chunk, pos, size, next

    def cb_result(self):
        return True

    def parse(self, filepath):
        filesize = os.stat(filepath).st_size
        self.fp = open(filepath,'rb')
        stack = []
        while self.fp.tell() <= filesize-8:

            while stack and stack[-1]==self.fp.tell():
                del stack[-1]
                self.cb_prev()

            chunk, pos, size, next = self.next_chunk()

            if chunk=='BB3D':
                self.cb_data(chunk, {'version': self.i(1)[0]})
                continue

            if chunk=='ANIM':
                flags, frames = self.i(2)
                fps = self.f(1)[0]
                self.cb_data(chunk, {'flags':flags, 'frames':frames, 'fps':fps})

            elif chunk=='TEXS':
                data = []
                while self.fp.tell()<next:
                    name = self.gets()
                    flags, blend = self.i(2)
                    pos = self.f(2)
                    scale = self.f(2)
                    rot = self.f(1)[0]
                    data.append(dotdict({'name':name,'position':pos,'scale':scale,'rotation':rot}))
                self.cb_data(chunk,{'textures':data})

            elif chunk=='BRUS':
                n_texs = self.i(1)[0]
                data = []
                while self.fp.tell()<next:
                    name = self.gets()
                    rgba = self.f(4)
                    shine = self.f(1)[0]
                    blend, fx = self.i(2)
                    tids = self.i(n_texs)
                    data.append(dotdict({'name':name, 'rgba':rgba,'shine':shine, 'blend':blend,'fx':fx,'tids':tids}))
                self.cb_data(chunk, {'materials':data})

            elif chunk=='NODE':
                self.cb_next()
                stack.append(next)
                name = self.gets()
                p = self.f(3)
                s = self.f(3)
                r = self.f(4)
                self.cb_data(chunk, {'name':name, 'position':p, 'rotation':r, 'scale':s})
                continue

            elif chunk=='BONE':
                bones = []
                while self.fp.tell()<next:
                    vertex_id = self.i(1)[0]
                    weight = self.f(1)[0]
                    bones.append((vertex_id, weight))
                self.cb_data(chunk,{'bones': bones})

            elif chunk=='MESH':
                self.cb_data(chunk, {'brush_id': self.i(1)[0]})
                #self.cb_next()
                #stack.append(next)
                continue

            elif chunk=='VRTS':
                flags, tcs, tcss = self.i(3)
                v,n,c,u = [],[],[],[]
                while self.fp.tell()<next:
                    v.append(self.f(3))
                    if flags & 1: n.append(self.f(3))
                    if flags & 2: c.append(self.f(4))
                    if tcs*tcss: u.append(self.f(tcs*tcss))
                self.cb_data(chunk, {'vertices':v, 'normals':n, 'rgba':c, 'uvs':u})

            elif chunk=='TRIS':
                brush_id = self.i(1)[0]
                faces = []
                while self.fp.tell()<next:
                    vertex_id = self.i(3)
                    faces.append(vertex_id)
                self.cb_data(chunk, {'brush_id':brush_id, 'indices':faces})

            elif chunk=='KEYS':
                flags = self.i(1)[0]
                keys = []
                while self.fp.tell()<next:
                    key = dotdict({'frame':self.i(1)[0]})
                    if flags & 1: key['position'] = self.f(3)
                    if flags & 2: key['scale'] = self.f(3)
                    if flags & 4: key['rotation'] = self.f(4)
                    keys.append(key)
                self.cb_data(chunk, keys)

            self.fp.seek(next)

        return self.cb_result()


class B3DDebugParser(B3DParser):
    def __init__(self):
        B3DParser.__init__(self)
        self.level = 0

    def cb_next(self):
        self.level += 1

    def cb_prev(self):
        self.level -= 1

    def cb_data(self, chunk, data):
        print(' '*self.level, end='')
        print(chunk, data)


class dotdict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__


class B3DList(B3DParser):
    def __init__(self):
        B3DParser.__init__(self)
        self.index = -1
        self.data = dotdict()
        self.data.nodes = []

    def cb_next(self):
        self.data.nodes.append(dotdict())
        parent = self.index
        self.index = len(self.data.nodes)-1
        self.data.nodes[self.index].parent = parent

    def cb_prev(self):
        self.index = self.data.nodes[self.index].parent

    def cb_data(self, chunk, data):
        if self.index != -1:
            node = self.data.nodes[self.index]

        if chunk in ['NODE','MESH','VRTS','BONE']:
            node.update(data)
        elif chunk=='TRIS':
            if 'faces' not in node:
                node.faces = []
            node.faces.append(dotdict(data))
        elif chunk=='KEYS':
            if 'keys' not in node:
                node['keys'] = []
            node['keys'].extend(data)
        elif chunk in ['ANIM', 'TEXS', 'BRUS']:
            self.data.update(data)

    def cb_result(self):
        return self.data


class B3DTree(B3DList):
    def __init__(self):
        B3DList.__init__(self)

    def cb_result(self):
        tree = []
        nodes = self.data.nodes

        for node in nodes:
            node.nodes = []

        for i, node in enumerate(nodes):
            if node.parent == -1:
                tree.append(node)
            else:
                nodes[node.parent].nodes.append(node)
            del node['parent']

        self.data.update({'nodes':tree})
        return self.data

def dump(node, level=0):
    for node in node.nodes:
        print(node.name)
        dump(node, level+1)

if __name__ == '__main__':
    import sys
    if len(sys.argv)<2:
        print('Usage: B3DParser.py [filename.b3d]')
        sys.exit(0)
    filepath = sys.argv[1]
    #B3DDebugParser().parse(filepath) # text dump
    #data = B3DList().parse(filepath) # json list
    data = B3DTree().parse(filepath) # json tree
    import json
    print(json.dumps(data, indent=1))
    #dump(data)

