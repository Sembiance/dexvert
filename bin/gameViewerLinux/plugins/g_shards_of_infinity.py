#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru

# Shards of Infinity

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Shards of Infinity" 
FORMATS_ARCHIVE = [".xpack"]
TYPES_ARCHIVE = [('Shards of Infinity', ("*.xpack"))]
GAMES = ["Shards of Infinity"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["3",
                            "ogg"]

        self.sup_types = {"3":1,
                          "ogg":3}
        self.images = []  
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "xpack":
            self.OpenArchivexpack(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "3":
            self.Unpack_3(io.BytesIO(self.file.read(size)))

        elif format == "ogg":
            self.Unpack_OGG(io.BytesIO(self.file.read(size)))

    def OpenArchivexpack(self,file):
        f = open(file,"rb")
        type = f.read(4) # Тип архива
        if type != b'KCPX': # Проверка на архив
            print("ЭТО НЕ АРХИВ",type,mult_file)
            return(0) # Остановка скрипта

        unclear = struct.unpack("<I",f.read(4))[0] # Непонятно
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов

        for i in range(col):
            unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно Тип файла ?
            unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно
            unclear_3 = struct.unpack("<I",f.read(4))[0] # Непонятно
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size = struct.unpack("<I",f.read(4))[0] # Размер
            unclear_4 = struct.unpack("<I",f.read(4))[0] # Непонятно размер непонятно заголовка ?
            unclear_5 = struct.unpack("<I",f.read(4))[0] # Непонятно
            unclear_6 = struct.unpack("<I",f.read(4))[0] # Непонятно
            unclear_7 = struct.unpack("<I",f.read(4))[0] # Непонятно
            unclear_8 = struct.unpack("<I",f.read(4))[0] # Непонятно
            f_path = f.read(128).split(b"\x00")[0].decode("utf8")

            if unclear_1 == 21: # Звук ogg
                if unclear_4 == 72:
                    offset += 72 # Пропускаем непонятный заголовок
                    size -= 72
                    f_path += ".ogg"
                else:
                    f_path += ".oggbin" # Непонятный звуковой файл

            elif unclear_1 == 3: # Картинка
                if unclear_4 == 88: # Файл с картинкой
                    f_path += "."+str(unclear_1)

                else: # Файлы без картинки
                    f_path += ".3bin"
            else:
                f_path += "."+str(unclear_1)

            format = f_path.split(".")[-1].lower()
            self.data.append((f_path, offset, size, format))

        self.file = f

    def Unpack_OGG(self, f):
        self.sound = f

    def Unpack_3(self, f):
        f.seek(16)
        w, h = struct.unpack("<II",f.read(8)) # Ширина и высота
        f.seek(88)
        f_image = Image.frombuffer('RGBA', (w,h), f.read(w*h*4), 'raw', 'BGRA', 0, 1)
        self.images.append(f_image)
