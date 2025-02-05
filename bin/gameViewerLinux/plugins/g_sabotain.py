#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Sabotain: Break the Rules(Саботаж - Кулак Империи)

import os, sys, io, struct
import zipfile
from PIL import Image
import numpy as np
import array

NAME = "Sabotage - Break the Rules"
FORMATS_ARCHIVE = ["sab"]
TYPES_ARCHIVE = [('Sabotain: Break the Rules', ('*.sab'))]
GAMES = ["Sabotain: Break the Rules"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["tga",
                            "bmp",
                            "dds",
                            "jpg",
                            "wav",
                            "ogg",
                            "areas",
                            "areas_car",
                            "areas_civ",
                            "c",
                            "txt",
                            "emo",
                            "civ",
                            "con",
                            "que",
                            "scale",
                            "scn",
                            "cfg",
                            "bot",
                            "items",
                            "ma2",
                            "ma3",
                            "mat"]
        self.sup_types = {"tga":1,
                          "bmp":1,
                          "dds":1,
                          "jpg":1,
                          "wav":3,
                          "ogg":3,
                          "areas":4,
                          "areas_car":4,
                          "areas_civ":4,
                          "c":4,
                          "txt":4,
                          "emo":4,
                          "civ":4,
                          "con":4,
                          "que":4,
                          "scale":4,
                          "scn":4,
                          "cfg":4,
                          "bot":4,
                          "items":4,
                          "ma2":4,
                          "ma3":4,
                          "mat":4}

        self.images = []
        self.sound = None
        self.text = None

    def open_data(self,file):
        self.OpenArchive(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]

        file_open = self.file.open(name, mode='r')

        if format in ["tga","bmp","dds","jpg"]:
            self.Unpack_Image(io.BytesIO(file_open.read()))
        elif format == "wav" or format == "ogg":
            self.Unpack_WAV(io.BytesIO(file_open.read()))
        elif format in ["areas", "areas_car","areas_civ","c","emo","civ","con","que","scale","scn","cfg","bot","items","ma2","ma3","mat"]:
            self.Unpack_TXT(io.BytesIO(file_open.read()))
        elif format in ["txt"]:
            self.Unpack_TXT2(io.BytesIO(file_open.read()))
        
    def OpenArchive(self,file):
        self.data = [] # Список файлов

        if not zipfile.is_zipfile(file):
            raise("Это не архив!")

        self.file = zipfile.ZipFile(file)
        for name in self.file.namelist():
            format = name.split(".")[-1].lower()
            offset = 0
            (dirname, filename) = os.path.split(name)
            if filename != "":
                size = self.file.getinfo(name).file_size
                self.data.append((name,offset,size,format,name))

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_Image(self, f):
        self.images = [Image.open(f)]

    def Unpack_TXT(self, f): 
        self.text = f.read().decode("cp1251")

    def Unpack_TXT2(self, f):
        try: # Исключения
            self.text = f.read().decode("utf_16_le")
        except :
            f.seek(0)
            self.text = f.read().decode("cp1251")
