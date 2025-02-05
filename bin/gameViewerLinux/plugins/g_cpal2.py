#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Pohádka o Mrazíkovi, Ivanovi a Nastěnce(Морозко: Приключение деда Мороза, Ивана и Насти)

import os, sys, io, struct
from PIL import Image
import zlib

NAME = "Морозко: Приключение деда Мороза, Ивана и Насти"
FORMATS_ARCHIVE = ['res']
TYPES_ARCHIVE = [('Морозко', ('*.res'))]
GAMES = ["Морозко: Приключение деда Мороза, Ивана и Насти"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        
        self.sup_formats = ["wav",
                            "gfx",
                            "txf"]

        self.sup_types = {"wav":3,
                          "gfx":2,
                          "txf":4}
        self.images = []
        self.sound = None
        self.text = None

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
        if format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))
        elif format == "gfx":
            self.Unpack_GFX(io.BytesIO(self.file.read(size)))
        elif format == "txf":
            self.Unpack_TXF(io.BytesIO(self.file.read(size)))

    def OpenArchiveRES(self,file):
        self.data = []
        f = open(file,"rb")

        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)
        type = f.read(44) # Тип архива
        if type != b'Centauri Production Resource File 2.01\n\n\x00\x00\x00\x00': # Проверка на архив
            print("ЭТО НЕ АРХИВ",type)
            raise Exception("Это не архив!")

        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        unclear = f.read(4) # Непонятно Хеш файла ?

        offset_tab = end_f-(col*92) # Расчёт начало таблицы файлов
        f.seek(offset_tab) # Переход на начало таблицы
        for i in range(col):
            filename = f.read(64).split(b"\x00")[0].decode("utf8").replace("\\\\","\\") # Имя файла
            f.read(12) # Непонятно
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size = struct.unpack("<I",f.read(4))[0] # Размер файла
            size_2 = struct.unpack("<I",f.read(4))[0] # Размер файла
            f.read(4) # Непонятно Хеш файла ?
            format = filename.split(".")[-1].lower()
            self.data.append((filename,offset,size,format))
        self.file = f

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_GFX(self, f): 
        data = [] # Список файлов
        type = f.read(16)
        if type != b'CP gfxdata 2.2\n\n':
            print("ЭТО НЕ анимация",type)
            raise Exception("Это не архив!")

        unclear = struct.unpack("<I",f.read(4))[0] # Непонятно
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        unclear = struct.unpack("<I",f.read(4))[0] # Непонятно

        for i in range(col):
            unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно
            size = struct.unpack("<I",f.read(4))[0]-(1+4+4) # Размер файла
            # -1 сделано чтоб начать с байта распаковки, Байты в конце файла -4 -4 первые непонятно, второй размер распакованно файла.
            unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно Читаются скорей по 2 байта
            offset = struct.unpack("<I",f.read(4))[0]+1 # Оффсет +1 сделано чтоб начать с байта распаковки и пропустить байт 0
            f.read(6) # Непонятно Читаются скорей по 2 байта
            w = struct.unpack("<I",f.read(4))[0] # Ширина картинки
            h = struct.unpack("<I",f.read(4))[0] # Высота
            unclear_3 = struct.unpack("<H",f.read(2))[0] # Непонятно
            tip = struct.unpack("<H",f.read(2))[0] # Тип картинки  8(8), 10(16), 18(24), 20(32)
            unclear = struct.unpack("<I",f.read(4))[0] # Непонятно
            size_decom = struct.unpack("<I",f.read(4))[0] # Размер распакованного файла
            unclear = struct.unpack("<I",f.read(4))[0] # Непонятно
            unclear = struct.unpack("<I",f.read(4))[0] # Непонятно
            f.read(16) # Непонятно
            f.read(4) # Непонятно FF FF FF FF
            f.read(8) # Непонятно
            data.append((offset,size,w,h,tip,size_decom))

        for i in data:
            f.seek(i[0])
            fd = f.read(i[1])
            decompress = zlib.decompressobj(zlib.MAX_WBITS) # Распаковка потока без crc
            fd = decompress.decompress(b'\x78\xda'+fd)

            # Конвертация картинок
            offset = i[0]
            w = i[2]
            h = i[3]
            size_decom = i[5]
            tip = i[4] # Тип
            if int(i[4]) == 8:
                f.read(8) # Непонятно
                Pal = b''
                for i in range(256): # Читаем палитру и переделаваем её
                    b = f.read(1)
                    g = f.read(1)
                    r = f.read(1)
                    f.read(1)
                    Pal += r+g+b

            f2 = io.BytesIO(fd)
            if tip == 8: # Картинки без палитры
                #print("Тип",tip)
                # 1,2,3 лишних байта после ширины w картинки
                if w*h+h == size_decom or w*h+(h*2) == size_decom or w*h+(h*3) == size_decom: 
                    if w*h+h == size_decom:       # 1 лишних байта
                        excess_bytes = 1

                    elif w*h+(h*2) == size_decom: # 2 лишних байта
                        excess_bytes = 2

                    elif w*h+(h*3) == size_decom: # 3 лишних байта
                        excess_bytes = 3

                    f3 = io.BytesIO() # Записываем правельные строчки картинки
                    for i in range(h):
                        fd2 = f2.read(w) # Читаем строчку картинки
                        f3.write(fd2)
                        f2.read(excess_bytes) # Лишний байт

                    f3.seek(0)
                    f_image = Image.frombuffer('P', (w,h), f3.read(w*h), 'raw', 'P', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
                    f_image.putpalette(Pal)
                    
                    self.images.append(f_image)
                    f3.close()
                    f2.close()

                else:
                    f_image = Image.frombuffer('P', (w,h), f2.read(w*h), 'raw', 'P', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
                    f_image.putpalette(Pal)
                    self.images.append(f_image)
                    f2.close()

            elif tip == 16: # Два байта на цвет
                #print("Тип",tip)
                if (w+1)*h*2 == size_decom: # Прибавить к ширине картинки +1
                    w += 1

                f_image = Image.frombuffer('RGB', (w,h), f2.read(w*h*2), 'raw', 'BGR;15', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
                self.images.append(f_image)
                f2.close()

            elif tip == 24: # Три байта на цвет
                # 1 или 2 лишних байта после ширины w картинки
                if (w*h*3)+h == size_decom or (w*h*3)+(h*2) == size_decom:
                    if (w*h*3)+h == size_decom:
                        excess_bytes = 1 # Лишний байт

                    elif (w*h*3)+(h*2) == size_decom: # 2 байта лишний после ширины w картинки
                        excess_bytes = 2

                    f3 = io.BytesIO() # Записываем правельные строчки картинки
                    for i in range(h):
                        fd2 = f2.read(w*3) # Читаем строчку картинки
                        f3.write(fd2)
                        f2.read(excess_bytes) # Лишний байт

                    f3.seek(0)
                    f_image = Image.frombuffer('RGB', (w,h), f3.read(w*h*3), 'raw', 'BGR', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
                    self.images.append(f_image)
                    f3.close()

                else: 
                    if ((w+1)*h)*3 == size_decom: # Значит в ширину больше на 1 пиксель
                        w += 1 # Прибавить к ширине картинки +1

                    f_image = Image.frombuffer('RGB', (w,h), f2.read(w*h*3), 'raw', 'BGR', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
                    self.images.append(f_image)

            elif tip == 32: # Четыре байта на цвет b,g,r,a
                #print("Тип",tip)
                f_image = Image.frombuffer('RGBA', (w,h), f2.read(w*h*4), 'raw', 'BGRA', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
                self.images.append(f_image)

            else:
                print("НЕ ПРАВЕЛЬНО", w, h, size_decom)
            f2.close()
            
    def Unpack_TXF(self, f): 
        data = [] # Список файлов
        type = f.read(16) # Тип архива
        if type != b'CP textfile 2.1\n': # Проверка
            print("ЭТО НЕ ТЕКСТ",type)
            return(0) # Остановка скрипта

        unclear = struct.unpack("<I",f.read(4))[0] # Непонятно
        col = struct.unpack("<I",f.read(4))[0] # Количество строчек текста
        add_offset = 24+(col*8) # Прибавить к оффсету текста

        for i in range(col):
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет на начало блока текста
            unclear = struct.unpack("<I",f.read(4))[0] # Непонятно
            if offset != 0:
                data.append((offset+add_offset,unclear))
                #print(offset+add_offset,unclear)

        for i in data:
            f.seek(i[0])
            size = struct.unpack("<I",f.read(4))[0] # Размер блока текста

            f.seek(i[0])
            fd = f.read(size)

            f2 = io.BytesIO(fd)
            size = struct.unpack("<I",f2.read(4))[0] # Размер блока текста
            name_sound = f2.read(128).split(b"\x00")[0].decode("utf8").replace("\\\\","\\") # Имя звукового файла
            if name_sound != "": # Если неравно значит тут есть имя звукового файла
                #print(name_sound)
                self.text.append(name_sound+"\n")

            unclear = struct.unpack("<I",f2.read(4))[0] # Непонятно записанно всегда 1 проверил
            f2.read(128) # 128 байт 00 нулей нечего вних нет проверил

            f_path = b'' # Читаем имя файла до байта 00
            while True:
                bait = f2.read(1) # Байт строчки
                if bait == b'\x00':
                    f_path = f_path.decode("cp1251") # Переделаваем байты в строчку
                    #print(f_path)
                    break
                f_path += bait # Прибавляем байт

            self.text.append(f_path+"\n")
            f2.close()
        f.close()