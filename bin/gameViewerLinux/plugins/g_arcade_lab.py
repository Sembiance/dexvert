#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Arcade Lab

import os, sys, io, struct
from PIL import Image
import numpy as np
import io

NAME = "Arcade Lab"
TYPES_FILES = [('gfx Images', ('*.gfx'))]
FORMATS_FILES = ["gfx"]
GAMES = ["Gold Miner Joe",
         "Superstar Chefs",
         "Digi Pool",
         "Bricks of Egypt",
         "Funny Faces",
         "Pirates of Treasure Island",
         "Spin & Win",
         "Bricks of Camelot",
         "Bricks of Atlantis",
         "Legend of Aladdin",
         "Bricks of Egypt 2: Tears of the Pharaohs",
         "Spin & Play: Carnival Madness",
         "Pizza Panic"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["gfx"]
        self.sup_types = {"gfx":2}
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

        if format == "gfx":
            self.Unpack_GFX(f2)

    def Unpack_GFX(self, f):
        type = f.read(8) # Тип
        if type != b'1XFGCSED': # Проверка
            print("ЭТО НЕ картинка",type)
            return(0) # Остановка скрипта

        size = struct.unpack("<I",f.read(4))[0] # Размер блока
        fd = f.read(size) # Непонятные данные

        while True:
            type = f.read(4) # Тип Блока сданными о картинке
            #print("Тип",type,"Позиция",f.tell()-4)

            if type == b'OFNI': # Проверка
                size = struct.unpack("<I",f.read(4))[0] # Размер блока
                w, h = struct.unpack("<II",f.read(8)) # Ширина и высота
                bit = struct.unpack("<I",f.read(4))[0] # Битность
                #print("Ширина и высота",w, h,"Битность",bit)
                unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно
                unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно
                unclear_3 = struct.unpack("<I",f.read(4))[0] # Непонятно
                unclear_4 = struct.unpack("<I",f.read(4))[0] # Непонятно
                unclear_5 = struct.unpack("<I",f.read(4))[0] # Непонятно
                #print("Непонятно",unclear_1,unclear_2,unclear_3,unclear_4,unclear_5)

            elif type == b'EGMI': # Проверка
                size = struct.unpack("<I",f.read(4))[0] # Размер блока
                if bit == 8:
                    f_image = Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1) 
                    # Картинку положим позже с палитрой

                elif bit == 16:
                    f_image = Image.frombuffer('RGB', (w,h), f.read(w*h*2), 'raw', 'BGR;16', 0, 1)
                    self.images.append(f_image)

                elif bit == 24:
                    f_image = Image.frombuffer('RGB', (w,h), f.read(w*h*3), 'raw', 'RGB', 0, 1)
                    self.images.append(f_image)
                else:
                    print("Ошибка непонятная битность картинки",bit)
 
            elif type == b'PAMC': # Палитра
                size = struct.unpack("<I",f.read(4))[0] # Размер блока
                Pal = f.read(768) # Палитра
                if bit == 8: # Если это картинка с палитрой добавляем палитру
                    f_image.putpalette(Pal)
                    self.images.append(f_image)

            elif type == b'LBTC': # Проверка
                size = struct.unpack("<I",f.read(4))[0] # Размер
                col = struct.unpack("<I",f.read(4))[0] # Количество файлов файлов картинок которое надо вырезать
                for i in range(col):
                    wx = struct.unpack("<I",f.read(4))[0] # Координаты по ширине картинки чтоб вырезать
                    hy = struct.unpack("<I",f.read(4))[0] # Координаты по высоте картинки чтоб вырезать
                    ww = struct.unpack("<I",f.read(4))[0] # Ширина картинки которую вырезать
                    hh = struct.unpack("<I",f.read(4))[0] # Высота картинки которую вырезать

                    unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно
                    unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно

                    unclear_3 = struct.unpack("<I",f.read(4))[0] # Непонятно Какието координаты
                    unclear_4 = struct.unpack("<I",f.read(4))[0] # Непонятно Какието координаты

                    unclear_5 = struct.unpack("<I",f.read(4))[0] # Непонятно
                    unclear_6 = struct.unpack("<I",f.read(4))[0] # Непонятно

                    if ww == 0 and hh == 0: # Тут нечего вырезать
                        pass
                    else:
                        f_image_2 = f_image.crop((wx,hy, wx+ww,hy+hh)) # Вырезаем картинку
                        self.images.append(f_image_2)
                        
            elif type == b'1PIM': # Проверка
                size = struct.unpack("<I",f.read(4))[0] # Размер
                f.read(size)

            elif type == b'FDNE': # Конец файла
                #print("Конец файла FDNE")
                size = struct.unpack("<I",f.read(4))[0] # Размер
                break

            else:
                print("Ошибка на",f.tell()-4)
                break
