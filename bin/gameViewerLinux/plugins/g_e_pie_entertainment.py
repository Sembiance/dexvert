#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Shanghai Dragon(Шанхайский дракон)
# Great Qin Warriors
# Vietnam War: Ho Chi Min Trail

import os, sys, io, struct
from PIL import Image
import zlib

NAME = "E-Pie Entertainment"
FORMATS_ARCHIVE = ['pck']
TYPES_ARCHIVE = [('E-Pie Entertainment', ('*.pck'))]
GAMES = ["Shanghai Dragon",
         "Great Qin Warriors",
         "Vietnam War: Ho Chi Min Trail"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["bmp",
                            "tga",
                            "wav",
                            "mp3",
                            "gfx",
                            "res",
                            "sdr",
                            "txt",
                            "mod",
                            "im",
                            "imd"]  

        self.sup_types = {"bmp":1,
                          "tga":1,
                          "wav":3,
                          "mp3":3,
                          "gfx":4,
                          "res":4,
                          "sdr":4,
                          "txt":4,
                          "mod":4,
                          "im":4,
                          "imd":4}

        self.images = []
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "pck":
            self.OpenArchivePCK(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "bmp" or format == "tga":
            fd = self.file.read(size)
            if data_res[4] == 1: # Распаковка сжатия
                fd = zlib.decompress(fd)
            self.Unpack_TGA(io.BytesIO(fd))
        elif format == "wav" or format == "mp3":
            fd = self.file.read(size)
            if data_res[4] == 1: # Распаковка сжатия
                fd = zlib.decompress(fd)
            self.Unpack_WAV(io.BytesIO(fd))
        elif format in ["gfx", "res", "sdr", "txt","mod", "im","imd"]:
            fd = self.file.read(size)
            if data_res[4] == 1: # Распаковка сжатия
                fd = zlib.decompress(fd)
            self.Unpack_TXT(io.BytesIO(fd))

    def OpenArchivePCK(self,file):
        f = open(file,"rb")

        f.seek(-(4+256+4+4),2)
        offset_tab = struct.unpack("<I",f.read(4))[0] # Оффсет начало таблицы файлов
        f_path = f.read(256).split(b"\x00")[0].decode("utf8")
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        unclear = struct.unpack("<I",f.read(4))[0] # Непонятно
        #print("Файлов",col,offset_tab,f_path,unclear)
        f.seek(offset_tab)

        for i in range(col):
            number_letters = struct.unpack("<I",f.read(4))[0] # Длина имени
            f_path = f.read(number_letters).split(b"\x00")[0].decode("gb18030")
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size = struct.unpack("<I",f.read(4))[0] # Размер без сжатия
            size_2 = struct.unpack("<I",f.read(4))[0] # Размер Размер сжатого файла
            format = f_path.split(".")[-1].lower()
            if size == size_2:
                self.data.append((f_path,offset,size,format,0)) # Без сжатия
            else:
               self.data.append((f_path,offset,size,format,1))
        self.file = f

    def Unpack_WAV(self, f): 
        self.sound = f

    def Unpack_TXT(self, f): 
        self.text = f.read().decode("gb18030")

    def Unpack_TGA(self, f):
        image = Image.open(f)
        self.images = [image]