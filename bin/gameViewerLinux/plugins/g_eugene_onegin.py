#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Антон Горев

# Евгений Онегин

import os, sys, io, struct
import zipfile
from PIL import Image
import numpy as np
import array

NAME = "Евгений Онегин"
FORMATS_ARCHIVE = ["PAK"]
TYPES_ARCHIVE = [('Евгений Онегин', ('*.PAK'))]
GAMES = ["Евгений Онегин"]
AUTHOR = "ZetpeR xax007@yandex.ru"


class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["png",
                            "jpg",
                            "wav",
                            "ogg",
                            "cnes"]

        self.sup_types = {"png":1,
                          "jpg":1,
                          "wav":3,
                          "ogg":3,
                          "cnes":4}

        self.images = []
        self.sound = None

    def open_data(self,file):
        self.OpenArchive(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]

        file_open = self.file.open(name, mode='r', pwd=b"putinissatan")

        if format == "png" or format == "jpg":
            self.Unpack_Image(io.BytesIO(file_open.read()))
        elif format == "wav" or format == "ogg":
            self.Unpack_WAV(io.BytesIO(file_open.read()))
        elif format == "cnes":
            self.Unpack_cnes(io.BytesIO(file_open.read()))

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

    def Unpack_cnes(self, f):
        f2 = io.BytesIO()
        f.seek(0,2)
        endf = f.tell()
        f.seek(0)
        check = 0
        while check != endf:
            stringlen = struct.unpack("<I",f.read(4))[0] // 2
            if f.tell() == endf:
                break

            for i in range(stringlen):
                fd = f.read(2)
                xor = b'\xF3\xD2'
                unxored = bytes(a ^ b for (a, b) in zip(fd, xor))
                f2.write(unxored)
                if (unxored == b'\x0D\x00'):
                    f2.write(b'\x0A\x00')
            check = f.tell()
        f2.seek(0)
        self.text = f2.read().decode("utf-16")
        f2.close()
