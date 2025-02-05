#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Для версии v2.3

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Fuguriya" 
FORMATS_ARCHIVE = ["BGM", "DATA", "MGD", "MSD", "SE", "VOICE"]
TYPES_ARCHIVE = [('Fuguriya', ("BGM", "DATA", "MGD", "MSD", "SE", "VOICE"))]
GAMES = ["Hanahira!",
         "Sono Hanabira ni Kuchizuke o",                                  # 1
         "Sono Hanabira ni Kuchizuke o - Watashi no Ouji-sama",           # 2
         "Sono Hanabira ni Kuchizuke o - Anata to Koibito Tsunagi",       # 3
         "Sono Hanabira ni Kuchizuke o - Itoshisa no Photograph",         # 4
         "Sono Hanabira ni Kuchizuke o - Anata o Suki na Shiawase",       # 5
         "Sono Hanabira ni Kuchizuke o - Kuchibiru to Kisu de Tsubuyaite",# 6
         "Sono Hanabira ni Kuchizuke o - Amakute Hoshikute Torokeru Chu", # 7
         "Sono Hanabira ni Kuchizuke o - Tenshi no Hanabirazome",         # 8
         "Sono Hanabira ni Kuchizuke o - Amakute Otona no Torokeru Chuu", # 9
         "Sono Hanabira ni Kuchizuke o - Lily Platinum",                  # 10
         "Sono Hanabira ni Kuchizuke o - Michael no Otome-tachi",         # 11
         "Sono Hanabira ni Kuchizuke o - Anata ni Chikau Ai",             # 17
         "Natsuiro Sagittarius",
         "Natsuiro Sagittarius Gaiden Ayato-kyun no Otoko no Ko Nikki"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["mgd",
                            "bmp",
                            "ogg"]
       
        self.sup_types = {"mgd":1,
                          "bmp":1,
                          "ogg":3}
        self.images = []  
        self.sound = None

    def open_data(self,file):
        (dirname, filename) = os.path.split(file)
        if filename in ["BGM", "DATA", "MGD", "MSD", "SE", "VOICE"]:
            self.OpenArchiveRES(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "mgd":
            self.Unpack_PNG(io.BytesIO(self.file.read(size)))
        elif format == "bmp":
            self.Unpack_BMP(io.BytesIO(self.file.read(size)))
        elif format == "ogg":
            self.Unpack_OGG(io.BytesIO(self.file.read(size))) 

    def OpenArchiveRES(self,file):
        self.data = []

        f = open(file,"rb")
        type = f.read(8) # Тип архива FJSYS..
        if type != b'\x46\x4A\x53\x59\x53\x00\x00\x00': # Проверка на архив 
            print("ЭТО НЕ АРХИВ",type)
            return(0) 
    
        offset_f = struct.unpack("<I",f.read(4))[0] # Оффсет начало файлов
        unclear = struct.unpack("<I",f.read(4))[0] # Непонятно
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        offset_file_name = col*16+84 # Начало таблицы имён файлов
    
        f.seek(84)
        for i in range(col):
            offset_name = struct.unpack("<I",f.read(4))[0]+offset_file_name # Оффсет имени файла
            posf = f.tell()
            f.seek(offset_name)
            f_path = b'' # Читаем имя файла до байта 00
            while True: 
                bait = f.read(1) # Байт строчки
                if bait == b'\x00':
                    filename = f_path.split(b"\x00")[0].decode("utf8")
                    format = filename.split(".")[-1].lower()
                    break
                else:
                    f_path += bait # Прибавляем байт
            f.seek(posf)
            size = struct.unpack("<I",f.read(4))[0] # Размер
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            f.read(4)
            self.data.append((filename,offset,size,format))
        self.file = f
        
    def Unpack_BMP(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_OGG(self, f):
        self.sound = f
        
    def Unpack_PNG(self, f):
        f.seek(96)
        type = f.read(4) # Тип ‰PNG
        if type == b'\x89\x50\x4E\x47': # Проверка на наличее картинки
            f.seek(96)
            fd = f.read()
            f2 = io.BytesIO(fd)
            image = Image.open(f2)
            self.images = [image]