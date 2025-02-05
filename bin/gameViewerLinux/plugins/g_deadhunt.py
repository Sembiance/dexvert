#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Deadhunt(Deadhunt - Охотник на Нежить)

import os, sys, io, struct
from PIL import Image

NAME = "Deadhunt"
FORMATS_ARCHIVE = ['idx',"pk5"]
TYPES_ARCHIVE = [('Deadhunt', ('*.idx', "*.pk5"))]
GAMES = ["Deadhunt"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["bin_jpg",
                            "ogg",
                            "csv"]  

        self.sup_types = {"bin_jpg":1,
                          "ogg":3,
                          "csv":4}

        self.images = []
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "idx":
            self.OpenArchiveIDX(file)
        elif format == "pk5":
            self.OpenArchivePK5(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "bin_jpg":
            self.Unpack_BIN_JPG(io.BytesIO(self.file.read(size)))
        elif format == "ogg":
            self.Unpack_OGG(io.BytesIO(self.file.read(size)),size)
        elif format == "csv":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)),size)

    def OpenArchivePK5(self,file):
        f = open(file,"rb")
        fd = bytearray(f.read(4))
        for i in range(len(fd)):
            fd[i] = fd[i] ^ 0xFF
        col = struct.unpack("<I",fd)[0] # Количество файлов

        fd = bytearray(f.read(col*268)) # Читаем и расшифровываем таблицу файлов
        for i in range(len(fd)):
            fd[i] = fd[i] ^ 0xFF

        f2 = io.BytesIO(fd)
        for i in range(col):
            filename = f2.read(260).split(b"\x00")[0].decode("cp1251") # Имя файла
            size = struct.unpack("<I",f2.read(4))[0] # Размер
            offset = struct.unpack("<I",f2.read(4))[0] # Оффсет
            format = filename.split(".")[-1].lower()
            self.data.append((filename,offset,size,format))
        self.file = f

    def OpenArchiveIDX(self,file):
        data = [] # Оффсеты
        f = open(file,"rb")

        pa,mult_file = os.path.split(file)

        if mult_file[:-4] == "Textures":
            f2 = pa+"\\"+"Textures.tex"
        elif mult_file[:-4] == "MeshCnts":
            f2 = pa+"\\"+"MeshCnts.msh"
        elif mult_file[:-4] == "HMeshes":
            f2 = pa+"\\"+"HMeshes.obj"
        else:
            print("Ошибка")
            return(0) # Остановка скрипта

        if not os.path.exists(f2):
            raise Exception("Файл {} не найден".format(f2))

        self.file = open(f2,"rb")

        self.file.seek(0,2)
        end_f = self.file.tell() # Конец файла
        self.file.seek(0)
        col = struct.unpack("<H",f.read(2))[0] # Количество файлов
        for i in range(col):
            f.read(2) # Непонятно
            f.read(2) # Непонятно
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            data.append(offset)
        data.append(end_f)

        for i in range(len(data)-1):
            size = data[i+1]-data[i] # Расчёт размера файла

            self.file.seek(data[i]+212)
            check = self.file.read(4) # Проверка
            if check == b'\xFF\xD8\xFF\xEE' or check == b'\xFF\xD8\xFF\xE0': # jpg
                format = "bin_jpg"
            else:
                format = "bin"
            self.data.append((str(data[i])+"."+format,data[i],size,format))
        f.close()

    def Unpack_OGG(self, f, size):
        fd = f.read(size)
        fd = bytearray(fd)
        for i in range(len(fd)):
            fd[i] = fd[i] ^ 0xFF
        f2 = io.BytesIO(fd)
        self.sound = f2

    def Unpack_TXT(self, f, size):
        fd = f.read(size)
        fd = bytearray(fd)
        for i in range(len(fd)):
            fd[i] = fd[i] ^ 0xFF
        f2 = io.BytesIO(fd)
        self.text = f2.read().decode("cp1251")

    def Unpack_BIN_JPG(self, f):
        f.seek(132)
        size = struct.unpack("<I",f.read(4))[0] # Размер
        f.seek(212)
        fd = f.read(size)
        f2 = io.BytesIO(fd)
        self.images = [Image.open(f2)]