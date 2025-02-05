#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# AfterShocked!
# L'Oeil du Kraken(Eye of the Kraken)
# Patrimonium. Act 1
# Patrimonium. Act 2
# Patrimonium. Act 3
# Ozzie & the Quantum Playwright

import os, sys, io, struct
from PIL import Image
import zlib

NAME = "AGAST"
FORMATS_ARCHIVE = ['game.data']
TYPES_ARCHIVE = [('AGAST', ('game.data'))]
GAMES = ["AfterShocked!",
         "L'Oeil du Kraken",
         "Patrimonium. Act 1",
         "Patrimonium. Act 2",
         "Patrimonium. Act 3",
         "Ozzie & the Quantum Playwright"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["wav",
                            "mp3",
                            "ogg",
                            "mid",
                            "sprite",
                            "font",
                            "image",
                            "zbuffer"]

        self.sup_types = {"wav":3,
                          "mp3":3,
                          "ogg":3,
                          "mid":3,
                          "sprite":2,
                          "font":2,
                          "image":1,
                          "zbuffer":1}

        self.images = []
        self.sound = None
        self.text = [] # Список для текста

    def open_data(self,file):
        p,f = os.path.split(file)
        arch = p+"\\Resource.data"

        if f.lower() == "game.data":
            if not os.path.exists(arch):
                raise Exception("Файл {} не найден".format(arch))
    
            else:
                self.OpenArchiveDATA(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        fd = zlib.decompress(self.file.read(size)) # Распаковка сжатия

        if format in ["mp3", "mid", "wav", "ogg"]:
            # Проверка на пустые байты в начале файла
            if fd[:731] == b'\x00' * 731: # Пустые байты в файле
                fd = fd[731:] # Удаляем пустые байты в начале

            elif fd[:626] == b'\x00' * 626:
                fd = fd[626:]

            elif fd[:522] == b'\x00' * 522:
                fd = fd[522:]

            elif fd[:417] == b'\x00' * 417:
                fd = fd[417:]

            self.Unpack_WAV(io.BytesIO(fd))

        elif format in ["sprite", "font", "image"]:
            self.Unpack_IMAG(io.BytesIO(fd))

        elif format == "zbuffer":
            self.Unpack_ZBU(io.BytesIO(fd))

    def OpenArchiveDATA(self,file):
        self.data = [] # Список файлов
        data3 = [] # Список имена файлов файлов

        f = open(file,"rb")
        fd = f.read()
        offset_tab_name = fd.find(b'}SCRIPTTABLE\x00\x00\x00\x00STRINGTABLE{\x00\x00\x00\x00',0) # Поиск начало таблицы с именами файлов
        if offset_tab_name == -1: # Если не нашли байты
            print("Ошибка не найдено начало таблицы с именами файлов")
            return(0) # Остановка

        f.seek(44)
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        f.seek(offset_tab_name+32+8) # Переход на начало таблицы с именами

        for i in range(col):
            name_length = struct.unpack("<I",f.read(4))[0] # Длина имени
            f_path = f.read(name_length).decode("utf8") # Имя и путь файла
            data3.append(f_path)
        f.close()

        # Чтение архива с файлами
        p,f = os.path.split(file)
        arch = p+"\\Resource.data"
        f = open(arch,"rb")

        f.seek(8)
        for i in range(col):
            f.read(4) # Заголовок AZIP
            unclear = struct.unpack("<I",f.read(4))[0] # Непонятно Возможно обозначают сжатый не сжатый файл
            size_comp = struct.unpack("<I",f.read(4))[0] # Размер сжатого файла
            size = struct.unpack("<I",f.read(4))[0] # Размер распакованого файла

            offset = f.tell()
            format = data3[i].split(".")[-1].lower()
            self.data.append((data3[i],offset,size_comp,format))
            f.seek(size_comp,1) # Пропускаем сжатый файл

        self.file = f

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_IMAG(self,f):
        unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно
        col = struct.unpack("<I",f.read(4))[0] # Количество картинок
        unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно
        unclear_3 = struct.unpack("<I",f.read(4))[0] # Непонятно

        for i in range(col):
            w, h = struct.unpack("<II",f.read(8)) # Ширина и высота
            self.images.append(Image.frombuffer('RGBA', (w,h), f.read(w*h*4), 'raw', 'BGRA', 0, 1))

    def Unpack_ZBU(self,f):
        type = f.read(4) # Тип AZBU
        w, h = struct.unpack("<II",f.read(8)) # Ширина и высота
        self.images.append(Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1))
        f.close()
