#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Канитель по беспределу (Руля и Сева)

import os, sys, io, struct
from PIL import Image
import numpy as np
import io

NAME = "Канитель по беспределу" 
FORMATS_ARCHIVE = ["GMD"]
TYPES_ARCHIVE = [('Канитель по беспределу', ("*.GMD"))]
GAMES = ["Канитель по беспределу"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["bmp",
                            "txt",
                            "wav"]
       
        self.sup_types = {"bmp":1,
                          "txt":4,
                          "wav":3}
        self.images = []  
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "gmd":
            self.OpenArchiveDAT(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "bmp":
            self.Unpack_BMP(io.BytesIO(self.file.read(size)))
        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))
        elif format == "txt":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))

    def OpenArchiveDAT(self,file):
        self.data = []

        f = open(file,"rb")

        f2 = open(file[:-4]+".gam","rb") # Таблица файлов
        f2.seek(0,2)
        end_f = f2.tell()
        f2.seek(0)
    
        while f2.tell() != end_f:
            name_length = struct.unpack("B",f2.read(1))[0] # Длина имени файла
            filename = f2.read(name_length).decode('utf-8') # Преобразования байтов в строку,имя файла
            format = filename.split(".")[-1].lower()
            f2.read(15 - name_length) # Ненужные байты
            size = struct.unpack("<I",f2.read(4))[0] # Размер
            offset = struct.unpack("<I",f2.read(4))[0] # Оффсет
            self.data.append((filename,offset,size,format))
        f2.close()
        self.file = f
        
    def Unpack_WAV(self, f):
        self.sound = f
        
    def Unpack_BMP(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_TXT(self, f): 
        f2 = io.StringIO() # Виртуальный файл для текста

        f.seek(0,2)
        end_f = f.tell()
        f.seek(0)
        
        octatok = end_f % 153 # Остаток от деления
        if octatok == 0: # Текст игровой
            for i in range(end_f // 153):
                f.read(3) # Непонятно
                name_length = struct.unpack("B",f.read(1))[0] # Длина
                line_text = f.read(name_length).decode('cp1251') # Преобразования байтов в строку
                f.read(149 - name_length) # Ненужные байты, нули
                f2.write(str(line_text)+"\n")

            f2.seek(0)
            self.text = f2.read()

        else: # Обычный текст с русскими буквами
            self.text = f.read().decode("cp1251")