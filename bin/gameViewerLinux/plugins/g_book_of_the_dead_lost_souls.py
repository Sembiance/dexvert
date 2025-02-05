#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Книга мертвых Потерянные души
# Красный Космос

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Книга мертвых Потерянные души"
FORMATS_ARCHIVE = ['pak']
TYPES_ARCHIVE = [('Книга мертвых Потерянные души', ('*.pak'))]
GAMES = ["Книга мертвых Потерянные души",
         "Красный Космос"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["bmp",
                            "jpg",
                            "ico",
                            "wav",
                            "scn"]

        self.sup_types = {"bmp":1,
                          "jpg":1,
                          "ico":1,
                          "wav":3,
                          "scn":4}
        self.images = []   
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "pak":
            self.OpenArchivePAK(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "bmp" or format == "jpg" or format == "ico":
            self.Unpack_BMP(io.BytesIO(self.file.read(size)))
        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))
        elif format == "scn":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))

    def OpenArchivePAK(self,file):
        data2 = [] # Список без оффсета
        f = open(file,"rb")
        col_f = int(f.read(4).decode("cp1251")) # Количество файлов
        for i in range(col_f):
            name_length = int(f.read(4).decode("cp1251")) # Длина имени
            filename = f.read(name_length).split(b"\x00")[0].decode("cp1251").replace("\\\\","\\")
            format = filename.split(".")[-1].lower()
            size = int(f.read(10).decode("cp1251"))   # Размер
            offset = int(f.read(10).decode("cp1251")) # Оффсет  
            data2.append((filename,offset,size,format))

        offset = f.tell()
        for i in data2:
            self.data.append((i[0],offset,i[2],i[3]))
            offset += i[2]
        self.file = f

    def Unpack_BMP(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_WAV(self, f):
        self.sound = f
        
    def Unpack_TXT(self, f):
        type = f.read(2)
        f.seek(0)
        if type != b'\x2F\x2F': # Проверка
            f2 = io.BytesIO()
            f.seek(0,2)
            end_f = f.tell()
            f.seek(0)
            for i in range(end_f):
                fd = struct.unpack("B",f.read(1))[0]
                if fd != 0: # Чтоб не отнять от 0
                    fd -= 1
                    fd = struct.pack("B", fd) # Получаем байт
                    f2.write(fd)
                else:
                    f2.write(b'\xFF')
            f2.seek(0)
            self.text = f2.read().decode("cp1251")
        else:
            self.text = f.read().decode("cp1251")