#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Alex kalumb1@ya.ru

# Звёздное Наследие 1. Черная Кобра
# Вечера на хуторе близ Диканьки 2: Вечер накануне Ивана Купала
# Обитаемый остров. Землянин

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Step Creative Group" 
FORMATS_ARCHIVE = [".bpk"]
TYPES_ARCHIVE = [('Step Creative Group', ("*.bpk"))]
GAMES = ["Звёздное Наследие 1. Черная Кобра",
         "Вечера на хуторе близ Диканьки 2: Вечер накануне Ивана Купала",
         "Обитаемый остров. Землянин"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["dds",
                            "png",
                            "tga",
                            "jpg",
                            "ogg",
                            "wav",
                            "config",
                            "font",
                            "imageset",
                            "layout",
                            "looknfeel",
                            "scheme",
                            "xsd",
                            "n3d2",
                            "bat",
                            "fx"]

        self.sup_types = {"dds":1,
                          "png":1,
                          "tga":1,
                          "jpg":1,
                          "ogg":3,
                          "wav":3,
                          "config":4,
                          "font":4,
                          "imageset":4,
                          "layout":4,
                          "looknfeel":4,
                          "scheme":4,
                          "xsd":4,
                          "n3d2":4,
                          "bat":4,
                          "fx":4}
        self.images = []  
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "bpk":
            self.OpenArchiveBPK(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format in ["dds","png","tga","jpg"]:
            self.Unpack_DDS(io.BytesIO(self.file.read(size)))
        elif format == "ogg" or format == "wav":
            self.Unpack_OGG(io.BytesIO(self.file.read(size)))
        elif format in ["config", "font", "imageset", "layout", "looknfeel", "scheme", "xsd", "n3d2", "bat", "fx"]:
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))

    def OpenArchiveBPK(self,file):
        f = open(file,"rb")
        type = f.read(4) # Тип архива BPK
        if type != b'BPK ': # Проверка на архив
            print("ЭТО НЕ АРХИВ")
            return(0)
        tip  = struct.unpack("<H",f.read(2))[0] # Тип зашифрованная таблица файлов или нет
        tip2 = struct.unpack("<H",f.read(2))[0] # Всегда 01 00
        f.read(4) # Непонятно

        if tip == 0: # Звёздное Наследие 1. Черная Кобра
            col_f = struct.unpack("<I",f.read(4))[0] # Количество файлов
            for i in range(col_f):
                f_path = f.read(112).split(b"\x00")[0].decode("utf8") # Имя файлов
                offset = struct.unpack("<I",f.read(4))[0] # Оффсет
                size = struct.unpack("<I",f.read(4))[0]   # Размер
                nuli = struct.unpack("<I",f.read(4))[0]   # Нули
                size2 = struct.unpack("<I",f.read(4))[0]  # Размер 2
                format = f_path.split(".")[-1].lower()
                self.data.append((f_path,offset,size,format))

        elif tip == 1:
            f2 = io.BytesIO()
            f.read(4) # Нули
            col_f = struct.unpack("<I",f.read(4))[0] # Количество файлов
            number_xor = col_f
            for i in range(col_f):
                t_comp = bytearray(f.read(128))
                for k in range(128):
                    number_xor = (214013 * number_xor + 2531011) & 0xffffffff
                    t_comp[k] ^= (number_xor >> 16) & 0xff
                f2.write(t_comp)

            f2.seek(0)
            for i in range(col_f):
                f_path = f2.read(108).split(b"\x00")[0].decode("utf8") # Имя файлов
                offset = struct.unpack("<I",f2.read(4))[0] # Оффсет
                size = struct.unpack("<I",f2.read(4))[0]   # Размер
                nuli = struct.unpack("<I",f2.read(4))[0]   # Нули
                size2 = struct.unpack("<I",f2.read(4))[0]  # Размер 2
                f2.read(4) # Непонятно
                format = f_path.split(".")[-1].lower()
                self.data.append((f_path,offset,size,format))
            f2.close()
        self.file = f
        
    def Unpack_OGG(self, f):
        self.sound = f
        
    def Unpack_TXT(self, f):
        try: # Исключения
            self.text = f.read().decode("utf-8")
        except :
            print("Не поддерживается")

    def Unpack_DDS(self, f):
        try: # Исключения
            image = Image.open(f)
            self.images = [image]
        except :
            print("Не поддерживается")