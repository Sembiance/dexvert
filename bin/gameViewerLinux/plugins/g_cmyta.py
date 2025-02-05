#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Смута - Ожившие мертвецы

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Смута - Ожившие мертвецы" 
FORMATS_ARCHIVE = ['dat', 'res', 'spr']
TYPES_ARCHIVE = [('Смута - Ожившие мертвецы', ('*.dat', '*.res', '*.spr'))]
GAMES = ["Смута - Ожившие мертвецы"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["fl",
                            "spr",
                            "bmp",
                            "fon",
                            "wav",
                            "txt"]

        self.sup_types = {"fl":2,
                          "spr":1,
                          "bmp":1,
                          "fon":2,
                          "wav":3,
                          "txt":4}

        self.images = []  
        self.sound = None
        self.text = None
        self.Pal = b'' # Палитра для картинок

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "dat" or format == "res":
            self.OpenArchiveDAT(file)
        elif format == "spr":
           self.OpenArchiveSPR_BMP(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "fl":
            self.Unpack_FL(io.BytesIO(self.file.read(size)))
        elif format == "spr":
            self.Unpack_SPR(io.BytesIO(self.file.read(size)))
        elif format == "bmp":
            self.Unpack_BMP(io.BytesIO(self.file.read(size)))
        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))
        elif format == "txt":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))
        elif format == "fon":
            self.Unpack_FON(io.BytesIO(self.file.read(size)),name)

    def OpenArchiveSPR_BMP(self,file):
        f = open(file,"rb")
        f.seek(0,2)
        size = f.tell()
        self.data.append(("0.bmp",0,size,"bmp"))
        self.file = f

    def OpenArchiveDAT(self,file):
        self.data = []

        f = open(file,"rb")
        col = struct.unpack("<H",f.read(2))[0] # Количество файлов
        for i in range(col):
            f_path = f.read(16).split(b"\x00")[0].decode("cp1251") # Имя файла
            size = struct.unpack("<I",f.read(4))[0] # Размер
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно
            table = str.maketrans("", "", "/") # Не допустимые символы

            posf = f.tell()
            f.seek(offset)
            check_1 = f.read(4) # Проверка на формат
            f.seek(offset)
            check_2 = f.read(2) # Проверка на формат
            f.seek(offset)
            w,h = struct.unpack("<HH",f.read(4)) # Ширина и высота
            if f_path == "GAMEP1" or f_path == "ЗАСТАВКА_ПАЛ":
                f_path += ".act"
                if f_path == "GAMEP1.act":
                    f.seek(offset)
                    for i in range(256):
                        r,g,b = struct.unpack("BBB",f.read(3))
                        r = (r << 2) | (r >> 4)
                        g = (g << 2) | (g >> 4)
                        b = (b << 2) | (b >> 4)
                        self.Pal += struct.pack("BBB", r,g,b)

            elif check_1 == b'RIFF':
                format = f_path.split(".")[-1].lower()
                if format != "wav": # Добавляем тип файла если его нет
                    f_path += " "+str(i)+".wav" # Число пишу чтоб не переписать файл с таким же именим

            elif check_2 in [b'\x0D\x0A', b'\x23\x20', b'\x32\x38']: # Текст
                f_path += ".txt"
            elif check_2 == b'\x42\x4D':
                f_path += ".bmp"
            elif f_path in ["FONT8", "FONT16"]: # Шрифты
                f_path += ".fon"
            elif f_path == "LIGHT1": # Не трогаем
                pass
                
            elif w*h+18 == size: # Это спрайт
                format = f_path.split(".")[-1].lower()
                if format != "spr": # Добавляем тип файла если его нет
                    f_path += ".spr"

            else: # Остальные файлы анимация
                f_path += ".fl"

            f.seek(posf)
            f_path = f_path.translate(table) # Удаляет не допустимые символы из текста pth
            format = f_path.split(".")[-1].lower()
            self.data.append((f_path,offset,size,format))
        self.file = f

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_BMP(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_TXT(self, f):
        try: # Исключения
            self.text = f.read().decode("cp1251")
        except : # Если есть нечитабельные байты
            f.seek(0,2)
            end_f = f.tell() # Конец файла
            f.seek(0)
            f2 = io.StringIO() # Виртуальный файл для текста
            for i in range(end_f):
                try: # Исключения
                    line_text = f.read(1).decode('cp1251') # Преобразования байтов в строку
                    f2.write(line_text)
                except :
                    f2.write("\n")
            f2.seek(0)
            self.text = f2.read()

    def Unpack_FL(self, f):
        f.seek(4)
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        f.seek((col*10)+12) # Получаем оффсет первой картинки
        for i in range(col):
            posf0 = f.tell()
            w,h = struct.unpack("<HH",f.read(4)) # Ширина и высота
            size = w*h+18 # Размер картинки с заголовком
            f.seek(posf0+18)
            f_image = Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1) 
            f_image.putpalette(self.Pal)
            self.images.append(f_image)
        f.close()

    def Unpack_SPR(self, f):
        w,h = struct.unpack("<HH",f.read(4)) # Ширина и высота
        f.seek(18)
        f_image = Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1) 
        f_image.putpalette(self.Pal)
        self.images = [f_image]
        
        f.close()

    def Unpack_FON(self, f,name):
        if name == "FONT8.fon":
            w = 8
            h = 8
        elif name == "FONT16.fon":
            w = 8
            h = 16
        for i in range(256):
            self.images.append(Image.frombuffer('1', (w,h), f.read(w*h//8), 'raw', '1', 0, 1))

        f.close()