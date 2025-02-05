#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# 12 стульев как это было на самом деле

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "12 стульев как это было на самом деле" 
FORMATS_ARCHIVE = [".SID"]
TYPES_ARCHIVE = [('12 стульев', ("*.SID"))]
GAMES = ["12 стульев как это было на самом деле"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["pack_jpg",
                            "pack_bmp",
                            "pack_wav",
                            "txt"]

        self.sup_types = {"pack_jpg":2,
                          "pack_bmp":2,
                          "pack_wav":3,
                          "txt":4}
        self.images = []  
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "sid":
            self.OpenArchiveSID(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "pack_jpg":
            self.Unpack_pack_jpg(io.BytesIO(self.file.read(size)))
        elif format == "pack_bmp":
            self.Unpack_pack_bmp(io.BytesIO(self.file.read(size)))
        elif format == "pack_wav":
            self.Unpack_pack_wav(io.BytesIO(self.file.read(size)))
        elif format == "txt":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))

    def OpenArchiveSID(self,file):
        self.data = []

        data = [] # Оффсет и размер
        f = open(file,"rb")
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов

        for i in range(col):
            read_byte = struct.unpack("<H",f.read(2))[0] # Сколько прочетать байт дальше
            fd1 = f.read(read_byte)
            read_byte = struct.unpack("<H",f.read(2))[0] # Сколько прочетать байт дальше
            fd2 = f.read(read_byte)
            size = struct.unpack("<I",f.read(4))[0] # Размер
            unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно
            data.append((offset,size))

        plus_offset = f.tell() # Позиция после таблицы

        for i in data:
            f.seek(i[0]+plus_offset+146) # jpg
            type1 = f.read(4)

            f.seek(i[0]+plus_offset+11)
            type2 = f.read(21)

            f.seek(i[0]+plus_offset+8)
            type3 = f.read(4)

            if type1 == b'\xFF\xD8\xFF\xE0': # jpg
                format = "pack_jpg"

            elif type2 == b'DELPHIXWAVECOLLECTION': # Wav
                format = "pack_wav"

            elif type2 == b'DELPHIXPICTURECOLLECT': # bmp 
                format = "pack_bmp"

            elif type3 == b'\xFF\xD8\xFF\xE0': # jpg PIL не открывает эти картинки, пропустить первые 8 байт, и пропустить последний байт в файле
                format = "jpg1"

            else:
                format = "txt"
            self.data.append((str(i[0]+plus_offset)+"."+format,i[0]+plus_offset,i[1],format))
        self.file = f

    def Unpack_TXT(self, f):
        self.text = f.read().decode("cp1251")

    def Unpack_pack_jpg(self, f):
        dataf = f.read()
        offset = 0 # Оффсет поиска

        while True:
            offset = self.Search_jpg(b'\xFF\xD8\xFF\xE0',dataf,offset) # Поиск заголовка
            f.seek(offset+4+2)
            check = f.read(4) # Проверка
            if check == b'JFIF': # Это точно картинка
                offset_jpg = offset
                offset = self.Search_jpg(b'\x0CSystemMemory',dataf,offset) # Поиск после файла строчки
                size = offset-offset_jpg # Получаем размер файла

                f.seek(offset_jpg)
                fd = f.read(size)

                f2 = io.BytesIO(fd) # Открываем картинку и копирвуем её
                image = Image.open(f2)
                self.images.append(image.copy())
                f2.close()

            elif offset == -1: # Конец поиска
                break

    def Search_jpg(self,search,dataf,offset):
        offset = dataf.find(search,offset)
        return (offset)

    def Unpack_pack_bmp(self, f):
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(27)
        while True:
            if f.tell() == end_f-49: # Конец файла
                break
            f.read(116) # Пропустить
            posf = f.tell()
            type = f.read(2)
            if type != b'BM': # Проверка на BM
                #print("ЭТО НЕ BM",type)
                break
            size = struct.unpack("<I",f.read(4))[0] # Размер
            f.seek(posf)
            fd = f.read(size)

            f2 = io.BytesIO(fd) # Открываем картинку и копирвуем её
            image = Image.open(f2)
            self.images.append(image.copy())

    def Unpack_pack_wav(self, f):
        f2 = io.BytesIO()
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(84)
        while True:
            if f.tell() == end_f: # Конец файла
                break
            f.read(33) # Пропустить
            posf = f.tell()
            type = f.read(4)
            if type != b'RIFF': # Проверка на звук
                #print("ЭТО НЕ звук WAV",type)
                break
            size = struct.unpack("<I",f.read(4))[0]+8 # Размер
            f.seek(posf)
            fd = f.read(size)

            f3 = io.BytesIO(fd)

            f3.seek(36)
            type = f3.read(4) # Тип архива
            if type != b'data': # Проверка на архив
                f3.seek(42)

            size = struct.unpack("<I",f3.read(4))[0] # Размер
            fd = f3.read(size)
            f2.write(fd)
            f3.close()

        f2.seek(0)
        fd = f2.read()
        size = f2.tell()
        f2.close()

        wav = b""
        wav += b"RIFF"
        wav += struct.pack("<I", size+44-8)# chunkSize размер файла-8
        wav += b"WAVE" # format WAVE
        wav += b"fmt " # subchunk1Id fmt 0x666d7420    
        subchunk1Size = 16 
        audioFormat = 1 
        numChannels = 1    # Количество каналов
        sampleRate = 44100 # Частота файла
        byteRate = 44100   # Частота выхода звука, для расчёта длины звучания
        blockAlign = 2
        bitsPerSample = 16 # Битность звука
        wav += struct.pack("<IHHIIHH", subchunk1Size, audioFormat, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample)
        wav += b"data"
        wav += struct.pack("<I", size)
        wav += fd # Данные

        f4 = io.BytesIO(wav)
        self.sound = f4
