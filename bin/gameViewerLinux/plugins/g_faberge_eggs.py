#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Яйца Фаберже. Приключение

import os, sys, io, struct
import zipfile
from PIL import Image
import numpy as np
import array

NAME = "Яйца Фаберже. Приключение"
FORMATS_ARCHIVE = ["zip"]
TYPES_ARCHIVE = [('Яйца Фаберже. Приключение', ('*.zip'))]
GAMES = ["Яйца Фаберже. Приключение"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["dds",
                            "dds1",
                            "jpeg",
                            "wav",
                            "anim",
                            "fx",
                            "lua",
                            "qpr",
                            "txt"]
        self.sup_types = {"dds":1,
                          "dds1":1,
                          "jpeg":1,
                          "wav":3,
                          "anim":4,
                          "fx":4,
                          "lua":4,
                          "qpr":4,
                          "txt":4}

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

        if format in ["dds","dds1","jpeg"]:
            self.Unpack_Image(io.BytesIO(file_open.read()))
        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(file_open.read()))
        elif format in ["anim", "fx","lua","qpr","txt"]:
            self.Unpack_TXT(io.BytesIO(file_open.read()))

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
