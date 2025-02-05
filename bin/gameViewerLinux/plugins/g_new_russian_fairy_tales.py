#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Новые русские сказки

import os, sys, io, struct
from PIL import Image
import numpy as np
import io

NAME = "Новые русские сказки"
TYPES_FILES = [('png Images', ('*.png')),('tga Images', ('*.tga')),('spr Images', ('*.spr'))]
FORMATS_FILES = ["png","tga","spr"]
GAMES = ["Новые русские сказки"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["png",
                            "tga",
                            "spr"]
        self.sup_types = {"png":1,
                          "tga":1,
                          "spr":1}
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

        if format in ["png","tga"]:
            self.Unpack_PNG(f2)
        elif format == "spr":
            self.Unpack_SPR(f2)

    def Unpack_PNG(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_SPR(self, f):
        type = f.read(8) # Тип
        if type != b'\x04\x00\x00\x00aspr': # Проверка
            print("ЭТО НЕ картинка",type)
            return(0) # Остановка скрипта

        col_32 = struct.unpack("<I",f.read(4))[0] # Количество строчек по 32 байта
        poz = 12+(col_32*32) # Позиция данных дальше
        f.seek(poz)
        col = struct.unpack("<I",f.read(4))[0] # Длина имени
        f_path = f.read(col).decode("utf8") # Имя с путём файла
        new_picture_w = struct.unpack("<I",f.read(4))[0] # Ширина картинкина которую заносится вырезанная часть  800
        new_picture_h = struct.unpack("<I",f.read(4))[0] # Ширина 600
        w, h = struct.unpack("<II",f.read(8)) # Ширина и высота полотна картинки
        multiply_w_h = struct.unpack("<I",f.read(4))[0] # Значение ширину умножить на высоту w*h

        f_image = Image.frombuffer('RGBA', (w,h), f.read(multiply_w_h*4), 'raw', 'BGRa', 0, 1) # Создание полотна для вырезания
        img = Image.new("RGBA", (new_picture_w, new_picture_h),(255,255,255,0)) # Создание новой картинки с белым фоном в скобачках ширина и высота картинки Сделал прозрачный задний фон

        f.seek(12) # Начало строчек по 32 байта
        for i in range(col_32):
            # Чтение 4 байт в режиме float
            # Для чтение картинки из файла
            unclear_1, unclear_2, unclear_3, unclear_4 = struct.unpack("ffff",f.read(16))
            # Для наложения на картинку  Тут получаются целые числа
            unclear_5, unclear_6, unclear_7, unclear_8 = struct.unpack("ffff",f.read(16))

            # Координаты вырезания картинки
            number_1 = int(w*unclear_1) # Значение получается с дробной частью 0.5
            number_2 = int(h*unclear_2)
            number_3 = int(w*unclear_3)
            number_4 = int(h*unclear_4)

            # Координаты вставки
            number_5 = int(unclear_5)
            number_6 = int(unclear_6)
            number_7 = int(unclear_7+1)
            number_8 = int(unclear_8+1)

            f_image_2 = f_image.crop((number_1,number_2, number_3,number_4)) # Вырезаем картинку
            img.paste(f_image_2,(number_5,number_6)) # Вставляем картинку в картинку
            f_image_2.close()

        f_image.close()
        f.close()
        self.images.append(img)