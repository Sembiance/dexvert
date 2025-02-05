#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Legal Crime (Чикаго 1932 Дон Капоне)

import os, sys, io, struct
from PIL import Image
import numpy as np
import io

NAME = "Legal Crime"
TYPES_FILES = [('bmp Images', ('*.bmp')),('wav Sound', ('*.wav')),('epi Text', ('*.epi')),('config Text', ('*.config')),('map Text', ('*.map')),('tile Text', ('*.tile')),('txt Text', ('*.txt')),('sce Text', ('*.sce'))]
FORMATS_FILES = ["bmp","jpg","wav","epi","config","map","tile","txt","sce"]
GAMES = ["Legal Crime"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["bmp",
                            "wav",
                            "epi",
                            "config",
                            "map",
                            "tile",
                            "txt",
                            "sce"]
        self.sup_types = {"bmp":1,
                          "wav":3,
                          "epi":4,
                          "config":4,
                          "map":4,
                          "tile":4,
                          "txt":4,
                          "sce":4}
        self.images = []
        self.sound = None
        self.text = None

    def open_files(self,files):
        self.data = files
    
    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        size = data_res[2]
        format = data_res[3]
        self.text = None
        f = open(name,"rb")
        f2 = io.BytesIO(f.read(size))
        f.close()

        if format == "bmp":
            self.Unpack_BMP(f2)
        elif format == "wav":
            self.Unpack_WAV(f2)
        elif format in ["epi", "config", "map", "tile", "txt", "sce"]:
            self.Unpack_TXT(f2)

    def Unpack_BMP(self, f):
        type = f.read(2) # Тип архива
        f.seek(0)
        if type == b'\x42\x4D': # Legal Crime
            image = Image.open(f)
            self.images = [image]

        elif type == b'\x8F\x80': # Чикаго 1932 Дон Капоне
            fd = bytearray(f.read())
            for i in range(len(fd)):
                fd[i] = fd[i] ^ 0xCD # XOR байт CD
            f2 = io.BytesIO(fd)
            image = Image.open(f2)
            self.images = [image]
        
    def Unpack_WAV(self, f):
        self.sound = f
        
    def Unpack_TXT(self, f): 
        self.text = f.read().decode("cp1251") # Есть русский текст