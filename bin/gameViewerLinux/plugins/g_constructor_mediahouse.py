#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Конструктор комиксов и мультфильмов от МедиаХауз
# Потдерживает игры Тип 1
# Конструктор комиксов - Аниме
# Конструктор комиксов - Фэнтези
# Конструктор игр Симсала Гримм
# Конструктор игр Незнайка на Луне
# Конструктор мультиков и комиксов Незнайка и Баррабасс

# Потдерживает игры Тип 2
# Конструктор мультфильмов Новые Бременские
# Конструктор мультфильмов. Мульти - Пульти  не потдерживает файл ANM_S.LIB там заместо имён байты
# Конструктор мультфильмов. Незнайка и все, все, все
# Конструктор мультиков и комиксов Мои любимые герои

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Конструктор комиксов и мультфильмов от МедиаХауз"
FORMATS_ARCHIVE = ['lib']
TYPES_ARCHIVE = [('Конструктор комиксов и мультфильмов от МедиаХауз', ('*.lib'))]
GAMES = ["Конструктор комиксов - Аниме",
         "Конструктор комиксов - Фэнтези",
         "Конструктор игр Симсала Гримм",
         "Конструктор игр Незнайка на Луне",
         "Конструктор мультиков и комиксов Незнайка и Баррабасс",
         "Конструктор мультфильмов Новые Бременские",
         "Конструктор мультфильмов. Мульти - Пульти",
         "Конструктор мультфильмов. Незнайка и все, все, все", 
         "Конструктор мультиков и комиксов Мои любимые герои"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = [] 
                       
        self.app = app
        
        self.sup_formats = ["png",
                            "bmp",
                            "jpg",
                            "wav"]
 
        self.sup_types = {"png":1,
                          "bmp":1,
                          "jpg":1,
                          "wav":3}
        self.images = [] 
        self.sound = None 
    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "lib":
            self.OpenArchiveLIB(file)
    
    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "png" or format == "jpg":
            self.Unpack_PNG(io.BytesIO(self.file.read(size)))
        elif format == "bmp":
            self.Unpack_BMP(io.BytesIO(self.file.read(size)))
        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))

    def OpenArchiveLIB(self,file):
        f = open(file,"rb")
        f.seek(96)
        type = f.read(16) # Тип архива
        if type == b'\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD': # Проверка на архив
            self.Unpack_typ_1(f)
        else:
            self.Unpack_typ_2(f)

    def Unpack_typ_1(self,f):
        f.seek(4)
        col_f = struct.unpack("<I",f.read(4))[0] # Количество файлов
        f.seek(16)

        for i in range(col_f):
            filename = f.read(100) # Имя файла
            filename = filename.split(b"\x00")[0].decode("cp1251").replace("\\\\","\\")
            format = filename.split(".")[-1].lower()
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size = struct.unpack("<I",f.read(4))[0]   # Размер
            self.data.append((filename,offset,size,format))
        self.file = f

    def Unpack_typ_2(self,f):
        f.seek(4)
        size_f = struct.unpack("<H",f.read(2))[0] # Количество файлов
        f.seek(0,2) # Переход на конец файла
        end_f = f.tell()
        table_offset = end_f-(39*size_f) # Расчёт места начала таблицы
        f.seek(table_offset)

        for i in range(size_f):
            filename = f.read(31).split(b"\x00")[0].decode("cp1251").replace("\\\\","\\")# Имя файла
            table = str.maketrans("", "", "|:;") # Не допустимые символы
            filename = filename.translate(table) # Удаляет не допустимые символы из текста pth
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            posf0 = f.tell()
            f.seek(offset)
            check1 = f.read(4) # pic Проверочные данные
            check2 = f.read(4) # wav
            f.read(4)
            check3 = f.read(4) # wav
            f.seek(offset)
            check4 = f.read(2) #  Анимация версия 2 ?
        
            if check1 == b'\x28\x00\x00\x00' and check3 == b'\x01\x00\x08\x00': # Картинки bmp без заголовка
                format = filename.split(".")[-1].lower()
                if format != "bmp": # Добавляет bmp в конец имени если нет его
                    filename += ".bmp"
                
            elif check2 == b'\x22\x56\x00\x00': # Звук частота его
                filename += ".wav"
            
            elif check4 == b'\x41\x4E': # Анимация версия 2 ?
                filename += ".AN"
        
            f.seek(posf0)
            format = filename.split(".")[-1].lower()
            size = struct.unpack("<I",f.read(4))[0] # Размер 
            self.data.append((filename,offset,size,format))
        self.file = f
        
    def Unpack_PNG(self, f):
        image = Image.open(f)
        self.images = [image]
        
    def Unpack_BMP(self, f):
        fd = f.read(2)
        if fd == b'\x42\x4D':
            image = Image.open(f)
            self.images = [image]
        else:
            f.seek(0)
            fd = f.read()
            f2 = io.BytesIO()
            f2.write(b'\x42\x4D\xD6\x2C\x00\x00\x00\x00\x00\x00\x36\x04\x00\x00')
            f2.write(fd)
            image = Image.open(f2)
            self.images = [image]

    def Unpack_WAV(self, f):
        f.read(2) # Непонятно
        mono_stereo = struct.unpack("<H",f.read(2))[0] # Моно стерио
        Frequency = struct.unpack("<I",f.read(4))[0]   # Частота
        f.read(4) # Внекоторых архивах частота выдаваемого звука
        f.read(6) # Непонятно
        
        fd = f.read()
        size = f.tell()-18
        
        wav = b""
        wav += b"RIFF"
        wav += struct.pack("<I", size+44-8)# chunkSize размер файла-8
        wav += b"WAVE" # format WAVE
        wav += b"fmt " # subchunk1Id fmt 0x666d7420
            
        subchunk1Size = 16
        audioFormat = 1
        numChannels = mono_stereo
        sampleRate = 22050
        byteRate = 44100
        blockAlign = 2
        bitsPerSample = 16

        wav += struct.pack("<IHHIIHH", subchunk1Size, audioFormat, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample)
        wav += b"data"
        wav += struct.pack("<I", size)
        wav += fd # Данные
        f2 = io.BytesIO(wav)

        self.sound = f2