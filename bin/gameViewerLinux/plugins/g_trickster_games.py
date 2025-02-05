#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Trickster Games
# Приключения барона Мюнхгаузена на Луне   [.pak]       [.dds .wav]
# Танита, или Морское Приключение          [.pak, .vid] [.pic, .wav]

import os, sys, io, struct
from PIL import Image

NAME = "Trickster Games"
FORMATS_ARCHIVE = ['pak']
TYPES_ARCHIVE = [('Trickster Games', ('*.pak', '*.vid'))]
GAMES = ["Приключения барона Мюнхгаузена на Луне",
         "Танита, или Морское Приключение"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["dds",
                            "pic",
                            "wav"]  

        self.sup_types = {"dds":1,
                          "pic":1,
                          "wav":3}

        self.images = []
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "pak":
            self.OpenArchivePAK(file)

        elif format == "vid":
            self.OpenArchiveVID(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)

        if format == "dds":
            self.Unpack_DDS(io.BytesIO(self.file.read(size)))

        elif format == "pic":
            self.Unpack_PIC(io.BytesIO(self.file.read(size)))

        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))

    def OpenArchiveVID(self,file):
        self.data = [] # Список файлов
        f = open(file,"rb")
        f.seek(0,2)
        size = f.tell() # Конец файла
        self.data.append(("1.avi", 0, size, "avi"))
        self.file = f

    def OpenArchivePAK(self,file):
        self.data = [] # Список файлов

        f = open(file,"rb")
        type = f.read(4) # Тип архива

        # Танита, или Морское Приключение
        if type == b'ahh\x00': # Проверка на архив
            data_0 = [] # Список
            col_tab = struct.unpack("<I",f.read(4))[0] # Количество таблиц

            for i in range(col_tab): # Читаем таблицы
                unclear = f.read(4) # Непонятно
                col = struct.unpack("<I",f.read(4))[0] # Количество файлов

                for i in range(col): # Читаем строчки про файлы
                    unclear_1 = f.read(4) # Непонятно
                    size = struct.unpack("<I",f.read(4))[0] # Размер
                    offset = struct.unpack("<I",f.read(4))[0] # Оффсет
                    unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно
                    unclear_3 = struct.unpack("<I",f.read(4))[0] # Непонятно
                    unclear_4 = struct.unpack("<I",f.read(4))[0] # Непонятно
                    data_0.append((offset, size))

            f_pos = f.tell()
            # Этот код сделан здесь, потому что чтобы перйти на файл надо прочитать полностью таблицу файлов только тогда узнаем где она кончается, это и будет началом файлов 

            for i in data_0: # Проверям на тип файла
                f.seek(i[0] + f_pos) # Преходим на начало файла правельно
                check = f.read(4) # Проверка

                if check == b'\x50\xF4\x00\x00': # Картинки DDS
                    tip = "pic"

                elif check == b'RIFF': # Звук wav
                    tip = "wav"

                elif check == b'\x1BLua': # Скрипт
                    tip = "infb"

                elif check == b'PFD0': # Непонятно
                    tip = "PFD0"

                else:
                    tip = "bin"

                self.data.append((str(i[0]+f_pos)+"."+tip, i[0]+f_pos, i[1], tip))

        # Приключения барона Мюнхгаузена на Луне
        elif type == b'PAK2':
            col = struct.unpack("<I",f.read(4))[0] # Количество файлов

            for i in range(col):
                unclear_1 = f.read(8) # Непонятно
                size = struct.unpack("<I",f.read(4))[0] # Размер
                offset = struct.unpack("<I",f.read(4))[0] # Оффсет
                unclear_2 = f.read(8) # Непонятно

                f_pos = f.tell()
                f.seek(offset)
                check = f.read(4) # Проверка

                if check == b'DDS ': # Картинки DDS
                    tip = "dds"

                elif check == b'RIFF': # Звук wav
                    tip = "wav"

                elif check == b'\x1BLua': # Скрипт
                    tip = "infb"

                else:
                    tip = "bin"

                f.seek(f_pos) # Возврат к таблице
                self.data.append((str(offset)+"."+tip, offset, size, tip))

        self.file = f

    def Unpack_WAV(self, f):
        try: # Исключения
            self.sound = f
        except :
            print("Не поддерживается")

    def Unpack_PIC(self, f):
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)
        type = f.read(4) # Тип архива

        if type != b'\x50\xF4\x00\x00': # Проверка
            print("ЭТО НЕ картинка",type)
            return(0) # Остановка скрипта

        w, h = struct.unpack("<II",f.read(8)) # Ширина и высота
        tip = f.read(4)

        if 16+((w*h)*4) == end_f: # BGRA 32 бита Цвета в другом порядке 
            self.images = [Image.frombuffer('RGBA', (w,h), f.read(w*h*4), 'raw', 'BGRA', 0, 1)]

        elif 16 +(((w*h) // 16) * 16) == end_f: # DDS(DXT3)
            f.seek(4)
            w_fd = f.read(4) # Ширина
            h_fd = f.read(4) # Высота

            f.seek(16)
            fd = f.read() # Картинка

            f2 = io.BytesIO(b'DDS |\x00\x00\x00\x07\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x04\x00\x00\x00DXT3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00') # Заголовок 128 байт
            f2.seek(12) # Позиция ширины и высоты
            f2.write(h_fd) # Записываем ширину
            f2.write(w_fd) # Записываем высоту

            f2.seek(0,2)
            f2.write(fd) # Записываем картинку
 
            self.images = [Image.open(f2)]

        else:
            print("Непонятный тип картинки", "размер файла",end_f)

    def Unpack_DDS(self, f):
        try: # Исключения
            image = Image.open(f)
            self.images = [image]
        except :
            print("Не поддерживается")