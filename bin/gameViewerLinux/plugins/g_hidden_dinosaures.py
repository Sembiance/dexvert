#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Starshine Legacy Episode 1: Mystery of the Soul Riders   (Ангелы подковы 1 - Лиза, Альтаир и скачки судьбы)
# Starshine Legacy Episode 2: Secret of Pine Hill Mansion  (Ангелы подковы 2 - Линда, Метеор и всадники судьбы)
# Starshine Legacy Episode 3: Legend of Pandoria           (Ангелы подковы 3 - Анна, Конкорд и легенды Пандории)
# Starshine Legacy Episode 4: The Riddle of Dark Core      (Ангелы подковы 4 - Алина, Буран и загадки Темных Недр)
# Star Academy: Episode 1: Competitive selection  (Звездная фабрика: Эпизод 1 - Конкурсный отбор)
# Star Academy: Episode 2: the Show begins        (Звездная фабрика: Эпизод 2 - Шоу начинается)  (Star Academy: Showtime!)
# Star Academy: Episode 3: Turning point          (Звездная фабрика: Эпизод 3 - Переломный момент)
# Star Academy: Episode 4: In a blaze of glory    (Звездная фабрика: Эпизод 4 - В лучах славы)

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Hidden Dinosaures" 
FORMATS_ARCHIVE = ["CSA"]
TYPES_ARCHIVE = [('Hidden Dinosaures', ("*.CSA"))]
GAMES = ["Starshine Legacy Episode 1: Mystery of the Soul Riders",
         "Starshine Legacy Episode 2: Secret of Pine Hill Mansion",
         "Starshine Legacy Episode 3: Legend of Pandoria",
         "Starshine Legacy Episode 4: The Riddle of Dark Core",
         "Star Academy: Episode 1: Competitive selection",
         "Star Academy: Episode 2: the Show begins",
         "Star Academy: Episode 3: Turning point",
         "Star Academy: Episode 4: In a blaze of glory"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["tga",
                            "png",
                            "jpg",
                            "pte",
                            "wav"]
       
        self.sup_types = {"tga":1,
                          "png":1,
                          "jpg":1,
                          "pte":1,
                          "wav":3}
        self.images = []  
        self.sound = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "csa":
            self.OpenArchiveDAT(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "tga" or format == "png" or format == "jpg":
            self.Unpack_TGA(io.BytesIO(self.file.read(size)))
        elif format == "wav":
            self.Unpack_wav(io.BytesIO(self.file.read(size))) 
        elif format == "pte":
            self.Unpack_PTE(io.BytesIO(self.file.read(size))) 

    def OpenArchiveDAT(self,file):
        self.data = []

        f = open(file,"rb")
        
        type = f.read(4) # Тип архива GEEK
        if type != b'\x47\x45\x45\x4B': # Проверка на архив
            print("ЭТО НЕ АРХИВ",type)
            return(0) # Остановка скрипта
    
        f.seek(16)
        size_f = struct.unpack("<I",f.read(4))[0] # Количество файлов

        for i in range(size_f):
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size = struct.unpack("<I",f.read(4))[0]   # Размер
            filename = f.read(128).split(b"\x00")[0].decode("utf8").replace("\\\\","\\") # Имя файла
            format = filename.split(".")[-1].lower()
            self.data.append((filename,offset,size,format))
        self.file = f

    def Unpack_wav(self, f):
        self.sound = f
        
    def Unpack_TGA(self, f):
        try: # Исключения
            image = Image.open(f)
            self.images = [image]
        except :
            print("Не поддерживается")

    def Unpack_PTE(self, f):
        unclear = struct.unpack("<I",f.read(4))[0] # Непонятно
        for i in range(2):
            unclear = struct.unpack("<I",f.read(4))[0] # Непонятно
            name_length = struct.unpack("<I",f.read(4))[0] # Длина строчки с текстом
            filename = f.read(name_length) # Текст
        f.read(32)

        fd = f.read() # Читаем остальной файл с картинкой DDS

        f2 = io.BytesIO(fd)
        try: # Исключения
            image = Image.open(f2)
            self.images = [image]
        except :
            print("Не поддерживается")