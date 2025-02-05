#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Perfil de Riesgo. Casos Federales
# Некоторые файлы ogg являются видео файлами.

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Perfil de Riesgo. Casos Federales" 
FORMATS_ARCHIVE = ['res']
TYPES_ARCHIVE = [('Perfil de Riesgo. Casos Federales', ('*.res'))]
GAMES = ["Perfil de Riesgo. Casos Federales"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["png",
                            "jpg",
                            "tga",
                            "ogg",
                            "xml"]
       
        self.sup_types = {"png":1,
                          "jpg":1,
                          "tga":1,
                          "ogg":3,
                          "xml":4}
        self.images = []  
        self.sound = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "res":
            self.OpenArchiveRES(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format in ["png", "jpg", "tga"]:
            self.Unpack_PNG(io.BytesIO(self.file.read(size)))
        elif format == "ogg":
            self.Unpack_OGG(io.BytesIO(self.file.read(size)))
        elif format == "xml":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))

    def OpenArchiveRES(self,file):
        self.data = []

        f = open(file,"rb")
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        for i in range(col):
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size = struct.unpack("<I",f.read(4))[0] # Размер
            filename = f.read(100).split(b"\x00")[0].decode("utf8").replace("\\\\","\\") # Имя файла
            format = filename.split(".")[-1].lower()
            self.data.append((filename,offset,size,format))
        self.file = f

    def Unpack_OGG(self, f):
        self.sound = f

    def Unpack_PNG(self, f):
        image = Image.open(f)
        self.images = [image]
        
    def Unpack_TXT(self, f): 
        self.text = f.read().decode("cp1251")