#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Репортаж

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Репортаж"
TYPES_FILES = [('sfx Images', ('*.sfx')),('anm Sound', ('*.anm'))]
FORMATS_FILES = ["sfx","anm"]
GAMES = ["Репортаж"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["sfx",
                            "anm"]
        self.sup_types = {"sfx":1,
                          "anm":3}
        self.images = []
        self.sound = None

    def open_files(self,files):
        self.data = files
    
    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        size = data_res[2]
        format = data_res[3]

        f = open(name,"rb")
        f2 = io.BytesIO(f.read(size))
        f.close()

        if format == "sfx":
            self.Unpack_BMP(f2)
        elif format == "anm":
            self.Unpack_WAV(f2)

    def Unpack_BMP(self, f):
        type = f.read(2) # Тип файла
        f.seek(0)
        if type == b'\x42\x4D':
            image = Image.open(f)
            self.images = [image]
        
    def Unpack_WAV(self, f):
        type = f.read(2) # Тип файла
        if type == b'\xFF\xFB' or type == b'\x49\x44' or type == b'\x52\x49' : # MP3 и WAV
            self.sound = f

        else:
            print("Не звук")