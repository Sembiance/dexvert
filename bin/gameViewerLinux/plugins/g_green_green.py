#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Green Green Для версии v2.3-4

import os, sys, io, struct
from PIL import Image
import numpy as np
import zlib

NAME = "Green Green" 
FORMATS_ARCHIVE = [".DAT", ".PCG"]
TYPES_ARCHIVE = [('Green Green', ("*.DAT", "*.PCG"))]
GAMES = ["Green Green"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["bmp",
                            "icon",
                            "ogg"]

        self.sup_types = {"bmp":1,
                          "icon":1,
                          "ogg":3}
        self.images = []
        self.sound = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "dat" or format == "pcg":
            self.OpenArchiveDAT(file)

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
        elif format == "ogg":
            self.Unpack_OGG(io.BytesIO(self.file.read(size))) 
        elif format == "icon":
            self.Unpack_ICON(io.BytesIO(self.file.read(size))) 

    def OpenArchiveDAT(self,file):
        f = open(file,"rb")
        type = f.read(4) # Тип
        if type == b'RIFF': # Проверка на архив если RIFF то не архив
            f.seek(56)
            col = struct.unpack("<I",f.read(4))[0] # Количество файлов

            f.seek(84)
            check = struct.unpack("<I",f.read(4))[0] # Проверка
            if check == 1: # Начало чтение картинок
                f.seek(100)

            elif check == 3:
                f.seek(148)

            for i in range(col):
                offset = f.tell()
                f.read(4) # Индефикатор icon
                size = struct.unpack("<I",f.read(4))[0] + 8 # Размер
                f.seek(size-8, 1) # Пропускаем байты
                self.data.append((str(i+1)+".icon",offset,size,"icon"))

        else:
            f.seek(0)
            col = struct.unpack("<I",f.read(4))[0] # Количество файлов
            size_t = struct.unpack("<I",f.read(4))[0] # Размер архива после таблицы файлов

            if file[-3:] == "PCG":
                for i in range(col):
                    filename = f.read(32).split(b"\x00")[0].decode("utf8").replace("\\\\","\\") # Имя файла
                    format = filename.split(".")[-1].lower()
                    size = struct.unpack("<I",f.read(4))[0] # Размер
                    offset = struct.unpack("<I",f.read(4))[0] # Оффсет
                    w,h = struct.unpack("<II",f.read(8)) # Ширина и высота
                    self.data.append((filename,offset,size,format))

            elif file[-3:] == "DAT":
                for i in range(col):
                    filename = f.read(64).split(b"\x00")[0].decode("utf8").replace("\\\\","\\") # Имя файла
                    format = filename.split(".")[-1].lower()
                    size = struct.unpack("<I",f.read(4))[0] # Размер
                    offset = struct.unpack("<I",f.read(4))[0] # Оффсет
                    self.data.append((filename,offset,size,format))
        self.file = f

    def Unpack_OGG(self, f):
        self.sound = f

    def Unpack_BMP(self, f):
        type = f.read(4) # Тип картинки

        if type in [b'NCMP', b'RCB\x00', b'LZ77']:
            # NCMP не сжатая картинка
            # RCB\x00 сжатая картинка
            # LZ77 сжатая картинка
            pass

        else:
            print("ЭТО НЕ КАРТИНКА",type)
            return(0)

        unclear = struct.unpack("<I",f.read(4))[0] # Непонятно сжат не сжат ?
        w,h = struct.unpack("<II",f.read(8)) # Ширина и высота
        size = struct.unpack("<I",f.read(4))[0] # Размер распакованной картинки
        col = struct.unpack("<I",f.read(4))[0]  # Количество повторений сжатых данных

        if type == b'LZ77':
            f2 = io.BytesIO()
            f2.write(f.read(255)) # Это несжатые цвета картинки

            for i in range(col):
                byte_1 = f.read(1)[0] # Оффсет чтения байтов
                byte_2 = f.read(1)[0] # Cколько прочетать байтов
                byte_3 = f.read(1) # Просто записываем этот байт

                offset = (f2.tell()-255) + byte_1 # Позиция чтения байт

                len_byte = f2.tell() - offset # Получаем количество байт доступное с конца файла
                if len_byte >= byte_2: # Если количество байт в конце файла больше чем нужно надо взять, просто читаем нужное число байт сразу
                    # Записываем в выходной файл последовательность байт
                    f2.seek(offset)
                    fd = f2.read(byte_2) # Читаем
                    f2.seek(0,2) # Переходим на конец файла
                    f2.write(fd) # Записываем

                else:
                    for ii in range(offset, offset+byte_2):
                        f2.seek(ii) # Переходим на чтение байта
                        fd = f2.read(1) # Читаем 1 байт
                        f2.seek(0,2) # Переходим на конец файла
                        f2.write(fd) # Записываем

                f2.write(byte_3) # Байт byte_3 всегда записывается

            f2.seek(0)
            self.images.append(Image.frombuffer('RGB', (w,h), f2.read(w*h*3), 'raw', 'BGR', 0, 1))
            f2.close()

        elif col > 0: # Распаковка сжатых данных
            f2 = io.BytesIO(b'\x00' * (w*h*3)) # Заполнене пустыми байтами, ускоряет распаковку
            for i in range(col):
                f2.write(f.read(3)*f.read(1)[0])

            f2.seek(0)
            self.images.append(Image.frombuffer('RGB', (w,h), f2.read(w*h*3), 'raw', 'BGR', 0, 1))
            f2.close()

        else: # Не сжатая картинка
            self.images.append(Image.frombuffer('RGB', (w,h), f.read(w*h*3), 'raw', 'BGR', 0, 1))

        f.close()

    def Unpack_ICON(self, f):
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)

        if end_f == 334: # 2 бит
            Pal = b'\x00\x00\x00\xFF\xFF\xFF\x00\xFF\x00\x00\x80\x0C' # Палитра сдедал сам
            w = 32
            h = 32
            f.seek(74) # Начало картинки

            BIT_1 = []
            BIT_2 = []

            for i in range(16):
                BIT_1 += bin(struct.unpack(">Q",f.read(8))[0])[2:].zfill(64) # Читаем 8 байт получаем строчку бит

            for i in range(16):
                BIT_2 += bin(struct.unpack(">Q",f.read(8))[0])[2:].zfill(64) # Читаем 8 байт Получаем строчку бит

            # Биты стоя в обратном порядке это как отображается в программе Crystal Tile
            list_numbers = [int(BIT_2[bit_number]+(BIT_1[bit_number]), 2) for bit_number in range(1024)] # В обратном порядке

            f_image = Image.frombuffer('P', (32,32), bytes(list_numbers), 'raw', 'P', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
            f_image.putpalette(Pal)

            self.images.append(f_image)

        elif end_f == 774: # 4 бита Нужна правельная палитра.
            Pal = b'\xFF\xFF\xFF\xEE\xEE\xEE\xDD\xDD\xDD\xCC\xCC\xCC\xBB\xBB\xBB\xAA\xAA\xAA\x99\x99\x99\x88\x88\x88\x77\x77\x77\x66\x66\x66\x55\x55\x55\x44\x44\x44\x33\x33\x33\x22\x22\x22\x11\x11\x11\x00\x00\x00' + (b'\x00'*720)

            w = 32
            h = 31
            f.seek(150) # Начало картинки
            f_image = Image.frombuffer('P', (w,h), f.read(w*h//2), 'raw', 'P;4', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
            f_image.putpalette(Pal) # Добавляем палитру в картинку
            self.images.append(f_image)

        elif end_f == 2246: # 8 бит
            fd = b'x\x9c\xed\x8cK\x15\x00!\x0c\xc4\xb0\x80\x05,\xd4B-`\x01\x0b\xb5\x80\x05,`\x01\x0bX\xc0B-\x94\xbcU\xb1\x07r\xeag&\x11\xe1\xee\xe7\x9c\xbd\xf7Zk\xce9\xc6\xe8\xbd\x9bYk\xad\xd6\xaa\xaa"RJ\xc99\xa7\x0f\x06V\x8e\xbc\x08\x10#L\x85"u$\xa8\x10\xa2\x8d\x88\xf4x\xfc\x98\x0b\x9b\xc2/\xd1'

            Pal = zlib.decompress(fd) # Распаковка палитры

            w = 32
            h = 60
            f.seek(198) # Начало картинки

            f_image = Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
            f_image.putpalette(Pal) # Добавляем палитру в картинку
            self.images.append(f_image)

        else:
            print("Ошибка непонятный размер файла",end_f)

        f.close()