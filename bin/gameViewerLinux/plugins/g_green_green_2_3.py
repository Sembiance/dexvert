#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Green Green 2-3" 
FORMATS_ARCHIVE = [".ARC"]
TYPES_ARCHIVE = [('Green Green 2-3', ("*.ARC"))]
GAMES = ["Green Green 2",
         "Green Green 3"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["bmp",
                            "png"]
       
        self.sup_types = {"bmp":1,
                          "png":1}
        self.images = []  
        self.sound = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "arc":
            self.OpenArchiveDAT(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "bmp" or format == "png":
            self.Unpack_BMP(io.BytesIO(self.file.read(size)))

    def OpenArchiveDAT(self,file):
        self.data = []

        f = open(file,"rb")
        type = f.read(4) # Тип архива ARC1
        if type != b'\x41\x52\x43\x31': # Проверка на архив 
            print("ЭТО НЕ АРХИВ",type)
            return(0) # Остановка скрипта 
        
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов если больше 1 то это архив SCR.arc
        if col == 1: # Проверка 
            fd = f.read(4) # DATA
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет таблицы файлов
            f.seek(offset+16)
            fd = f.read(4) # HEAD
            size = struct.unpack("<I",f.read(4))[0] # Размер таблицы файлов
            col = size // 296 # Количество файлов 
            for i in range(col):
                filename = f.read(264).split(b"\x00")[0].decode("shift-jis")# Имя файла Встречаются японские буквы
                format = filename.split(".")[-1].lower()
                size = struct.unpack("<I",f.read(4))[0] # Размер
                offset = struct.unpack("<I",f.read(4))[0] # Оффсет
                f.read(24) # Непонятные байты
                self.data.append((filename,offset,size,format))

        else:
            offset = struct.unpack("<I",f.read(4))[0]  # Оффсет таблицы файлов
            unclear = struct.unpack("<I",f.read(4))[0] # Непонятно
            size = struct.unpack("<I",f.read(4))[0] # Размер данных в архиве без учёта заголовка
            f.seek(offset)
        
            for i in range(col):
                filename = f.read(16).split(b"\x00")[0].decode("shift-jis") # Имя файла
                format = filename.split(".")[-1].lower()
                size = struct.unpack("<I",f.read(4))[0] # Размер
                offset = struct.unpack("<I",f.read(4))[0] # Оффсет
                self.data.append((filename,offset,size,format))
        self.file = f
        
    def Unpack_BMP(self, f):
        image = Image.open(f)
        self.images = [image]