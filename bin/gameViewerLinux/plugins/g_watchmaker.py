#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Watchmaker(Тайна Маятника) Распаковка архива GameData.wm

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Watchmaker" 
FORMATS_ARCHIVE = ['wm']
TYPES_ARCHIVE = [('Watchmaker', ('*.wm'))]
GAMES = ["Watchmaker"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app
        
        self.sup_formats = ["tga",
                            "dds",
                            "wav"]
        self.sup_types = {"tga":1,
                          "dds":1,
                          "wav":3}
        self.images = []   
        self.sound = None  

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "wm":
            self.OpenArchiveWM(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "tga" or format == "dds":
            self.Unpack_TGA(io.BytesIO(self.file.read(size)))
        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))

    def OpenArchiveWM(self,file):
        self.data = [] 
        f = open(file,"rb")
        
        size_fblock = struct.unpack("<I",f.read(4))[0] # Количество файлов
        for i in range(size_fblock-1):
            filename = f.read(52).split(b"\x00")[0].decode("utf8").replace("\\\\","\\") # Имя файла
            format = filename.split(".")[-1].lower()
            offset = struct.unpack("<I",f.read(4))[0] # Начало файла
            f.seek(f.tell()+60)
            s = struct.unpack("<I",f.read(4))[0] # Читает размер следующего файла
            size = s-offset # Расчёт размера файла
            f.seek(f.tell()-64)
            f.read(8) # Непонятно
            self.data.append((filename,offset,size,format))
        self.file = f

    def Unpack_TGA(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_WAV(self, f):
        self.sound = f