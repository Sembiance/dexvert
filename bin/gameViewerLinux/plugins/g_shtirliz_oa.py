#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Штырлитц: Открытие Америки

import os, sys
import struct
import pygame
import io
from PIL import Image, ImageTk
import numpy as np
import array
import copy # Нужно для копирования переменной w

NAME = "Штырлитц: Открытие Америки"
FORMATS_ARCHIVE = ['res']
TYPES_ARCHIVE = [('Штырлитц: Открытие Америки', ('*.res', 'MP.DLL'))]
GAMES = ["Штырлитц: Открытие Америки"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["tex",
                            "pic",
                            "wav"]
        self.sup_types = {"tex":1,
                          "pic":1,
                          "wav":3}
        self.images = []
        self.sound = None

    def open_data(self,file):
        (dirname, filename) = os.path.split(file)
        format = file.split(".")[-1].lower()
        if filename.lower() == "sounds.res": # Преобразование имени к нижнему регистру
            self.OpenArchiveSOUNDS_RES(file)

        elif format == "res":
            self.OpenArchiveRES(file)

        #elif filename.lower() == "mp.dll":
        elif filename.lower() in ["mp.dll", "playavi_.dll", "protect.dll"]:
            self.OpenArchiveDLL(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "tex":
            self.ConvertTEX(io.BytesIO(self.file.read(size)))

        elif format == "wav":
            self.ConvertWAV(io.BytesIO(self.file.read(size)),data_res[4])

        elif format == "pic":
            self.ConvertPIC(io.BytesIO(self.file.read(size)))

    def OpenArchiveRES(self,file):
        self.data = [] # Список файлов

        f = open(file,"rb")
        col = struct.unpack("<I", f.read(4))[0] // 64
        f.seek(0)

        for i in range(col):
            offset, size = struct.unpack("<II", f.read(8)) # Оффсет размер
            f.read(6) # Нули
            pth = f.read(50).split(b"\x00")[0].decode("cp1251") # Путь
            format = pth.split(".")[-1].lower()
            if size > 0:
                self.data.append((pth,offset,size,format,44100))
        self.file = f
        
    def OpenArchiveDLL(self,file):
        self.data = [] # Список файлов

        f = open(file,"rb")
        f.seek(0,2)
        end_f = f.tell() # Конец файла

        if end_f == 339968: # Белое солнце пустыни и остальные. mp.dll
            offset = 321424
            col = 18 # Количество картинок

        elif end_f == 328704: # Вовочка и Петечка, Операция Пластилин(Agent Hlina (cz)) playavi_.dll
            offset = 317972
            col = 7 # Количество картинок

        elif end_f == 976583: # Штырлец 3  protect.dll
            offset = 282040
            col = 1 # Количество картинок

        else:
            print("Ошибка неизвестная библиотека")
            return(0) # Остановка скрипта

        f.seek(offset) # Начало картинок
        for i in range(col):
            offset = f.tell() # Начало картинки
            unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно
            if unclear_1 != 40:
                offset = f.tell()
                unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно всегда 28 00 00 00

            w, h = struct.unpack("<LL",f.read(8)) # Ширина и высота

            f.read(2) # Непонятно
            tip = struct.unpack("<H",f.read(2))[0] # Формат картинки 4 бита
            f.read(24)# Непонятно

            # Выравневание картинки к 8
            whole, rest = divmod(w,8) # Делит правельно сначало идёт целое число потом остаток
            if rest != 0:
                w += (8-rest) # Прибавляем чтоб правельно отбразить кратинку

            if h == 64 and tip == 4: # Исправляем последнию картинку
                h = 40

            if tip == 1: # 1 бит
                f.read(8) # Пропускаем палитру
                f.read((w*h)//8) # Картинка

            elif tip == 4: # 4 бита
                f.read(64) # Пропускаем палитру
                f.read(w*h//2) # Картинка

            size = f.tell()-offset # Размер картинки
            self.data.append((str(offset)+".pic",offset,size,"pic"))
        self.file = f

    def OpenArchiveSOUNDS_RES(self,file):
        self.data = [] # Список файлов

        f = open(file,"rb")
        data2 = set() # Множество
        for i in range(5000):
            offset = struct.unpack("<I",f.read(4))[0]+40000 # Оффсет 
            size = struct.unpack("<I",f.read(4))[0] # Размер
            if size != 4294967295:
                data2.add((offset,size)) # Добавляем в множество

        data = list(data2) # Удаляет одинаковые оффсеты и размеры
        data = sorted(data) # Сортировка по первому значению

        for i in data:
            if i[1] <= 1832830: # Всё что ниже с частотой 22050
                frequency = 22050
            else:
                frequency = 44100
            self.data.append((str(i[0])+".wav",i[0],i[1],"wav",frequency))
        self.file = f

    def ConvertWAV(self, f, frequency):
        data = f.read()
        size = len(data)
        wav = b""
        try:
            wav += b"RIFF"
            wav += struct.pack("<I", size+44-8) # chunkSize размер файла-8
            wav += b"WAVE" # format WAVE
            wav += b"fmt " # subchunk1Id fmt 0x666d7420

            subchunk1Size = 16
            audioFormat = 1
            numChannels = 1
            sampleRate = frequency
            byteRate = 44100
            blockAlign = 2
            bitsPerSample = 16

            wav += struct.pack("<IHHIIHH", subchunk1Size, audioFormat, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample)
            wav += b"data"
            wav += struct.pack("<I", size)
            wav += data # Данные
        finally:
            self.sound = io.BytesIO(wav)

    def ConvertTEX(self,f):
        def Color3(p):
            # Третья формула RGBA4444
            b = ((p & 15)<<4)
            g = (((p >> 4)& 15))<<4 
            r = (((p >> 8)& 15))<<4
            a = (((p >> 12)& 15))<<4
            return (r,g,b,a)

        f.seek(0,2)
        posf0 = f.tell()
        f.seek(0)
        w,h = struct.unpack("<II",f.read(8))
        tip = struct.unpack("<I",f.read(4))[0]

        if tip == 2:
            f.seek(30)
            sizeff = w*h*3+30
            if sizeff == posf0:
                self.images.append(Image.frombuffer('RGB', (w,h), f.read(w*h*3), 'raw', 'BGR', 0, 1))
            else:
                self.images.append(Image.frombuffer('RGBA', (w,h), f.read(w*h*4), 'raw', 'BGRA', 0, 1))

        elif tip == 23:
            self.images.append(Image.frombuffer('RGB', (w,h), f.read(w*h*2), 'raw', 'BGR;16', 0, 1))

        elif tip == 25:
            self.images.append(Image.frombuffer('RGBA', (w,h), f.read(w*h*2), 'raw', 'BGRA;15', 0, 1))

        elif tip == 26:
            rgb = []
            rgb = np.frombuffer(f.read(w*h*2), dtype=np.uint16)
            rgb = np.array(rgb, np.uint16).reshape(h, w)
            r,g,b,a = Color3(rgb)
            rgb = np.dstack((r,g,b,a))
            rgb = np.uint8(rgb)
            self.images.append(Image.fromarray(rgb,"RGBA"))

        else:
            raise("Непонятный тип: {}".format(tip))

    def ConvertPIC(self,f):
        unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно всегда 28 00 00 00
        w, h = struct.unpack("<LL",f.read(8)) # Ширина и высота

        unclear_2 = struct.unpack("<H",f.read(2))[0] # Непонятно
        tip = struct.unpack("<H",f.read(2))[0] # Формат картинки 4 бита
        unclear_3 = struct.unpack("<I",f.read(4))[0] # Непонятно
        unclear_4 = struct.unpack("<I",f.read(4))[0] # Непонятно
        unclear_5 = struct.unpack("<I",f.read(4))[0] # Непонятно
        unclear_6 = struct.unpack("<I",f.read(4))[0] # Непонятно
        unclear_7 = struct.unpack("<I",f.read(4))[0] # Непонятно
        unclear_8 = struct.unpack("<I",f.read(4))[0] # Непонятно

        ww = copy.deepcopy(w) # Поная копиия переменной w, Нужно для правельного обрезания картинки

        # Выравневание картинки к 8
        whole, rest = divmod(w,8) # Делит правельно сначало идёт целое число потом остаток
        if rest != 0:
            w += (8-rest) # Прибавляем чтоб правельно отбразить кратинку

        if h == 64 and tip == 4: # Исправляем последнию картинку
            h = 40

        if tip == 1: # 1 бит
            Pal = b"" # Палитра
            for i in range(2):
                B = f.read(1)
                G = f.read(1)
                R = f.read(1)
                A = f.read(1)
                Pal += R+G+B

            f_image = Image.frombuffer('1', (w,h), f.read((w*h)//8), 'raw', '1', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)

        elif tip == 4: # 4 бита
            Pal = b'' # Палитра
            for i in range(16):
                B = f.read(1)
                G = f.read(1)
                R = f.read(1)
                A = f.read(1)
                Pal += R+G+B

            f_image = Image.frombuffer('P', (w,h), f.read(w*h//2), 'raw', 'P;4', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
            f_image.putpalette(Pal)

        else:
            print("Ошибка непонятный формат картинки",tip)

        f_image = f_image.crop([0, 0, ww, h]) # Вырезаем картинку, чтобы неотображались лишние пиксели для выравневания.
        self.images.append(f_image)