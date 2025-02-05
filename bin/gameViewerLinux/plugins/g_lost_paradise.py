#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# dat Затерянный рай
# Звук wav не проигровает некоторые mp3 тоже не проигровается, есть картинки dds

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Затерянный рай"
FORMATS_ARCHIVE = ['dat'] 
TYPES_ARCHIVE = [('Затерянный рай', ('*.dat'))]
GAMES = ["Затерянный рай"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app
        
        self.sup_formats = ["jpg",
                            "mp3"]

        self.sup_types = {"jpg":1,
                          "mp3":3}
        self.images = []
        self.sound = None 

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "dat":
            self.OpenArchiveDAT(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "jpg":
            self.Unpack_JPG(io.BytesIO(self.file.read(size)))
        elif format == "mp3":
            self.Unpack_MP3(io.BytesIO(self.file.read(size)))
        #elif format == "wav":
            #self.Unpack_WAV(io.BytesIO(self.file.read(size)))

    def OpenArchiveDAT(self,file):
        f = open(file,"rb")
        type = f.read(4) # Тип архива VPAK
        if type != b'\x56\x50\x41\x4B': # Проверка на архив
            print("ЭТО НЕ АРХИВ")
            return(0) # Остановка скрипта 
        f.read(4)
        f.read(128)# Внутренне имя
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        addedf = struct.unpack("<I",f.read(4))[0] # Надо прибавить к оффсету
        for i in range(col):
            filename = f.read(128).split(b"\x00")[0].decode("cp1251").replace("\\\\","\\")# Имя файла
            format = filename.split(".")[-1].lower()
            size = struct.unpack("<I",f.read(4))[0]
            offset = struct.unpack("<I",f.read(4))[0]+addedf+8
            self.data.append((filename,offset,size,format))
        self.file = f
        return 1

    def Unpack_JPG(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_MP3(self,f):
        self.sound = f