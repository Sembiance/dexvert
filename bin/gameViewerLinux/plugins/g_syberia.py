#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Syberia I
# Alex kalumb1@ya.ru

# SYJ to JPG converter by -=CHE@TER=-
# http://www.ctpax-x.org/

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Syberia" # Имя группы в программе
FORMATS_FILES = ["syj","wav","mp3"] # Форматы поддерживаемых архивов
TYPES_FILES = [('SYJ Images', ('*.syj')),('WAV Sound', ('*.wav')),('MP3 Sound', ('*.mp3'))] # Типы файлов в окне "Открыть архив"
GAMES = ["Syberia I"]
AUTHOR = "Alex kalumb1@ya.ru" # Информация об авторе

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["syj",
                            "wav",
                            "mp3"]
        self.sup_types = {"syj":1,
                          "wav":3,
                          "mp3":3}
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
        res = io.BytesIO(f.read(size))
        f.close()

        if format == "syj":
            self.Unpack_SYJ(res)
        elif format == "wav" or format == "mp3":
            self.Unpack_WAV_MP3(res)

    def Unpack_SYJ(self, f):
        im = io.BytesIO()
        im.write(b"\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46")
        im.write(f.getvalue())
        image = Image.open(im)
        self.images = [image]
            
    def Unpack_WAV_MP3(self, f):
        self.sound = f
        
        