#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Druuna Morbus Gravis (Друуна. Morbus Gravis)

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Druuna Morbus Gravis"
FORMATS_ARCHIVE = ['dat', 'imf']
TYPES_ARCHIVE = [('Druuna Morbus Gravis', ('*.dat','*.imf'))]
GAMES = ["Druuna Morbus Gravis"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["bmp",
                            "jpg",
                            "wav",
                            "sea"]

        self.sup_types = {"bmp":1,
                          "jpg":1,
                          "wav":3,
                          "sea":4}
        self.images = []   
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "dat":
            self.OpenArchiveDAT(file)
        elif format == "imf":
            self.OpenArchiveIMF(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "bmp" or format == "jpg":
            self.Unpack_BMP(io.BytesIO(self.file.read(size)))
        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))
        elif format == "sea":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))

    def OpenArchiveDAT(self,file):
        f = open(file,"rb")
        type = f.read(4) # Тип архива BANK
        if type != b'\x42\x41\x4E\x4B':
            print("ЭТО НЕ АРХИВ",type)
            return(0) 

        col_f = struct.unpack("<I",f.read(4))[0]  # Количество файлов
        offset = struct.unpack("<I",f.read(4))[0] # Оффсет первого файла
        for i in range(col_f):
            length_name = struct.unpack("<I",f.read(4))[0] # Длина имени
            filename = f.read(length_name).split(b"\x00")[0].decode("cp1251").replace("\\\\","\\")# Имя файла
            format = filename.split(".")[-1].lower()
            size = struct.unpack("<I",f.read(4))[0] # Размер
            self.data.append((filename,offset,size,format))
            offset += size # Чтоб узначть начало следующего файла
        self.file = f

    def OpenArchiveIMF(self,file):
        f = open(file,"rb")
        right_name = file.rfind('.') # Ищем / С права на строчке
        name_f = file[:right_name+1] # Сделано специально чтоб открыть файл .hdr с размерами
        f2 = open(name_f+"hdr","r") # Файл с размерами
        data2 = [] # Оффсеты и размеры файлов
        ss = 0
        offset = 0
        line1 = f2.readline() # Читает одну строчку
        line2 = f2.readline() 
        check = f2.readline() # Для сверки
        col_f2 = int(f2.readline()) # Сколько прочетать строк
        #print("Сколько прочетать в начеле строчек",col_f2)
        name_f = "" # Если нет имени
        for i in range(col_f2):
            name_f = f2.readline()
            #print("Имя",name_f)

        if check == "DynaWaves\n": # Дальше будет имя файла но не всегда
            if name_f != "":
                pass
                #print("Первый имя файла",name_f)

        elif check == "StatWaves\n": # Дальше будет размер файла но не всегда
            if name_f != "":
                size = int(name_f) # Размер первого файла
                data2.append((offset,size))
                #print("Первый оффсет",offset,size)
                offset += size
        else:
            print("Непонятно",check)
            return(0) # Остановка скрипта

        col_f = int(f2.readline()) # Количество строчек с размерами

        for i in range(col_f):
            size = int(f2.readline()) # Размер файла
            data2.append((offset,size))
            offset += size

        for i in data2:
            ss += 1
            f.seek(i[0])
            check = f.read(4)
            if check == b'\xFF\xD8\xFF\xE0': # jpg
                format = "jpg"
                filename = str(ss)+"."+format
            elif check == b'\x52\x49\x46\x46': # Звук wav
                format = "wav"
                filename = str(ss)+"."+format
            else:
                format = "bin"
                filename = str(ss)+"."+format
            self.data.append((filename,i[0],i[1],format))
        self.file = f

    def Unpack_BMP(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_TXT(self, f): 
        self.text = f.read().decode("cp1251")