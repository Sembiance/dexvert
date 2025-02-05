#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Golden Palace. В поисках золотого жука(Арчи Баррел. Дело №2. Казино Golden Palace)

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Golden Palace. В поисках золотого жука" 
FORMATS_ARCHIVE = ['dat', 'sd', 'ss', 'ira', 'res', 'cfg', 'ini', 'msk'] 
TYPES_ARCHIVE = [('Golden Palace. В поисках золотого жука', ('*.dat', '*.sd', '*.ss', '*.ira', '*.res', '*.cfg', '*.ini', '*.msk'))]
GAMES = ["Golden Palace. В поисках золотого жука"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app
        self.sup_formats = ["loc",
                            "pic",
                            "res",
                            "anm",
                            "ogg",
                            "wav",
                            "cfg",
                            "ini",
                            "msk"]

        self.sup_types = {"loc":1,
                          "pic":1,
                          "res":1,
                          "anm":2,
                          "ogg":3,
                          "wav":3,
                          "cfg":4,
                          "ini":4,
                          "msk":1}
        self.images = [] 
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format in ["dat", "sd", "ss", "ira", "cfg", "ini", "msk"]:
            self.OpenArchiveDAT(file)
        elif format == "res":
            self.OpenArchiveRES(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "anm":
            self.Unpack_ANM(io.BytesIO(self.file.read(size)))
        elif format == "wav" or format == "ogg":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))
        elif format == "loc":
            self.Unpack_LOC(io.BytesIO(self.file.read(size)))
        elif format == "pic":
            self.Unpack_PIC(io.BytesIO(self.file.read(size)))
        elif format == "res":
            self.Unpack_RES(io.BytesIO(self.file.read(size)))
        elif format == "cfg" or format == "ini":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))
        elif format == "msk":
            self.Unpack_MSK(io.BytesIO(self.file.read(size)))

    def OpenArchiveDAT(self,file):
        f = open(file,"rb")

        check = f.read(4) # Проверочные данные
        f.seek(0, 2) # Проверка
        end_f = f.tell()
        posf0 = end_f-18
        f.seek(posf0)
        ta = f.read(18)
        f.seek(0)

        (dirname, filename) = os.path.split(file)
        format = filename.split(".")[-1].lower()

        if format in ["cfg", "ini"]: # Просто текст
            self.data.append((filename,0,end_f, format))

        elif format == "msk": # Картинки маски
            self.data.append((filename,0,end_f, format))

        elif check == b'\x4f\x67\x67\x53': # Проверка на ogg в некоторых файлах dat есть звук
            #print("OGG звук",file)
            ss = 0
            f.seek(-4,2)
            size_f = struct.unpack("<I",f.read(4))[0] # Количество файлов
            size_offset = size_f*8+4 # Получаем длину оффсета в конце файла,+4 это количество файлов
            f.seek(-size_offset,2) # Переходим к началу таблицы оффсетов в конце файла
            for i in range(size_f):
                ss += 1
                offset, size = struct.unpack("<II",f.read(8))
                self.data.append((str(ss)+".ogg",offset,size,"ogg"))

        elif check == b'\x52\x49\x46\x46':
            #print("Wav звук",file)
            self.data.append(("1.wav",0,end_f,"wav"))

        elif ta == b'\x54\x52\x55\x45\x56\x49\x53\x49\x4f\x4e\x2d\x58\x46\x49\x4c\x45\x2e\x00':
            #print("Картинка без жатия",file) # В некоторых файлах dat есть картинки, первые 4 байта 00 00 02 00
            self.data.append(("1.loc",0,end_f,"loc"))

        elif file[-3:] == 'ira': # В формате ira бывают не сжатые картинки, первые 4 байта 00 00 02 00
            #print("Сжатые картинкa",file)
            self.data.append(("1.pic",0,end_f,"pic")) # Сжатые картинкa

        elif check == b'\x00\x00\x02\x00': # Анимация
            #print("Анимация",file)
            self.data.append(("1.anm",0,end_f,"anm"))

        elif check == b'\x00\x00\x01\xBA': # Файл .dat с видео
            #print("Видео",file)
            self.data.append(("1.dat",0,end_f,"dat"))

        else: 
            print("Непонятно",file)
        self.file = f

    def OpenArchiveRES(self,file):
        f = open(file,"rb")
        f.seek(0, 2)
        end_f = f.tell()
        self.data.append(("1.res",0,end_f,"res"))
        self.file = f

    def Unpack_RES(self, f):
        w = 800
        h = 170
        self.images.append(Image.frombuffer('RGBA', (w,h), f.read(w*h*4), 'raw', 'BGRA', 0, 1))

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_LOC(self,f):
        f.seek(12)
        w, h = struct.unpack("<HH",f.read(4)) # Ширина и высота
        f.read(2)
        self.images.append(Image.frombuffer('RGB', (w,h), f.read(w*h*4), 'raw', 'BGRX', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)) # Переворот картинки

    def Unpack_PIC(self,f):
        f.seek(0, 2)
        size = f.tell()
        size = (size-18)//6
        f.seek(12) 
        w, h = struct.unpack("<HH",f.read(4))
        f.read(2)

        f2 = io.BytesIO()
        for i in range(size):
            f2.write(f.read(4)*struct.unpack("<H",f.read(2))[0])
            # 4 байта цвета 2 байта сколько раз повторить
        f2.seek(0)
        self.images.append(Image.frombuffer('RGBA', (w,h), f2.read(w*h*4), 'raw', 'BGRA', 0, 1))
        f2.close()

    def Unpack_ANM(self,f):
        data = [] # Оффсеты кадров
        f.seek(12) # Перейти на начало ширины
        w,h = struct.unpack("<HH",f.read(4)) # ширина и высота
        size = (w*h)*4 # Получаем размер распакованной картинки
        f.read(2)
        col_f = struct.unpack("<H",f.read(2))[0] # Сколько файлов
        #print("Количество картинок",col_f)
        offset_tab = col_f*4 # Количество файлов умножаем на 4 байта для расчёта нахожденние таблицы в конце
        f.seek(-offset_tab,2) # Переходин на конец файла
        for i in range(col_f):# Чтение таблицы оффсетов в конце файлов
            offset = struct.unpack("<I",f.read(4))[0] + 22
            data.append(offset)

        for i in data:
            f2 = io.BytesIO()
            f.seek(i) # Оффсет файлов распаковки
            while True: 
                f2.write(f.read(4)*struct.unpack("<H",f.read(2))[0])
                # 4 байта цвета 2 байта сколько раз повторить

                if f2.tell() == size: # Если размер равен распакованной картинки то конец
                    f2.seek(0)
                    self.images.append(Image.frombuffer('RGBA', (w,h), f2.read(w*h*4), 'raw', 'BGRA', 0, 1))
                    f2.close()
                    break

    def Unpack_TXT(self,f):
        self.text = f.read().decode("cp1251")

    def Unpack_MSK(self,f):
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)

        if end_f == 96000:
            w = 1600
            h = 480

        elif end_f == 90000:
            w = 1600
            h = 450

        elif end_f == 81000:
            w = 1440
            h = 450

        elif end_f == 60000:
            w = 800
            h = 600

        elif end_f == 45000:
            w = 800
            h = 450

        elif end_f == 451:
            f.read(1) # 1 байт ширина картинки
            w = 80
            h = 45

        elif end_f == 406:
            f.read(1) # 1 байт ширина картинки
            w = 72
            h = 45

        elif end_f == 226:
            f.read(1) # 1 байт ширина картинки
            w = 40
            h = 45

        else:
            print("Неизвестный файл размер",end_f)
            f.close()
            return(0) # Остановка

        self.images.append(Image.frombuffer('1', (w,h), f.read(w*h//8), 'raw', '1', 0, 1))
