#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# По следам убийцы
# ФотоОхота

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "По следам убийцы"
FORMATS_FILES = ["002","003","005","006","010","011","jpg","gif","chn","dat","drg","fme","lks","obj","txt","version","distribution","general","texts","variables"]
TYPES_FILES = [('002 Images', ('*.002')),('003 Images', ('*.003')),('005 Images', ('*.005')),('006 Images', ('*.006')),('010 Sound', ('*.010')),('011 Sound', ('*.011')),('jpg Images', ('*.jpg')),('gif Images', ('*.gif')),('chn tex', ('*.chn')),('dat tex', ('*.dat')),('drg tex', ('*.drg')),('fme tex', ('*.fme')),('lks tex', ('*.lks')),('obj tex', ('*.obj')),('txt tex', ('txt'))]
GAMES = ["По следам убийцы",
         "ФотоОхота"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["002",
                            "003",
                            "005",
                            "006",
                            "010",
                            "011",
                            "jpg",
                            "gif",
                            "chn",
                            "dat",
                            "drg",
                            "fme",
                            "lks",
                            "obj",
                            "txt"]

        self.sup_types = {"002":1,
                          "003":1,
                          "005":1,
                          "006":1,
                          "010":3,
                          "011":3,
                          "jpg":1,
                          "gif":1,
                          "chn":4,
                          "dat":4,
                          "drg":4,
                          "fme":4,
                          "lks":4,
                          "obj":4,
                          "txt":4}
        self.images = []
        self.sound = None
        self.text = None

    def open_files(self,files):
        for i in files:
            right_quote = i[0].rfind('\\')
            name = i[0][right_quote+ 1:]
            if name in ["Distribution","General","Texts","Variables","Version"]:
                self.data.append((i[0],i[1],i[2],'txt'))
            else:
                self.data.append(i)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None

        name = data_res[0]
        size = data_res[2]
        format = data_res[3]

        f = open(name,"rb")
        f2 = io.BytesIO(f.read(size))
        f.close()
        if format == "002" or format == "003":
            self.Unpack_002(f2)
        elif format in ["005", "006", "jpg", "gif",]: # jpg gif
            self.Unpack_JPG(f2)
        elif format == "010" or format == "011": # wav mid
            self.Unpack_WAV(f2)
        elif format in ["chn","dat","drg","fme","lks","obj","txt"]:
            self.Unpack_TXT(f2)

    def Unpack_JPG(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_002(self, f):
        f.seek(0,2)
        end_f = f.tell()

        pal = [] # Палитра
        rgb = []
        w = 32
        h = 32    
        f.seek(62)

        if end_f == 2238:
            for i in range(256):
                r,g,b,a = struct.unpack("4B",f.read(4))
                pal.append((r,g,b,255))
                #pal.append((r,g,b,a))

            for i in range(w*h):
                fd = struct.unpack("B",f.read(1))[0]
                rgb.extend(pal[fd])
            rgb = np.array(rgb,np.uint8).reshape(h, w, 4)
            self.images.append(Image.fromarray(rgb,"RGBA"))

        elif end_f == 766: # 4 битные картинки
            for i in range(16):
                r,g,b,a = struct.unpack("4B",f.read(4))
                pal.append((r,g,b,255))

            for i in range(w*h//2):
                bit = struct.unpack("B",f.read(1))[0] # Байт с двумя цветами
                colour_1 = bit >> 4 # Первый цвет
                colour_2 = bit & 15 # Второй цвет
                #print("Байт",bit,"Цвета",colour_1,colour_2)
                rgb.extend(pal[colour_1])
                rgb.extend(pal[colour_2])
            rgb = np.array(rgb,np.uint8).reshape(h, w, 4)
            self.images.append(Image.fromarray(rgb,"RGBA"))

        #elif end_f == 326: # 4 битные картинки непонятно ширина картинки и высота

        else:
            print("Не поддерживается")

    def Unpack_TXT(self, f): 
        self.text = f.read().decode("cp1251")