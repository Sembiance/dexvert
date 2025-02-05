#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Torrente: El Juego (Торренте Ла Бомба)

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Torrente: El Juego"
TYPES_FILES = [('tex Images', ('*.tex')),('jpg Images', ('*.jpg')),('wav Sound', ('*.wav')),('rut Text', ('*.rut'))]
FORMATS_FILES = ["tex","jpg","wav","rut"]
GAMES = ["Torrente: El Juego"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["tex",
                            "jpg",
                            "wav",
                            "rut",]
        self.sup_types = {"tex":2,
                          "jpg":1,
                          "wav":3,
                          "rut":4}
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

        if format == "tex":
            self.Unpack_TEX(f2)
        elif format == "jpg":
            self.Unpack_JPG(f2)
        elif format == "wav":
            self.Unpack_WAV(f2)
        elif format in ["rut"]:
            self.Unpack_TXT(f2)
            
    def Unpack_TXT(self, f): 
        self.text = f.read().decode("utf8")

    def Unpack_JPG(self, f):
        image = Image.open(f)
        self.images = [image]
            
    def Unpack_WAV(self, f):
        self.sound = f
        
    def Unpack_TEX(self, f):
        f.seek(4)
        format_images = struct.unpack("B",f.read(1))[0] # Формат картинки 
        number_images = struct.unpack("B",f.read(1))[0] # Количество картинок
        f.seek(9)
        w = struct.unpack("H",f.read(2))[0] # Ширина
        f.read(2)
        h = struct.unpack("H",f.read(2))[0] # Высота
        f.seek(17)
        #print("Ширина и высота количество файлов",w,h,number_images)
        #print("Формат картинки",format_images)

        if format_images == 0:
            def image(f,w,h):
                rgb = []
                rgb = np.frombuffer(f.read(w*h*3), dtype = np.uint8)
                rgb = np.array(rgb,np.uint8).reshape(h, w, 3)
                r,g,b = np.rollaxis(rgb, axis = -1) # Записанная последовательность в файле
                rgb = np.dstack([r,g,b])
                self.images.append(Image.fromarray(rgb,"RGB"))

            image(f,w,h)
            
            if number_images > 1:
                for i in range(number_images-1): # Повторить количество кадров
                    w = w // 2
                    h = h // 2
                    image(f,w,h)

        elif format_images == 1:
            def image(f,w,h):
                rgb = []
                rgb = np.frombuffer(f.read(w*h*4), dtype = np.uint8)
                rgb = np.array(rgb,np.uint8).reshape(h, w, 4)
                a, r, g, b = np.rollaxis(rgb, axis = -1) # Записанная последовательность в файле
                rgb = np.dstack([r,g,b,a])
                self.images.append(Image.fromarray(rgb,"RGBA"))

            image(f,w,h)
            
            if number_images > 1:
                for i in range(number_images-1): # Повторить количество кадров
                    w = w // 2
                    h = h // 2
                    image(f,w,h)
        else:
            print("НЕПОНЯТНЫЙ ФОРМАТ КАРТИНКИ")    
        f.close()