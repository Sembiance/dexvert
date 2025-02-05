#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Zanzarah The Hidden Portal

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Zanzarah The Hidden Portal" 
FORMATS_ARCHIVE = ['pak']
TYPES_ARCHIVE = [('Zanzarah The Hidden Portal', ('*.pak', '*.bcf'))]
GAMES = ["Zanzarah The Hidden Portal"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["bmp",
                            "mp3",
                            "wav",
                            "pic"]

        self.sup_types = {"bmp":1,
                          "mp3":3,
                          "wav":3,
                          "pic":1}

        self.images = []  
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "pak":
            self.OpenArchivePAK(file)

        elif format == "bcf":
            self.OpenArchiveBCF(file)

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

        elif format == "mp3" or format == "wav":
            self.Unpack_MP3(io.BytesIO(self.file.read(size)))

        elif format == "pic":
            self.Unpack_PIC(io.BytesIO(self.file.read(size)))

    def OpenArchivePAK(self,file):
        self.data = []
        data2 = [] # Список файлов с неточным оффсетом
        f = open(file,"rb")

        unclear = struct.unpack("<I",f.read(4))[0] # Непонятно
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов

        for i in range(col):
            name_length = struct.unpack("<I",f.read(4))[0] # Длина имени
            f_path = f.read(name_length).decode("utf8")[3:] # Имя и путь файла
            offset = struct.unpack("<I",f.read(4))[0]+4 # Оффсет +4 Пропускаем ненужные байты
            size = struct.unpack("<I",f.read(4))[0]-4 # Размер
            format = f_path.split(".")[-1].lower()
            data2.append((f_path,offset,size,format))

        posf = f.tell() # Нужно для правельного расчёта оффсета

        for i in data2:
            f.seek(i[1]+posf+(i[2]-4))
            fd = f.read(4) # Проверка на конечные 4 байта
            if fd == b'\x01\x01\x00\x00': # Надо удалить из размера ненужные байты в конце файла -4
                self.data.append((i[0],i[1]+posf,i[2]-4,i[3])) # Делаем правельный оффсет
            else:
                self.data.append((i[0],i[1]+posf,i[2],i[3])) # Делаем правельный оффсет
        self.file = f

    def OpenArchiveBCF(self,file):
        self.data = []
        data2 = [] # Список только оффсеты
        f = open(file,"rb")

        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)

        offset_tab = struct.unpack("<I",f.read(4))[0] # Оффсет таблицы файлов
        f.seek(offset_tab)

        col = (end_f-offset_tab)//4 # Получаем количество файлов
        for i in range(col):
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            data2.append(offset)

        data2.append(end_f) # Для правельного расчёта размера файла

        for i in range(col):
            size = data2[i+1]-data2[i] # Получаем размер файла
            self.data.append((str(data2[i])+".pic",data2[i],size,"pic"))

        self.file = f

    def Unpack_MP3(self, f):
        self.sound = f

    def Unpack_BMP(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_PIC(self, f):
        f.seek(16)
        w, h = struct.unpack("<HH",f.read(4)) # Ширина и высота
        f.seek(36)
        self.images.append(Image.frombuffer('RGB', (w,h), f.read(w*h*3), 'raw', 'BGR', 0, 1))
