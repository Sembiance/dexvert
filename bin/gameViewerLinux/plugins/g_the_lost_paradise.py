#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Затерянные острова

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Затерянные острова" 
FORMATS_ARCHIVE = ['pak'] 
TYPES_ARCHIVE = [('Затерянные острова', ('*.pak'))]
GAMES = ["Затерянные острова"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app
        
        self.sup_formats = ["dds",
                            "png",
                            "jpg",
                            "ogg",
                            "ini",
                            "txt",
                            "fx",
                            "lua",
                            "xml",
                            "phonemes",
                            "terrain"]

        self.sup_types = {"dds":1,
                          "png":1,
                          "jpg":1,
                          "ogg":3,
                          "ini":4,
                          "txt":4,
                          "fx":4,
                          "lua":4,
                          "xml":4,
                          "phonemes":4,
                          "terrain":4}
        self.images = []
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "pak":
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
        if format == "dds" or format == "png" or format == "jpg":
            self.Unpack_JPG(io.BytesIO(self.file.read(size)))
        elif format == "ogg":
            self.Unpack_OGG(io.BytesIO(self.file.read(size)))

        elif format in ["ini","fx","lua","xml","phonemes","terrain"]:
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))
            
        elif format in ["txt"]:
            self.Unpack_TXT_2(io.BytesIO(self.file.read(size)))

    def OpenArchiveDAT(self,file):
        f = open(file,"rb")
        type = f.read(4) # Тип архива YYST
        if type != b'\x59\x59\x53\x54': # Проверка на архив
            print("ЭТО НЕ АРХИВ",type)
            return(0) # Остановка скрипта 
        
        unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно
        col = struct.unpack("<I",f.read(4))[0]       # Количество файлов
        size_tab = struct.unpack("<I",f.read(4))[0]  # Размер таблицы файлов

        for i in range(col):
            col_b = struct.unpack("<H",f.read(2))[0] # Длина имени
            filename = f.read(col_b).split(b"\x00")[0].decode("utf8").replace("\\\\","\\") # Имя файла
            format = filename.split(".")[-1].lower()
            size = struct.unpack("<I",f.read(4))[0]   # Размер
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            self.data.append((filename,offset,size,format))
        self.file = f
        return 1

    def Unpack_JPG(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_OGG(self, f):
        self.sound = f
        
    def Unpack_TXT(self, f): 
        self.text = f.read().decode("utf8")
        
    def Unpack_TXT_2(self, f): 
        self.text = f.read().decode("cp1251")