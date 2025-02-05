#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Blood Code
# kalumb1@ya.ru

import os, sys
import struct
import pickle
import zlib
import io
import random
import base64
import binascii
from PIL import Image

NAME = "Blood Code"
FORMATS_ARCHIVE = ['rpa']
TYPES_ARCHIVE = [('Blood Code Pack', ('*.rpa'))]
GAMES = ["Blood Code"]
AUTHOR = "Alex Lazov kalumb1@ya.ru"

def sha1(code):
    fl = int("".join([item for item in code if item.isdigit()]))
    return int(round(pow(fl + int(str(101 * int(random.SG_MAGICCONST)) + str(33)) ** int(str(random.BPF)[0]), float(1) / int(str(random.BPF)[1]))) / 79 * int(str(int(str(random.BPF)[0]) + 1) + str(int(str(random.BPF)[1]) + 1) + str(int(str(random.BPF)[0]) + int(random.SG_MAGICCONST))))

def read64(file):
    return io.BytesIO(base64.decodestring(binascii.unhexlify(file.read(160))) + base64.decodestring(base64.b64decode(file.read(128)) + file.read(88)[::-1]) + file.read())

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] # (имя файла, оффсет, размер, формат)
        self.app = app
        self.sup_formats = ["png",
                            "jpg",
                            "ico",
                            "ogg"]
        self.sup_types = {"png":1,
                          "jpg":1,
                          "ico":1,
                          "ogg":3}
        self.images = []
        self.sound = None
        
    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "rpa":
            self.OpenArchiveRPA(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        prefix = data_res[4]
        self.file.seek(offset)
        if format in ["png","jpg", "ico"]:
            self.Unpack_IMAGE(read64(io.BytesIO(prefix+self.file.read(size))))
        if format == "ogg":
            self.Unpack_SOUND(read64(io.BytesIO(prefix+self.file.read(size))))
    
    def OpenArchiveRPA(self,file):
        self.data = [] # Список файлов
            
        def deobfuscate_index(index, key):
            for k in index.keys():
                if len(index[k][0]) == 2:
                    index[k] = [ (offset ^ key, dlen ^ key, b"") for offset, dlen in index[k] ]
                else:
                    index[k] = [ (offset ^ key, dlen ^ key, start) for offset, dlen, start in index[k] ]
            return index

        
        f = open(file,"rb")

        sign = f.read(8)
        if sign == b"RPA-ZiX ":
            f.seek(8)
            indexoffset = int(f.read(16), 16)
            key = sha1("28e0a530db528e1c88fcf4b40c175bf30a2751bc")
            
            f.seek(indexoffset)
            indexcomp = f.read()
            index = pickle.loads(zlib.decompress(indexcomp),encoding='bytes')
            index = deobfuscate_index(index, key)
            
            for item, data in index.items():
                if type(item) == bytes:
                    item = item.decode("utf8")
                format = item.split(".")[-1].lower()
                self.data.append((item, data[0][0], data[0][1]-len(data[0][2]), format, data[0][2]))
                     
        self.file = f
        
    def Unpack_SOUND(self, f): 
        self.sound = f
        
    def Unpack_IMAGE(self, f):
        self.images = [Image.open(f)]