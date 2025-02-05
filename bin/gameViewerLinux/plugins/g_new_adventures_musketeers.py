#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Новые приключения мушкетеров

import os, sys, io, struct
from PIL import Image
import numpy as np
import io
import zlib

NAME = "Новые приключения мушкетеров"
TYPES_FILES = [('bmp Images', ('*.bmp')),('tga Images', ('*.tga')),('spr Images', ('*.spr')),('zspr Images', ('*.zspr')),('wav Sound', ('*.wav')),('mp3 Sound', ('*.mp3')),('txt Text', ('*.txt')),('atx Text', ('*.atx')),('dat Text', ('*.dat'))]
FORMATS_FILES = ["bmp","tga","spr","zspr","wav","mp3","txt","atx","dat"]
GAMES = ["Новые приключения мушкетеров"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["bmp",
                            "tga",
                            "spr",
                            "zspr",
                            "wav",
                            "mp3",
                            "txt",
                            "atx",
                            "dat"]
        self.sup_types = {"bmp":1,
                          "tga":1,
                          "spr":1,
                          "zspr":1,
                          "wav":3,
                          "mp3":3,
                          "txt":4,
                          "atx":4,
                          "dat":4}
        self.images = []
        self.sound = None
        self.text = None

    def open_files(self,files):
        self.data = files

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        size = data_res[2]
        format = data_res[3]
        self.text = None
        f = open(name,"rb")
        f2 = io.BytesIO(f.read(size))
        f.close()

        if format in ["bmp","tga"]:
            self.Unpack_PNG(f2)
        elif format == "spr" or format == "zspr":
            self.Unpack_SPR(f2,name)
        elif format == "wav" or format == "mp3":
            self.Unpack_WAV(f2)
        elif format in ["txt", "atx"]:
            self.Unpack_TXT(f2)
        elif format == "dat":
            self.Unpack_TXT2(f2)

    def Unpack_PNG(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_TXT(self, f): 
        self.text = f.read().decode("utf-16-le") # Есть русский текст

    def Unpack_TXT2(self, f): 
        self.text = f.read().decode("utf8")

    def Unpack_SPR(self, f, name):
        f2 = io.BytesIO() # Для распаковки
        (dirname, filename) = os.path.split(name)

        f.seek(0,2)
        end_f = f.tell()
        f.seek(0)
        if end_f <= 16:
            print("Ошибка это файл содержит только заголовок",end_f)
            f.close()
            return(0) # Остановка скрипта

        unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно всегда одинаковые
        unclear_2 = struct.unpack("<H",f.read(2))[0] # Непонятно
        #print("Бывает 1600 600 и 800 128:",unclear_1,unclear_2)
        coordinates_w = struct.unpack("<H",f.read(2))[0] # Координаты на картинки по ширине 
        coordinates_h = struct.unpack("<H",f.read(2))[0] # Координаты на картинки по высоте
        w,h = struct.unpack("<HH",f.read(4)) # Ширина и высота
        #print("Ширина и высота картинки",w,h)
        #print("Координаты по ширине",coordinates_w,"по высоте картинки",coordinates_h)
      
        format = filename.split(".")[-1].lower()
        if format == "zspr": # Распаковка сжатия
            end_f = struct.unpack("<I",f.read(4))[0] # Размер распакованного файла
            fd = f.read()
            fdw = zlib.decompress(fd)
            f.close()
            f = io.BytesIO(fdw)

        number_lines = 0 # Количество строк картинки
        while True:
            if f.tell() == end_f:
                #print("Конец файла",f.tell())
                break
            posf = f.tell()
            col = struct.unpack("B",f.read(1))[0] # Управляющий байт
            #print("Управляющей байт",col)

            # Биты 1100 0000 
            if col == 192: # C0 Это новая строчка распаковки по ширине картинки
                #print("Байт C0 Это новая строчка распаковки по ширине картинки")
                number_lines += 1
                self.Calculation(w,f2,number_lines) # Расчёт сколько записать байтов

            # Биты 1100 0001
            elif col == 193: # C1 Конец файла
                #print("Зашли C1")
                number_lines += 1
                self.Calculation(w,f2,number_lines) # Расчёт сколько записать байтов
                if number_lines != h: # Значит надо дописать ещё строки в конец картинки  
                    f2.write(b'\xFF'*((w*2)*(h-number_lines)))
                #print("Конец файла C1",f.tell())

            # Возможно тут работает эфект сглаживания
            # От бит 1000 0000 до >      1011 1111 бит 191(BF) ?
            elif col >= 128 : # 80 Читать пар по 3 байта
                col_b = (col - 128)+1 # Количество пар которое надо прочетать
                #print("Диапозон 128> Повторение по 2 байта позиция",posf)
                for i in range(col_b):
                    unclear = struct.unpack("B",f.read(1))[0] # Непонятно
                    fd = f.read(2)
                    f2.write(fd)

            # От бит 0100 000 до 0111 1111 бит
            elif col >= 64 and col <= 127: # 40-7F Просто чтение байтов
                #print("Диапозон 64-127 Чтение позиция",posf)
                col_2 = ((col-64)+1)*2
                fd = f.read(col_2)
                f2.write(fd)
                #print("Прочетать байтов",col_2,f.tell()-1,fd)

            # От бит 0000 0000 до 0011 1111
            elif col >= 0 and col <= 63: # 3F
                #print("Диапозон 0-63 Повторение позиция",posf)
                for i in range((col+1)*2): # Повторяем цвета прозрачности
                    f2.write(b'\xFF')

        if f2.tell() == w*h*2:
            f2.seek(0)
            # 16 бит RGB 15
            f_image = Image.frombuffer('RGB', (w,h), f2.read(w*h*2), 'raw', 'BGR;15', 0, 1)
            self.images.append(f_image)

        elif f2.tell() > w*h*2:
            print("Слишком много распаковалось байтов",f2.tell()-(w*h*2))
        else:
            print("Недостаточно распаковалось байтов надо ещё",(w*h*2)-f2.tell())
        f2.close()
        f.close()

    def Calculation(self, w, f2, number_lines):
        posf2 = f2.tell()
        whole, rest = divmod(posf2,w*2) # Делит правельно сначало идёт целое число потом остаток
        if posf2 < w*2: # Если данных меньше чем одна строчка по ширине
            for i in range((w*2)-posf2): # Получаем сколько надо ещё повторить байтов
                f2.write(b'\xFF')

        elif rest > 0: # Если нехватет байтов в конце строчки
            #print(posf2,"Данные",whole, rest,"Повторить",(w*2)-rest)
            for i in range((w*2)-rest): # Получаем сколько надо ещё повторить байтов
                f2.write(b'\xFF') 

        elif f2.tell() < (w*2)*number_lines:
            repeat = ((w*2)*number_lines)-f2.tell()
            #print("Надо заполнить строчку прозрачностью",repeat)
            #print(f2.tell(),number_lines,"Ширина",w*2)
            for i in range(repeat):
                f2.write(b'\xFF')