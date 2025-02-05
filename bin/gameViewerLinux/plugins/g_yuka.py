#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Koisuru Shimai no Sextet                      [YKC, PNG, OGG, INI, TXT]
# Akane Iro ni Somaru Saka                      [YKC, PNG, BMP, YKG, OGG, WAV, INI]
# SuGirly Wish                                  [YKC, YKG, OGG, INI]
# Hoshizora e Kakaru Hashi                      [YKC, PNG, YKG, OGG, INI]
# Hoshizora e Kakaru Hashi AA                   [YKC, PNG, YKG, OGG, INI]
# Iinazuke wa Imouto-sama!                      [YKC, PNG, YKG, OGG, INI, DATA, YKP]
# Koi x Koi = Infinity                          [YKC, PNG, YKG, OGG, INI]
# Shitsuji ga Aruji o Erabu Toki                [YKC, PNG, YKG, OGG, INI, DATA, YKP, TXT]
# Tsun na Kanojo Dere na Kanojo                 [YKC, PNG, YKG, OGG, INI]
# Amakan Ecchi na "Love Icha" Tsumechaimashita  [YKC, PNG, YKG, OGG, INI]
# Lover Able                                    [YKC, YKG, OGG, INI]
# Dousei Lover Able                             [YKC, YKG, OGG, INI]
# Lovely Quest                                  [YKC, YKG, OGG, INI]
# PriministAr                                   [YKC, PNG, YKG, OGG, INI, CUR]
# PriministAr Mini Fandisc Enamori Senri & Koma Kayano Ver [YKC, PNG, YKG, OGG, INI, CUR]
# Strawberry Nauts                              [YKC, YKG, OGG, INI, CUR]
# Zutto Tsukushite Ageru no!                    [YKC, PNG, YKG, OGG, INI]
# Kimi o Aogi Otome wa Hime ni                  [YKC, PNG, YKG, OGG, INI, TXT, BAK, DATA]
# Ama Ane                                       [YKC, PNG, YKG, OGG, INI, DATA]

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Yuka" 
FORMATS_ARCHIVE = ['ykc']
TYPES_ARCHIVE = [('Yuka', ('*.ykc'))]
GAMES = ["Koisuru Shimai no Sextet",
         "Akane Iro ni Somaru Saka",
         "SuGirly Wish",
         "Hoshizora e Kakaru Hashi",
         "Hoshizora e Kakaru Hashi AA",
         "Iinazuke wa Imouto-sama!",
         "Koi x Koi = Infinity",
         "Shitsuji ga Aruji o Erabu Toki",
         "Tsun na Kanojo Dere na Kanojo",
         "Amakan Ecchi na Love Icha Tsumechaimashita",
         "Lover Able",
         "Dousei Lover Able",
         "Lovely Quest",
         "PriministAr",
         "PriministAr Mini Fandisc Enamori Senri & Koma Kayano Ver",
         "Strawberry Nauts",
         "Zutto Tsukushite Ageru no!",
         "Kimi o Aogi Otome wa Hime ni",
         "Ama Ane"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["png",
                            "bmp",
                            "ykg",
                            "ogg",
                            "wav",
                            "ini",
                            "data",
                            "ykp",
                            "txt",
                            "cur",
                            "bak"]

        self.sup_types = {"png":1,
                          "bmp":1,
                          "ykg":1,
                          "ogg":3,
                          "wav":3,
                          "ini":4,
                          "data":4,
                          "ykp":4,
                          "txt":4,
                          "cur":1,
                          "bak":4}

        self.images = []  
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "ykc":
            self.OpenArchiveYKC(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "png" or format == "bmp" or format == "cur":
            self.Unpack_PNG(io.BytesIO(self.file.read(size)))
        elif format == "ogg" or format == "wav":
            self.Unpack_OGG(io.BytesIO(self.file.read(size)))
        elif format == "ykg":
            self.Unpack_YKG(io.BytesIO(self.file.read(size)))
        elif format in ["ini", "data", "ykp", "txt", "bak"]:
            self.Unpack_INI(io.BytesIO(self.file.read(size)))

    def OpenArchiveYKC(self,file):
        self.data = []

        f = open(file,"rb")
        type = f.read(8) # Тип архива YKC001
        if type != b'YKC001\x00\x00': # Проверка на архив
            print("ЭТО НЕ АРХИВ",type)
            return(0) # Остановка скрипта

        f.seek(0,2)
        end_f = f.tell()
        f.seek(16)
        offset_tb = struct.unpack("<I",f.read(4))[0] # Оффсет таблицы файлов

        f.seek(offset_tb)
        col = (end_f - offset_tb)// 20 # Количество файлов

        for i in range(col):
            offset_filename = struct.unpack("<I",f.read(4))[0] # Оффсет имени файла
            len_b = struct.unpack("<I",f.read(4))[0]  # Длина имени
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size = struct.unpack("<I",f.read(4))[0]   # Размер
            zeros = struct.unpack("<I",f.read(4))[0]  # 4 байта нули

            posf = f.tell()
            f.seek(offset_filename)  # Переход на имя файла
            filename = f.read(len_b) # Читаем имя файла
            f.seek(posf) # Возвращение к таблицы

            filename = filename.split(b"\x00")[0].decode("shift-jis").replace("\\\\","\\")
            format = filename.split(".")[-1].lower()
            self.data.append((filename,offset,size,format))
        self.file = f

    def Unpack_OGG(self, f):
        self.sound = f

    def Unpack_PNG(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_INI(self, f):
        self.text = f.read().decode("shift-jis")

    def Unpack_YKG(self, f):
        type = f.read(8)
        if type != b'YKG000\x00\x00': # Проверка
            print("ЭТО НЕ КАРТИНКА",type)
            return(0)

        f.seek(56)
        size = struct.unpack("<I",f.read(4))[0] - 64 # Размер
        f.read(4)
        fd = f.read(size)
        f2 = io.BytesIO(fd)
        f2.seek(0)
        f2.write(b"\x89PNG")
        image = Image.open(f2)
        self.images = [image]
