#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Капитан Пронин - Один Против Всех

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Капитан Пронин - Один Против Всех" 
FORMATS_ARCHIVE = [".RMT"]
TYPES_ARCHIVE = [('Капитан Пронин - Один Против Всех', ("*.RMT"))]
GAMES = ["Капитан Пронин - Один Против Всех"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["bmp",
                            "cur",
                            "wav"]
       
        self.sup_types = {"bmp":1,
                          "cur":1,
                          "wav":3}
        self.images = []  
        self.sound = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "rmt":
            self.OpenArchiveRMT(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "bmp":
            self.Unpack_BMP(io.BytesIO(self.file.read(size)),data_res[4],data_res[5])
        elif format == "cur":
            self.Unpack_CUR(io.BytesIO(self.file.read(size)))
        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))

    def OpenArchiveRMT(self,file):
        f = open(file,"rb")
        Search_byte = b'\xbc\x01\xe0\xd6\nm6e\xcf\x11\x9d}\x00\xaa\x00`\xfb\xbc' # HEX значение для поиска байт BC 01 E0 D6 0A 6D 36 65 CF 11 9D 7D 00 AA 00 60 FB BC
        dataf = f.read() # Читаем весь файл и записываем его в dataf для поиска
        yy = 0 # Первая точка 
        offset = 0  # Найденная позиция байта
        while offset > -1:
            offset = dataf.find(Search_byte,yy) # Поиск значения Search_byte, по месту нахождения в файле yy
            if offset > -1: # Если нашли файл
                f.seek(offset+18)
                # 56 байт непонятные данные
                col_b = struct.unpack("<I",f.read(4))[0]*2 # Размер
                f_path = f.read(col_b).decode("UTF-16") # Путь и имя файла
                unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно всегда 12 
                cvid_1 = f.read(4) # Непонятно если тут 63 76 69 64 это анимация cvid
                unclear_3 = struct.unpack("<I",f.read(4))[0] # Непонятно 10000
                unclear_4 = struct.unpack("<I",f.read(4))[0] # Непонятно размер картинки +42 
                unclear_5 = struct.unpack("<I",f.read(4))[0] # Непонятно
                w,h = struct.unpack("<II",f.read(8)) # Ширина и высота

                # Удаляем начало имени d:\\ или \\
                if f_path[:3] == "D:\\" or f_path[:3] == "d:\\":
                    f_path = f_path[3:]
                elif f_path[:1] == "\\":
                    f_path = f_path[2:]
                format = f_path.split(".")[-1].lower()

                if f_path[-3:] == "bmp" and cvid_1 != b'cvid' or f_path[-3:] == "BMP" and cvid_1 != b'cvid': # Если не равна cvid
                    if w == 115: # Исправления ширины картинки
                        w = 116
                    f.seek(offset+18+4+col_b+56)
                    posf = f.tell() # Начало файла
                    self.data.append((f_path,posf,w*h*3,format,w,h))  

                elif f_path[-3:] == "bmp" or f_path[-3:] == "BMP":
                    pass
                    #print("   Это не картинка  Может анимация ?")
                    
                elif f_path[-3:] == "wav": # Звук
                    f.seek(offset+18+4+col_b+20)
                    posf = f.tell() # Начало звука
                    f.read(4)
                    size = struct.unpack("<I",f.read(4))[0]+8 # Размер файла
                    self.data.append((f_path,posf,size,format))

                elif f_path[-3:] == "cur": # Курсор
                    f.seek(offset+18+4+col_b)
                    size = struct.unpack("<I",f.read(4))[0] # Размер
                    posf = f.tell() # Начало файла
                    self.data.append((f_path,posf,size,format))

                elif f_path[-3:] == "mpg": # Файл вне архива
                    pass
                else:
                    print("Непонятно что за файл")
            yy = offset + 1 # Позиция дальше для поиска в файле
        self.file = f
        
    def Unpack_WAV(self, f):
        self.sound = f
        
    def Unpack_CUR(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_BMP(self, f,w,h):
        rgb = np.frombuffer(f.read(w*h*3), dtype = np.uint8)
        rgb = np.array(rgb,np.uint8).reshape(h, w, 3)
        b,g,r = np.rollaxis(rgb, axis = -1)
        rgb = np.dstack([r,g,b])
        self.images.append(Image.fromarray(rgb, "RGB").transpose(Image.FLIP_TOP_BOTTOM))