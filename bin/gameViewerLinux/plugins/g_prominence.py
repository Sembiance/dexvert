#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Prominence
# Scratches (Шорох)
# Scratches: Director's Cut (Шорох - Последний визит)
# Некоторые файлы ogg являются видео файлами.
# В лицензионных версиях игр Шорох от Руссобит-М архивы зашифрованы.

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Prominence" 
FORMATS_ARCHIVE = ['res']
TYPES_ARCHIVE = [('Prominence', ('*.res'))]
GAMES = ["Prominence",
         "Scratches",
         "Scratches: Director's Cut"]
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
                            "dds",
                            "ico",
                            "sub",
                            "txt"]
       
        self.sup_types = {"png":1,
                          "jpg":1,
                          "tga":1,
                          "ogg":3,
                          "dds":1,
                          "ico":1,
                          "sub":4,
                          "txt":4}
        self.images = []  
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "res":
            self.OpenArchiveRES(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format in ["png", "jpg", "tga", "dds", "ico"]:
            self.Unpack_PNG(io.BytesIO(self.file.read(size)))
        elif format == "ogg":
            self.Unpack_OGG(io.BytesIO(self.file.read(size))) 
        elif format == "sub":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))  
        elif format == "txt":
            self.Unpack_TXT_2(io.BytesIO(self.file.read(size)))

    def OpenArchiveRES(self,file):
        self.data = []

        f = open(file,"rb")

        check_1 = f.read(20)
        f.seek(240)
        check_2 = f.read(8)
        f.seek(0)
        check_3 = f.read(4)

        if check_1 == b'SCream resource file' or check_2 == b'\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC':
            pass

        elif check_3 == b'SFFS':
            print("Это зашифрованный архив SFFS")
            return(0)

        else:
            print("ЭТО НЕ АРХИВ",type)
            return(0)

        f.seek(256)
        size_fblock = struct.unpack("<I",f.read(4))[0] # Количество файлов
        for i in range(size_fblock):
            filename = f.read(80) # Имя
            filename = filename.split(b"\x00")[0].decode("cp1251").replace("\\\\","\\")
            format = filename.split(".")[-1].lower()
            f.read(4) # Непонятно
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size = struct.unpack("<I",f.read(4))[0]   # Размер
            self.data.append((filename,offset,size,format))
        self.file = f

    def Unpack_OGG(self, f):
        self.sound = f
        
    def Unpack_TXT(self, f): 
        self.text = f.read().decode("cp1251")
        
    def Unpack_TXT_2(self, f): 
        self.text = f.read().decode("utf8")

    def Unpack_PNG(self, f):
        try: # Исключения
            image = Image.open(f)
            self.images = [image]
        except :
            print("Не поддерживается")