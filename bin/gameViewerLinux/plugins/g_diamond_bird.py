#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Алмазный Птах

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Алмазный Птах" 
FORMATS_ARCHIVE = ['flt'] 
TYPES_ARCHIVE = [('Алмазный Птах', ('*.flt'))]
GAMES = ["Алмазный Птах"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app
        
        self.sup_formats = ["bmp"]

        self.sup_types = {"bmp":1}
        self.images = []  
        self.sound = None 

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "flt":
            self.OpenArchiveFLT(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "bmp":
            self.Unpack_BMP(io.BytesIO(self.file.read(size)))

    def OpenArchiveFLT(self,file):
        f = open(file,"rb")
        col = struct.unpack("<H",f.read(2))[0] # Количество файлов
        unclear = struct.unpack("<H",f.read(2))[0] # Непонятно
        for i in range(col):
            f_path = f.read(8).split(b"\x20")[0].decode("utf8")
            format = f.read(4).split(b"\x00")[0].decode("utf8")
            size = struct.unpack("<I",f.read(4))[0] # Размер
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            self.data.append((f_path+"."+format,offset,size,format.lower()))
        self.file = f

    def Unpack_BMP(self, f):
        self.images = [Image.open(f)]