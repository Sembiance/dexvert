#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Chłopaki nie płaczą(Boyz Don't Cry)(Пацаны не плачут)

import os, sys, io, struct
from PIL import Image

NAME = "Пацаны не плачут"
FORMATS_ARCHIVE = ['pac']
TYPES_ARCHIVE = [('Pacany Pack', ('*.pac'))]
GAMES = ["Пацаны не плачут"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        
        self.sup_formats = ["png",
                            "jpg",
                            "ogg",
                            "ext",
                            "anf",
                            "xml"]

        self.sup_types = {"png":1,
                          "jpg":1,
                          "ogg":3,
                          "ext":3,
                          "anf":4,
                          "xml":4}
        self.images = []
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "pac":
            self.OpenArchivePAC(file)
    
    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "png" or format == "jpg":
            self.Unpack_PNG(io.BytesIO(self.file.read(size)))
        elif format == "ogg" or format == "ext":
            self.Unpack_OGG(io.BytesIO(self.file.read(size)))
        elif format == "xml" or format == "anf":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))

    def OpenArchivePAC(self,file):
        self.data = []
        f = open(file,"rb")
        
        type = f.read(8)
        if type != b"LARTLIB1":
            raise Exception("Это не архив!")
            
        tab_size = struct.unpack("<I",f.read(4))[0] # Размер таблицы файлов от начало файла
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        f.seek(8,1) # Размер архива без таблицы файлов + ещё что-то
        line = "" # Путь папки
        for i in range(col):
            f.seek(8,1)
            offset = struct.unpack("<I",f.read(4))[0]+tab_size # Оффсет 
            name_length = struct.unpack("<I",f.read(4))[0] # Длина имени
            filename = f.read(name_length).decode("cp1251") # Имя файла
            format = filename.split(".")[-1].lower()
            size1 = struct.unpack("<I",f.read(4))[0] # Размер
            size2 = struct.unpack("<I",f.read(4))[0] # Размер
            tip_f = struct.unpack("<I",f.read(4))[0] # 1 - папка, 2 - файл 
            if tip_f == 1: # Папка
                line = filename # Путь папки
            elif tip_f == 2: # Файл
                filename = line+"\\"+filename # Имя и путь
                self.data.append((filename,offset,size1,format))
        self.file = f

    def Unpack_PNG(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_OGG(self, f):
        self.sound = f
        
    def Unpack_TXT(self, f): 
        self.text = f.read().decode("cp1251")