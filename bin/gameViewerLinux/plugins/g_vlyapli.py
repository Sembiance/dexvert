#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Вляпли!

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Вляпли!" 
FORMATS_ARCHIVE = ['Вляпли!']
TYPES_ARCHIVE = [('Вляпли!', ('*.alp', '*.sca', '*.scn', '*.scp'))]
GAMES = ["Вляпли!"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["bmp",
                            "wav",
                            "mp3",
                            "scr",
                            "scc",
                            "prd",
                            "pic"]

        self.sup_types = {"bmp":1,
                          "wav":3,
                          "mp3":3,
                          "scr":4,
                          "scc":4,
                          "prd":4,
                          "pic":1}
        self.images = []
        self.sound = None
        self.text = None
        self.f2 = io.BytesIO() # Псевдо архив в котором будут лежать расшифрованные файлы

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format in ["sca", "scn", "scp"]:
            self.OpenArchiveSCN(file)

        elif format == "alp":
            self.OpenArchiveALP(file)

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

        elif format in ["wav", "mp3"]:
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))

        elif format in ["scc", "prd"]:
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))

        elif format == "scr":
            self.Unpack_TXT_2(io.BytesIO(self.file.read(size)))

        elif format == "pic":
            self.Unpack_PIC(io.BytesIO(self.file.read(size)))

    def OpenArchiveSCN(self,file):
        self.data = [] 
        f = open(file,"rb")
        offset = 0 # Начало файлов

        fd = self.decoding(f, 4) # Расшифровка количество файлов
        col = struct.unpack("<I", fd[:])[0] # Количество файлов

        for ii in range(col):
            col_name = f.read(1)[0] ^ 0xD5 # Расшифровка длины имени внутренего файла

            f_path = self.decoding(f, col_name) # Расшифровка имени файла
            f_path = bytes(f_path).decode("utf8") # Имя файла

            fd = self.decoding(f, 4) # Расшифровка размера файла
            size = struct.unpack("<I",bytes(fd))[0] # Размер файла

            # Файлы полностью зашифрованы
            if f_path[-4:] == ".scc" or (f_path[-4:]).lower() == ".scr": # Для архивов .scp
                fd_1 = self.decoding(f, size) # Расшифровка файла
                self.f2.write(bytes(fd_1)) # Записываем расшифрованный файл

            else: # Файлы частично зашифрованы, для архивов .sca, .scn
                fd_1 = self.decoding(f, 115) # 115 байт Расшифровка начало файла
                self.f2.write(bytes(fd_1)) # Записываем часть расшифрованного файла

                self.f2.write(f.read(size - 115)) # Сколько ещё прочитать байт надо, Часть файла которая не зашфрованна

            filename = str(ii+1)+" "+f_path
            format = f_path.split(".")[-1].lower()
            self.data.append((filename, offset, size, format))
            offset += size # Для правельно расчёта следующего файла

        f.close()
        self.file = self.f2 # Добавляем псевдо архив

    def OpenArchiveALP(self,file):
        self.data = [] 
        f = open(file,"rb")
        offset = 0 # Начало файлов

        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)

        if end_f == 1013844: # Alpha.alp
            col = 104 # Количество картинок
            block_1_size = 232024
            block_2_size = 116220

        elif end_f == 553134: # AlphaRefusal.alp
            col = 54 # Количество картинок
            block_1_size = 138284
            block_2_size = 69250

        w = 160
        h = 40

        for i in range(col):
            self.data.append((str(i)+".pic", offset, 6400, "pic"))
            offset += 6400

        self.data.append((str(col)+".block_1", offset, block_1_size, "block_1"))
        offset += block_1_size

        self.data.append((str(col+1)+".block_2", offset, block_2_size, "block_2"))
        offset += block_2_size

        self.file = f

    def decoding(self, f, col):
        whole, rest = divmod(col, 4) # Делит правельно сначало идёт целое число потом остаток

        xor_key = bytearray(b'\xAC\x6E\x75\x4D' * whole) # XOR ключ AC 6E 75 4D
        fd = bytearray(f.read(whole*4)) # Зашифрованные байты

        for i in range(whole*4):
            fd[i] = fd[i] ^ xor_key[i]

        for i in range(rest): # Если файл не кратен 4 байтам то расшифровываем 1-3 байтов
            fd.append(f.read(1)[0] ^ 0xD5) # Расшифровка байта

        return(fd)

    def Unpack_TXT(self, f): 
        self.text = f.read().decode("cp1251") # Потдержка русского текста
        f.close()

    def Unpack_TXT_2(self, f): # Для файлов .scr
        self.text = f.read().decode("cp866")
        f.close()

    def Unpack_BMP(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_PIC(self, f):
        w = 160
        h = 40
        f_image = Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1)
        self.images = [f_image]
