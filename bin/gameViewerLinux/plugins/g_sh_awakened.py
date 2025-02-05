#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Sherlock Holmes: The Awakened (Шерлок Холмс и Секрет Ктулху)

import os, sys, io, struct
from PIL import Image
import numpy as np
import zlib 

NAME = "Sherlock Holmes: The Awakened" 
FORMATS_ARCHIVE = ["img", "dat", "snd"]
TYPES_ARCHIVE = [('Sherlock Holmes: The Awakened', ('*.img','*.dat','*.snd'))]
GAMES = ["Sherlock Holmes: The Awakened"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["dds",
                            "ogg",
                            "lua",
                            "qpr"]
       
        self.sup_types = {"dds":1,
                          "ogg":3,
                          "lua":4,
                          "qpr":4}

        self.images = []  
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "img" or format == "dat" or format == "snd":
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
        if format == "dds":
            self.Unpack_DDS(io.BytesIO(self.file.read(size)))
        elif format == "ogg":
            self.Unpack_OGG(io.BytesIO(self.file.read(size))) 
        elif format == "lua" or format == "qpr":
            self.Unpack_TXT(io.BytesIO(self.file.read(size))) 

    def OpenArchiveDAT(self,file):
        self.data = []
        f = open(file,"rb")
        
        type = f.read(4) # Тип архива
        if type != b'\x01\x00\x00\x00': # Проверка на архив
            print("ЭТО НЕ АРХИВ",type)
            return(0) # Остановка скрипта 
     
        line_length = struct.unpack("B",f.read(1))[0] # Длина строчки
        f_pa1 = f.read(line_length).split(b"\x00")[0].decode("cp1251").replace("\\\\","\\") #
        f_path, end_tab, size, col_folder = self.tab(f)
        #print(f_path,"Конец таблицы файлов", end_tab, size,"Количество папок внутри", col_folder)

        while f.tell() != end_tab:
            f_path, offset, size, zero = self.tab(f)
            if zero > 0: # Если больше то это папка и это номер сколько в ней папок или файлов
                pass         
            else:
                format = f_path.split(".")[-1].lower() 
                self.data.append((f_path,offset,size,format))
        self.file = f

    def tab(self, f):
        line_length = struct.unpack("B",f.read(1))[0] # Длина строчки
        f_path = f.read(line_length).split(b"\x00")[0].decode("cp1251").replace("\\\\","\\") #
        offset = struct.unpack("<I",f.read(4))[0]    # Оффсет
        size = struct.unpack("<I",f.read(4))[0]      # Размер файла
        col_files = struct.unpack("<I",f.read(4))[0] # Количество файлов в папке
        return f_path, offset, size, col_files

    def Unpack_OGG(self, f):
        self.sound = f

    def Unpack_TXT(self, f): 
        self.text = f.read().decode("cp1251")

    def Unpack_DDS(self, f):
        try: # Исключения
            image = Image.open(f)
            self.images = [image]
        except :
            print("Не поддерживается")