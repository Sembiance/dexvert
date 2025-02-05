#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Чукча в большом городе

import os, sys, io, struct
from PIL import Image

NAME = "Чукча в Большом Городе"
FORMATS_ARCHIVE = ['npk']
TYPES_ARCHIVE = [('Чукча в Большом Городе', ('*.npk'))]
GAMES = ["Чукча в Большом Городе"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["dds",
                            "tga",
                            "wav",
                            "ogg",
                            "tcl",
                            "error",
                            "fx",
                            "n3d2",
                            "nanim2",
                            "tai",
                            "n2",
                            "xml"]  

        self.sup_types = {"dds":1,
                          "tga":1,
                          "wav":3,
                          "ogg":3,
                          "tcl":4,
                          "error":4,
                          "fx":4,
                          "n3d2":4,
                          "nanim2":4,
                          "tai":4,
                          "n2":4,
                          "xml":4}

        self.images = []
        self.sound = None
        self.text = None
        
    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "npk":
            self.OpenArchiveNPK(file)
    
    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "dds" or format == "tga":
            self.Unpack_TGA(io.BytesIO(self.file.read(size)))
        elif format == "wav" or format == "ogg":
            self.Unpack_OGG(io.BytesIO(self.file.read(size)))
        elif format in ["tcl", "error", "fx", "n3d2", "nanim2", "tai", "n2"]:
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))
        elif format == "xml":
            self.Unpack_TXT_2(io.BytesIO(self.file.read(size)))
    
    def OpenArchiveNPK(self,file):
        self.data = [] # Список файлов
        line = "" # Путь
        
        f = open(file,"rb")
        
        type = f.read(4)
        if type != b"0KPN": raise("Это не архив!")
        
        f.seek(8)
        ofset_plus = struct.unpack("<I",f.read(4))[0] + 8
        
        while True:
            type = f.read(4) # Тип
            if type == b'ELIF' : # Файл
                f.read(4)
                offset = struct.unpack("<I",f.read(4))[0] + ofset_plus
                size = struct.unpack("<I",f.read(4))[0]
                name_size = struct.unpack("<H",f.read(2))[0]
                name = f.read(name_size)
                name = name.decode('cp1251')
                format = name.split(".")[-1].lower()
                pth = line + name
                self.data.append((pth,offset,size,format))

            elif type == b'_RID' : # Создать папку    
                f.read(4)
                name_size = struct.unpack("<H",f.read(2))[0]
                name = f.read(name_size) # имя
                name = name.decode('cp1251')
                line += "\\" + name
                
            elif type == b'DNED' : # Назад на 1 папку
                f.read(4)
                search = line.rfind("\\") # Ищем справа в строчки  строчку "\\"
                line = line[:search] # Срез с конца
                
            elif type == b'ATAD' : # Конец таблицы
                f.read(4)
                break

            else:
                posf0 = f.tell()
                print("Ошибка !!!",type,posf0)
                break
        self.file = f

    def Unpack_OGG(self, f): 
        self.sound = f
        
    def Unpack_TXT(self, f): 
        self.text = f.read().decode("cp1251")
        
    def Unpack_TXT_2(self, f): 
        self.text = f.read().decode("utf8")
        
    def Unpack_TGA(self, f):
        try: # Исключения
            image = Image.open(f)
            self.images = [image]
        except :
            print("Не поддерживается")