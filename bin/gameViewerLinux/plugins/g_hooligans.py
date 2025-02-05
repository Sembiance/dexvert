#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Hooligans

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Hooligans" 
FORMATS_ARCHIVE = ['x13']
TYPES_ARCHIVE = [('Hooligans', ('*.x13'))]
GAMES = ["Hooligans"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app
        
        self.sup_formats = ["g13",
                            "a13",
                            "txt",
                            "bmp",
                            "wav",]
       
        self.sup_types = {"g13":1,
                          "a13":1,
                          "txt":4,
                          "bmp":1,
                          "wav":3}
        self.images = []   
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "x13":
            self.OpenArchiveX13(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "bmp":
            self.Unpack_BMP(io.BytesIO(self.file.read(size)))

        elif format == "g13":
            self.Unpack_G13(io.BytesIO(self.file.read(size)))
            
        elif format == "a13":
            self.Unpack_A13(io.BytesIO(self.file.read(size)))
            
        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))
            
        elif format == "txt":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))

    def OpenArchiveX13(self,file):
        self.data = [] 
        f = open(file,"rb")
        type = f.read(4) # Тип архива
        if type != b'PACK': # Проверка на архив
            print("ЭТО НЕ АРХИВ",type)
            return(0) # Остановка скрипта

        offset_tab = struct.unpack("<I",f.read(4))[0] # Оффсет таблицы файлов
        size_tab = struct.unpack("<I",f.read(4))[0] # Размер таблицы файлов

        f.seek(offset_tab) # Переходим на начало таблицы
        col = size_tab // 64 # Количество файлов

        for i in range(col):
            f_path = f.read(56).split(b"\x00")[0].decode("utf8") # Имя файла встрочке встречаются непонятные байты возможно они чтото значят
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size = struct.unpack("<I",f.read(4))[0] # Размер
            format = f_path.split(".")[-1].lower()
            self.data.append((f_path,offset,size,format))

        self.file = f

    def Unpack_BMP(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_WAV(self, f):
        self.sound = f
        
    def Unpack_TXT(self, f): 
        self.text = f.read().decode("cp1251")

    def Unpack_G13(self, f):
        f.seek(0,2)
        end_f = f.tell() # Конец файла

        f.seek(31)
        name_length = struct.unpack(">I",f.read(4))[0] # Длина имени файла
        name = f.read(name_length) # Внутрение имя файла

        f.seek(20,1) # Пропускаем следующие 20 байтов
        w, h = struct.unpack(">II",f.read(8)) # Ширина и высота

        if w*h*2 < end_f: # Если файл картинка
            f.seek(40,1) # Пропускаем следующие 40 байтов
            f_image = Image.frombuffer('RGB', (w,h), f.read(w*h*2), 'raw', 'BGR;16', 0, 1)
            self.images.append(f_image)

        else: # Этот файл не картинки
            print("Этот файл не картинки")

        f.close()

    def Unpack_A13(self, f):
        f.seek(16)
        w, h = struct.unpack(">II",f.read(8)) # Ширина и высота
        self.images.append(Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1))
        f.close()