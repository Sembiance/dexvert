#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Bud Redhead The Time Chase

import os, sys, io, struct
from PIL import Image
import numpy as np
import io

NAME = "Bud Redhead The Time Chase"
TYPES_FILES = [('gfx Images', ('*.gfx'))]
FORMATS_FILES = ["gfx"]
GAMES = ["Bud Redhead The Time Chase"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["gfx"]
        self.sup_types = {"gfx":1}
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
        type = f.read(4)
        if type != b'GFX1': # Проверка
            print("ЭТО НЕ КАРТИНКА",type)
            return(0) # Остановка скрипта

        unclear = struct.unpack("<I",f.read(4))[0] # Непонятно
        w, h = struct.unpack("<HH",f.read(4)) # Ширина и высота
        #print(w, h,"Непонятно",unclear)
        Pal = f.read(768)
        f2 = io.BytesIO()

        while True:
            check = f.read(1)[0] # Действие
            #print("Действие",check,"позиция",f.tell()-1)

            if check >= 0x6A: # Повторить два следующих байта
                col = check - 0x6A
                fd = f.read(1) # Читаем цвет
                col += 2
                f2.write(fd*col)
                #print("Повторить байта цвета",col,fd)

            elif check == 0:
                #print("Конец файла сжатия")
                break

            else:
                fd = f.read(check)
                f2.write(fd)
                #print("Прочетать цветов",check)

        f.close()
        f2.seek(0)

        f_image = Image.frombuffer('P', (w,h), f2.read(w*h), 'raw', 'P', 0, 1) 
        f_image.putpalette(Pal)
        self.images.append(f_image)
