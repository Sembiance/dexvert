#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Приключения Гарри Улики под нижним бельём

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Приключения Гарри Улики под нижним бельём"
FORMATS_ARCHIVE = ['res']
TYPES_ARCHIVE = [('Приключения Гарри Улики под нижним бельём', ('*.res'))]
GAMES = ["Приключения Гарри Улики под нижним бельём"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["bmp",
                            "wav",
                            "dat"]

        self.sup_types = {"bmp":1,
                          "wav":3,
                          "dat":4}
        self.images = []
        self.sound = None
        self.text = [] # Список для текста
        
    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "res":
            self.OpenArchiveRES(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = [] # Список для текста
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "bmp":
            self.Unpack_BMP(io.BytesIO(self.file.read(size)))
        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))
        elif format == "dat":
            self.Unpack_DAT(io.BytesIO(self.file.read(size)))

    def OpenArchiveRES(self,file):
        f = open(file,"rb")
        (dirname, filename1) = os.path.split(file) # Достаём имя файла
        data2 = [] # Список имён
        type = f.read(2)
        if type != b'\x00\x00': # Проверка на архив 00 00
            print("ЭТО НЕ АРХИВ",type)
            return(0)

        size_name = struct.unpack("<I",f.read(4))[0] # Размер блока с именами
        while f.tell() != size_name+6: # Читаем имена файлов
            name_length = struct.unpack("B",f.read(1))[0]
            filename = f.read(name_length)
            filename = filename.split(b"\x00")[0].decode("cp1251").replace("\\\\","\\")
            if filename1 == "graphics.res": # Добавляем тип файла
                filename += ".bmp"
            elif filename1 == "sounds.res":
                filename += ".wav"
            format = filename.split(".")[-1].lower()
            data2.append((filename,format))
        
        size_table = struct.unpack("<I",f.read(4))[0] # Размер блока с оффсетами
        posf0 = f.tell()

        while f.tell() != posf0+size_table: # Читаем таблицу файлов
            length = struct.unpack("B",f.read(1))[0]-12 # -12 байты которые читаем
            f.read(length) # Читаем непонятные байты
            name_number = struct.unpack("H",f.read(2))[0] # Номер имени
            f.read(1) # Непонятный байт
            offset = struct.unpack("<I",f.read(4))[0]
            size = struct.unpack("<I",f.read(4))[0]
            self.data.append((data2[name_number][0],offset,size,data2[name_number][1]))
        self.file = f
        return 1

    def Unpack_BMP(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_WAV(self, f):
        self.sound = f
        
    def Unpack_DAT(self, f): 
        f.seek(0,2)
        end_f = f.tell()
        f.seek(0)
        text = b'' # Байты текста
    
        for i in range(end_f):
            bait = f.read(1) # Байт 
            if bait in [b'\x00', b'\x80', b'\x81', b'\x82', b'\x83', b'\x84', b'\x85', b'\x86', b'\x87', b'\x88', b'\x89', b'\x8a', b'\x8b', b'\x8c', b'\x8d', b'\x8e', b'\x8f', b'\x90', b'\x91', b'\x92', b'\x93', b'\x94', b'\x95', b'\x96', b'\x97', b'\x98', b'\x99', b'\x9a', b'\x9b', b'\x9c', b'\x9d', b'\x9e', b'\x9f', b'\xa3', b'\xa5', b'\xa6', b'\xa7', b'\xa9', b'\xab', b'\xac', b'\xad', b'\xae', b'\xb1', b'\xb2', b'\xb3', b'\xb4', b'\xb5', b'\xb6', b'\xbb', b'\xbc', b'\xbd', b'\xbe',b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07', b'\x08', b'\t', b'\n', b'\x0b', b'\x0c', b'\r', b'\x0e', b'\x0f', b'\x10', b'\x11', b'\x12', b'\x13', b'\x14', b'\x15', b'\x16', b'\x17', b'\x18', b'\x19', b'\x1a', b'\x1b', b'\x1c', b'\x1d', b'\x1e', b'\x1f', b'\x7f', b'\xa0', b'\xa1', b'\xa2', b'\xa4', b'\xa8', b'\xaa', b'\xaf', b'\xb0', b'\xb7', b'\xb8', b'\xb9', b'\xba', b'\xbf']:
                if text != b'': # Если текст неравен пустой строчки то это текст
                    fd = text.decode("cp1251")
                    self.text.append(fd+"\n")
                text = b''

            else:
                text += bait # Прибавляем байт