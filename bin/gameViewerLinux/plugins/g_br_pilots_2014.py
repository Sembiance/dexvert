#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Братья Пилоты. По следам полосатого слона Версия 2014  [tex tga png ico wav mp3 ogg txt log]
# Братья Пилоты. Дело о серийном маньяке Версия 2014     [tex tga png ico mp3 ogg txt log]
# Братья Пилоты. Обратная сторона Земли Версия 2015      [tex tga png ico mp3 ogg txt log]

import os, sys, io, struct
from PIL import Image
import numpy as np
import io
import zlib

NAME = "Братья Пилоты Версия 2014-2015"
TYPES_FILES = [('tex Images', ('*.tex')),('tga Images', ('*.tga')),('png Images', ('*.png')),('ico Images', ('*.ico')),('wav Sound', ('*.wav')),('mp3 Sound', ('*.mp3')),('ogg Sound', ('*.ogg')),('txt Text', ('*.txt')),('log Text', ('*.log'))]
FORMATS_FILES = ["tex","tga","png","ico","wav","mp3","ogg","txt","log"]
GAMES = ["Братья Пилоты. По следам полосатого слона Версия 2014",
         "Братья Пилоты. Дело о серийном маньяке Версия 2014",
         "Братья Пилоты. Обратная сторона Земли Версия 2015"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["tex",
                            "tga",
                            "png",
                            "ico",
                            "wav",
                            "mp3",
                            "ogg",
                            "txt",
                            "log"]
        self.sup_types = {"tex":1,
                          "tga":1,
                          "png":1,
                          "ico":1,
                          "wav":3,
                          "mp3":3,
                          "ogg":3,
                          "txt":4,
                          "log":4}
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

        if format in ["tga","png","ico"]:
            self.Unpack_PNG(f2)
        elif format in ["wav","mp3","ogg"]:
            self.Unpack_WAV(f2)
        elif format in ["txt", "log"]:
            self.Unpack_TXT(f2)
        elif format == "tex":
            self.Unpack_TEX(f2)
            
    def Unpack_PNG(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_TXT(self, f): 
        self.text = f.read().decode("utf8")

    def Unpack_TEX(self, f):
        w,h = struct.unpack("<HH",f.read(4)) # Ширина и высота
        format = f.read(2) # Формат картинки
        unclear_2 = struct.unpack("<H",f.read(2))[0] # Непонятно
        size = struct.unpack("<I",f.read(4))[0] # Размер сжатых данных дальше
        fd = f.read()
        f.close()
        databyte = zlib.decompress(fd)

        f2 = io.BytesIO(databyte)
        f2.seek(0,2)
        end_f2 = f2.tell() # Конец файла
        f2.seek(0)
        if format == b'\x10\x00': # RGBA4444
            rgb = np.frombuffer(f2.read(w*h*2), dtype=np.uint16)
            rgb = np.array(rgb, np.uint16).reshape(h, w)
            r,g,b,a = self.Color3(rgb)
            rgb = np.dstack((r,g,b,a))
            rgb = np.uint8(rgb)
            f_image = Image.fromarray(rgb, "RGBA")

        elif format == b'\x12\x00':
            f_image = Image.frombuffer('RGBA', (w,h), f2.read(w*h*4), 'raw', 'RGBA', 0, 1)
        else:
            print("ОШИБКА неизвестный формат картинки")
            return(0)

        if end_f2 != f2.tell():
            print("ОШИБКА в конце файла остались ещё данные",end_f2-f2.tell())
            print(w,h,format,unclear_2)
        self.images.append(f_image)

    def Color3(self,p):
        # Третья формула RGBA4444
        a = ((p & 15)<<4)
        b = (((p >> 4)& 15))<<4 
        g = (((p >> 8)& 15))<<4
        r = (((p >> 12)& 15))<<4
        return (r,g,b,a)