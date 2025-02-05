#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# The Second Reproduction
# kalumb1@ya.ru

import os
import struct
import io
from PIL import Image

NAME = "The Second Reproduction"
FORMATS_ARCHIVE = ['nsa']
TYPES_ARCHIVE = [('The Second Reproduction Pack', ('*.nsa'))]
GAMES = ["The Second Reproduction"]
AUTHOR = "Alex Lazov kalumb1@ya.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] # (имя файла, оффсет, размер, формат)
        self.app = app
        self.sup_formats = ["jpg",
                            "ogg",
                            "wav",
                            "mp3"]
        self.sup_types = {"jpg":1,
                          "ogg":3,
                          "wav":3,
                          "mp3":3}
        self.images = []
        self.sound = None
        
    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "nsa":
            self.OpenArchiveNSA(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format in ["png","jpg"]:
            self.Unpack_IMAGE(io.BytesIO(self.file.read(size)))
        if format in ["ogg","wav","mp3"]:
            self.Unpack_SOUND(io.BytesIO(self.file.read(size)))
    
    def OpenArchiveNSA(self,file):
        self.data = [] # Список файлов
        
        f = open(file,"rb")
        
        col = struct.unpack(">H", f.read(2))[0]
        offset_g = struct.unpack(">I", f.read(4))[0]

        for i in range(col):
            name = b""
            while True:
                b = f.read(1)
                if b == b"\x00":
                    break
                name += b
            f.seek(1,1)
            name = name.decode("utf8")
            
            offset = struct.unpack(">I", f.read(4))[0] + offset_g
            size = struct.unpack(">I", f.read(4))[0]
            f.seek(4,1)
            format = name.split(".")[-1].lower()
            if format == "svn-base":
                format = name.split(".")[-2].lower()
            
            self.data.append((name,offset,size,format))
                     
        self.file = f
        
    def Unpack_SOUND(self, f): 
        self.sound = f
        
    def Unpack_IMAGE(self, f):
        self.images = [Image.open(f)]