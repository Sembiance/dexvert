#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Тайна Третьей планеты 2003

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Тайна Третьей планеты"
FORMATS_ARCHIVE = ['.carc','LData']
TYPES_ARCHIVE = [('Тайна Третьей планеты', ('*.carc','LData'))]
GAMES = ["Тайна Третьей планеты"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["tga",
                            "bmp",
                            "wav"]

        self.sup_types = {"tga":1,
                          "bmp":1,
                          "wav":3}
        self.images = [] 
        self.sound = None 

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        (dirname, filename) = os.path.split(file)
        if format == "carc" or filename == "LData":
            self.OpenArchiveCARC(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "tga" or format == "bmp":
            self.Unpack_TGA(io.BytesIO(self.file.read(size)))
        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))

    def OpenArchiveCARC(self,file):
        f = open(file,"rb")
        type = f.read(4) # Тип архива cAr.
        if type != b'\x63\x41\x72\x2e': # Проверка на архив
            print("ЭТО НЕ АРХИВ")
            return(0)
        
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        for i in range(col):
            f_path = b''
            while True:
                bait = f.read(1) # Байт строчки
                if bait == b'\x00':
                    size1 = struct.unpack("<I",f.read(4))[0]  # Размер
                    size2 = struct.unpack("<I",f.read(4))[0]  # Размер
                    offset = struct.unpack("<I",f.read(4))[0] # Оффсет
                    filename = f_path.split(b"\x00")[0].decode("cp1251").replace("\\\\","\\")# Переделаваем байты в строчку, есть русские буквы
                    format = filename.split(".")[-1].lower()
                    self.data.append((filename,offset,size1,format))
                    break

                elif bait == b'\x3A': # Меняем знак : на \ 
                    f_path += b'\x5C'
                else:
                    f_path += bait # Прибавляем байт
        self.file = f

    def Unpack_TGA(self, f):
        try: # Исключения
            image = Image.open(f)
            self.images = [image]
        except :
            print("Не поддерживается")

    def Unpack_WAV(self, f):
        self.sound = f