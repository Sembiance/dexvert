#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Dracula: Origin (Охотник на Дракулу)
# Sherlock Holmes Contre Arsene Lupin (Шерлок Холмс против Арсена Люпена) 2007
# Sherlock Holmes Contre Arsene Lupin. Remastered Edition (Шерлок Холмс против Арсена Люпена) 2010
# Sherlock Holmes: The Awakened (Remastered Version) (Шерлок Холмс и секрет Ктулху. Золотое издание)
# Sherlock Holmes vs. Jack the Ripper (Шерлок Холмс против Джека Потрошителя)
# The Testament of Sherlock Holmes (Последняя воля Шерлока Холмса)

import os, sys, io, struct
from PIL import Image
import numpy as np
import zlib 

NAME = "Frogwares pak" 
FORMATS_ARCHIVE = ["pak"]
TYPES_ARCHIVE = [('Frogwares', ("*.pak"))]
GAMES = ["Dracula: Origin",
         "Sherlock Holmes Contre Arsene Lupin",
         "Sherlock Holmes Contre Arsene Lupin. Remastered Edition",
         "Sherlock Holmes: The Awakened (Remastered Version)",
         "Sherlock Holmes vs. Jack the Ripper",
         "The Testament of Sherlock Holmes"]
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
                            "lua",
                            "qpr"]
       
        self.sup_types = {"dds":1,
                          "png":1,
                          "jpg":1,
                          "ogg":3,
                          "lua":4,
                          "qpr":4}

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
            self.Unpack_DDS(io.BytesIO(self.file.read(size)))
        elif format == "ogg":
            self.Unpack_OGG(io.BytesIO(self.file.read(size))) 
        elif format == "lua" or format == "qpr":
            f2 = self.Unpack_Tab(io.BytesIO(self.file.read(size))) 
            self.Unpack_TXT(f2)

    def OpenArchiveDAT(self,file):
        self.data = []
        List_folders = [] # Список путей папок
        f = open(file,"rb")

        f.seek(0,2)
        end_f = f.tell()
        f.seek(end_f-4)
        offset_tab = struct.unpack("<I",f.read(4))[0] # Оффсет начало сжатых таблиц
        f.seek(offset_tab)
        f1 = self.Unpack_Tab(f) # Распакованная первая таблица с именами файлов
        f2 = self.Unpack_Tab(f) # Распакованная вторая таблица с путями папок

        #Таблица 2
        unclear = struct.unpack("<I",f2.read(4))[0]     # Непонятно
        col_folders = struct.unpack("<I",f2.read(4))[0] # Количество строчек
        for i in range(col_folders):
            f_path = self.Decoderletters(f2) # Путь файлов
            List_folders.append(f_path[1:])  # Срез удаляем первый символ
        f2.close()


        # Таблица 1
        f1.seek(0,2)
        end_f = f1.tell() # Длина файла
        f1.seek(0)

        while f1.tell() != end_f:
            temp_list = [] # Временный список
            col = struct.unpack("<I",f1.read(4))[0] # Количество файлов
            for i in range(col):
                unclear_1 = struct.unpack("<H",f1.read(2))[0]     # Непонятно
                folder_number = struct.unpack("<H",f1.read(2))[0] # Номер папки пути
                f_path = self.Decoderletters(f1) # Имя файла
                right_f = f_path.rfind('#')   # Ищем с права на строчке #
                f_path = f_path[right_f + 1:] # Вырезаем ненужный путь со знаком # 
                
                # Две строчки это для (Арсена Люпена 2007) архив game.pak 
                table = str.maketrans("", "", "?") # Не допустимые символы
                f_path = f_path.translate(table) # Удаляет не допустимые символы из текста
                
                offset = struct.unpack("<I",f1.read(4))[0] # Оффсет
                size = struct.unpack("<I",f1.read(4))[0]   # Размер
                unclear_2 = struct.unpack("<I",f1.read(4))[0] # Непонятно всегда 0
                unclear_3 = struct.unpack("<I",f1.read(4))[0] # Непонятно
                unclear_4 = struct.unpack("<I",f1.read(4))[0] # Непонятно
                temp_list.append((f_path,offset,size,folder_number))

            #print("Четыре конечные строчки в блоке таблицы файлов")
            f_path_1 = self.Decoderletters(f1) # Тип файлов и папка
            format = self.Decoderletters(f1)   # Тип файлов 
            f_path_2 = self.Decoderletters(f1) # Папка
            f_path_3 = self.Decoderletters(f1) # Нули 00 00 почти всегда

            for i in temp_list:
                f_path_f = List_folders[i[3]]+"\\"+i[0]+format # Собранный полный путь к файлу
                format_2 = f_path_f.split(".")[-1].lower() 
                self.data.append((f_path_f,i[1],i[2],format_2))
                #print(f_path_f)
        f1.close()
        self.file = f

    def Unpack_Tab(self, f): # Распаковка сжатия
        byte = struct.unpack("B",f.read(1))[0]         # Непонятно всегда 1
        size = struct.unpack("<I",f.read(4))[0]        # Размер сжатых данных
        size_Unpack = struct.unpack("<I",f.read(4))[0] # Размер распакованных данных
        fd = f.read(size)
        fd_tab = zlib.decompress(fd)
        f2 = io.BytesIO(fd_tab)
        return f2

    def Decoderletters(self, f):
        line_length = struct.unpack("<H",f.read(2))[0] # Длина строчки
        filename = f.read(line_length).split(b"\x00")[0].decode("cp1251").replace("\\\\","\\") # специально такая кодировка
        return filename

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