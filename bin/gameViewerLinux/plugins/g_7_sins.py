#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# 7 Sins

import os, sys
import struct
import pygame
import io
from PIL import Image, ImageTk
import numpy as np
import array

NAME = "7 Sins"
FORMATS_ARCHIVE = ['pak','rws']
TYPES_ARCHIVE = [('7 Sins', ('*.pak', '*.rws'))]
GAMES = ["7 Sins"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["wav",
                            "png",
                            "bmp",
                            "eng",
                            "cin",
                            "fx",
                            "ini",
                            "met",
                            "txt",
                            "res"]
        self.sup_types = {"wav":3,
                          "png":1,
                          "bmp":1,
                          "eng":4,
                          "cin":4,
                          "fx":4,
                          "ini":4,
                          "met":4,
                          "txt":4,
                          "res":4}
        self.images = []
        self.sound = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        (dirname, filename) = os.path.split(file)
        if format == "pak":
            self.OpenArchivePAK(file)
        elif format == "rws":
            self.OpenArchiveRWS(file,filename)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "wav":
            self.ConvertWAV(io.BytesIO(self.file.read(size)))
        elif format == "png" or format == "bmp":
            self.Unpack_PNG(io.BytesIO(self.file.read(size)))
        elif format in ["cin", "fx","ini","met", "txt", "res"]:
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))
        elif format == "eng":
            self.Unpack_TXT2(io.BytesIO(self.file.read(size)))

    def OpenArchivePAK(self,file):
        self.data = [] # Список файлов
        f = open(file,"rb")
        type = f.read(4) # Тип архива
        if type != b'PACK': # Проверка на архив
            print("ЭТО НЕ АРХИВ",type)
            return(0) # Остановка скрипта
        offset_tab = struct.unpack("<I",f.read(4))[0] # Оффсет таблицы
        size_tab = struct.unpack("<I",f.read(4))[0] # Размер таблицы
        col = size_tab // 80 # Количество файлов
        f.seek(offset_tab)
        for i in range(col):
            f_path = f.read(72).split(b"\x00")[0].decode("utf8") # Имя файла
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size = struct.unpack("<I",f.read(4))[0] # Размер
            if f_path != "": # Чтоб не прошла пустая строчка
                format = f_path.split(".")[-1].lower()
                self.data.append((f_path,offset,size,format))
        self.file = f

    def OpenArchiveRWS(self,file,filename):
        f = open(file,"rb")
        f.seek(0,2)
        size = f.tell()
        f.seek(228)
        frequency = struct.unpack("<I",f.read(4))[0] # Частота
        if frequency != 22052:
            pass
        else:
            self.data.append((filename[:-4]+".wav",0,size,"wav"))
        self.file = f

    def ConvertWAV(self, f):
        f.seek(228)
        frequency = struct.unpack("<I",f.read(4))[0] # Частота
        if frequency != 22052:
            print("Ошибка тут нет частоты звука")
        else:
            f.seek(241)
            nchannels = struct.unpack("B",f.read(1))[0] # Количество каналов

            f.seek(2048)
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
                numChannels = nchannels
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

    def Unpack_PNG(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_TXT(self, f): 
        self.text = f.read().decode("charmap")

    def Unpack_TXT2(self, f): 
        self.text = f.read().decode("utf_16")