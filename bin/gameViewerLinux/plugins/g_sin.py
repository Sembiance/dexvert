#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# SiN
# SiN: Wages of Sin

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "SiN" 
FORMATS_ARCHIVE = ['sin']
TYPES_ARCHIVE = [('SiN', ('*.sin'))]
GAMES = ["SiN",
         "SiN: Wages of Sin"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app
        
        self.sup_formats = ["swl",
                            "tga",
                            "def",
                            "e31",
                            "e32",
                            "e33",
                            "e34",
                            "hdh",
                            "hdl",
                            "iml",
                            "imh",
                            "mn1",
                            "mnu",
                            "mus",
                            "scr",
                            "tmp",
                            "txt",
                            "000",
                            "001",
                            "002",
                            "003",
                            "004",
                            "005",
                            "006",
                            "007",
                            "008",
                            "009",
                            "010",
                            "011",
                            "012",
                            "013",
                            "014",
                            "015",
                            "016",
                            "017",
                            "018",
                            "019",
                            "020",
                            "021",
                            "022",
                            "023",
                            "024",
                            "030",
                            "031",
                            "032",
                            "033",
                            "034",
                            "001a",
                            "006a",
                            "cfg",
                            "lst",
                            "msf",
                            "spr"]
       
        self.sup_types = {"swl":2,
                          "tga":1,
                          "def":4,
                          "e31":4,
                          "e32":4,
                          "e33":4,
                          "e34":4,
                          "hdh":4,
                          "hdl":4,
                          "iml":4,
                          "imh":4,
                          "mn1":4,
                          "mnu":4,
                          "mus":4,
                          "scr":4,
                          "tmp":4,
                          "txt":4,
                          "001":4,
                          "002":4,
                          "003":4,
                          "004":4,
                          "005":4,
                          "006":4,
                          "007":4,
                          "008":4,
                          "009":4,
                          "010":4,
                          "011":4,
                          "012":4,
                          "013":4,
                          "014":4,
                          "015":4,
                          "016":4,
                          "017":4,
                          "018":4,
                          "019":4,
                          "020":4,
                          "021":4,
                          "022":4,
                          "023":4,
                          "024":4,
                          "030":4,
                          "031":4,
                          "032":4,
                          "033":4,
                          "034":4,
                          "001a":4,
                          "006a":4,
                          "cfg":4,
                          "lst":4,
                          "msf":4,
                          "spr":4}
        self.images = []   
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "sin":
            self.OpenArchiveSIN(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "tga":
            self.Unpack_TGA(io.BytesIO(self.file.read(size)))
        elif format == "swl":
            self.Unpack_SWL(io.BytesIO(self.file.read(size)))
            
        elif format in ["def","e31","e32","e33","e34","hdh","hdl","iml","imh","mn1","mnu","mus","scr","tmp","txt","000","001","002","003","004","005","006","007","008","009","010","011","012","013","014","015","016","017","018","019","020","021","022","023","024","030","031","032","034","001a","006a","cfg","lst","msf","spr"]:
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))

    def OpenArchiveSIN(self,file):
        self.data = [] 
        f = open(file,"rb")

        type = f.read(4) # Тип архива
        if type != b'SPAK': # Проверка на архив
            print("ЭТО НЕ АРХИВ",type)
            return(0) # Остановка скрипта

        offset_tab = struct.unpack("<I",f.read(4))[0] # Оффсет начало таблицы файлов
        size_tab = struct.unpack("<I",f.read(4))[0] # Размер таблицы файлов
        col = size_tab // 128 # Получаем количество файлов
        f.seek(offset_tab)

        for i in range(col):
            filename = f.read(120).split(b"\x00")[0].decode("utf8") # Имя файла
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size = struct.unpack("<I",f.read(4))[0] # Размер
            format = filename.split(".")[-1].lower()
            self.data.append((filename,offset,size,format))

        self.file = f
        
    def Unpack_TXT(self, f): 
        self.text = f.read().decode("cp1251") # Потдержка русского текста
        
    def Unpack_TGA(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_SWL(self, f):
        data = [] # Список оффсет файлов картинок
        f_path = f.read(64).split(b"\x00")[0].decode("cp866") # Внутрение имя с путём такая кодировка чтоб невызывала ошибку в firergb.swl
        w, h = struct.unpack("<II",f.read(8)) # Ширина и высота

        Pal = b"" # Палитра
        for i in range(256):
            Pal += f.read(3)
            f.read(1)

        unclear = struct.unpack("<I",f.read(4))[0] # Непонятно

        for i in range(4):
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет картинки
            if offset == 0: # Дальше нет оффсетов
                break
            data.append(offset)

        f_path2 = f.read(64).split(b"\x00")[0].decode("cp866") # Внутрение имя с путём
        block = f.read(56) # Блок 56 байт непонятно как читается, по 4 байта ?

        ss = 0 # Номер картинки
        for offset in data:
            ss += 1
            f.seek(offset)
            f_image = Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1)
            f_image.putpalette(Pal)
            self.images.append(f_image)

            # Делить ширину и высоту на 2 
            w = w // 2 
            h = h // 2
        f.close()
