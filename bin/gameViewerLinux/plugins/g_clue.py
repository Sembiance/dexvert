#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Clue: Murder at Boddy Mansion (Улика Убийца Бодди Мэншена)

import os, sys, io, struct
from PIL import Image
import zlib

NAME = "Clue: Murder at Boddy Mansion"
FORMATS_ARCHIVE = ['a', 'res']
TYPES_ARCHIVE = [('Clue: Murder at Boddy Mansion', ('*.a', '*.res'))]
GAMES = ["Clue: Murder at Boddy Mansion"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["EIMG"]

        self.sup_types = {"EIMG":1}

        self.images = []
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "a" or format == "res":
            self.OpenArchiveRES(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "EIMG":
            self.Unpack_EIMG(io.BytesIO(self.file.read(size)))

    def OpenArchiveRES(self,file):
        self.data = [] # Список файлов
        f = open(file,"rb")

        type = f.read(4) # Индефикатор
        if type != b'PACK': # Проверка
            print("ЭТО НЕ СЖАТЫЕ ДАННЫЕ",type)
            return(0) # Остановка

        size_comp = struct.unpack("<I",f.read(4))[0] # Размер сжатых данных
        size = struct.unpack("<I",f.read(4))[0] # Размер распакованных данных

        fd = zlib.decompress(f.read(size_comp)) # Распаковка сжатия
        f.close()

        f = io.BytesIO(fd) # Распакованный файл
        type = f.read(4) # Тип архива
        if type != b'DDRV': # Проверка на архив
            print("ЭТО НЕ АРХИВ",type)
            return(0) # Остановка скрипта

        offset_tab = struct.unpack("<I",f.read(4))[0] # Оффсет на таблицу
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        f.seek(offset_tab) # Переходим на таблицу

        for i in range(col):
            zeros = f.read(4) # Записаны всегда нули
            unclear = f.read(8) # Непонятно читаются по 2 байта возможно координаты

            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size = struct.unpack("<I",f.read(4))[0] # Размер
            f_path = f.read(128).split(b"\x00")[0].decode("utf8").replace("\\\\","\\") # Имя файла

            f_pos = f.tell() 
            f.seek(offset)
            type = f.read(4).split(b"\x00")[0].decode("utf8") # Тип файла
            # Есть только два типа файлов .EIMG .ANIM
            f.seek(f_pos) # Возврат к таблице
            self.data.append((str("%03d" %i)+" "+f_path+"."+type, offset, size, type))

        col_2 = struct.unpack("<I",f.read(4))[0] # Количество файлов 2
        self.file = f

    def Unpack_EIMG(self, f):
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)

        type = f.read(4) # Тип
        if type != b'EIMG': # Проверка
            print("ЭТО НЕ сжатая картинка",type)
            return(0) # Остановка скрипта

        flag = f.read(4) # Индефикатор
        size = struct.unpack("<I",f.read(4))[0] # Размер файла дальше

        if flag == b'\x00\x01\x00\x00':
            w, h = struct.unpack("<HH",f.read(4)) # Ширина и высота
            unclear_ = f.read(28) # Непонятно
            check = 0x00 # Байт остановки на конце строчки по ширине картинки

        elif flag == b'\x00\x02\x00\x00':
            unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно похоже читается по 2 байта позиция на экране где дожны быть записаны данные ?
            w, h = struct.unpack("<II",f.read(8)) # Ширина и высота
            unclear_3 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_4 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_5 = f.read(13) # Непонятно
            w_2, h_2 = struct.unpack("<II",f.read(8)) # Ширина и высота
            check = 0x80 # Байт остановки на конце строчки по ширине картинки

        else:
            print("НЕПОНЯТНЫЙ ТИП картинки", flag)
            return(0) # Остановка скрипта

        unclear_6 = f.read(4) # Непонятно
        size_comp = struct.unpack("<I",f.read(4))[0] # Размер сжатых данных дальше
        f2 = io.BytesIO()

        try: # Исключения
            for i in range(h): # Распаковка сжатия
                ss = 0 # Сколько распаковано байт на строчку по ширине картинки
                while True:
                    byte = f.read(1)[0] # Читаем байт управления

                    if byte == check: # Конец распаковки на строчки по ширине картинки
                        if ss != w: # Недостаточно цветов в конце строчки
                            f2.write(b'\x00\x00'*(w - ss))
                        break

                    elif byte & 0x80 == 0x00: # Бит равен нулю
                        f2.write(f.read(byte*2)) # Читаем нужное количество цветов записываем в файл
                        ss += byte

                    else: # Повторение последнего цвета
                        f2.write(b'\x00\x00'*(byte & 0x7F))
                        ss += byte & 0x7F

        except: # Неправельно созданные файлы встречается только в русской версии игры
            f2.write(b'\x00'*(((w*h)*2)-f2.tell())) # Забиваем остаток файла пустыми байтами

        #if f.tell() != end_f:
            #print("    Ошибка в конце файла есть ещё байты", end_f-f.tell(), "позиция", f.tell(),"\n")
            # Лишние байты остаются только в русской версии игры, пираты зачемто поверх оригенальной буквы положили свою криво запакованную букву и она меньше чем оригенальная и байты остались от старой буквы.

        # Если картинка распаковалась правельно
        if f2.tell() == (w*h)*2:
            f2.seek(0)
            f_image = Image.frombuffer('RGB', (w,h), f2.read(w*h*2), 'raw', 'BGR;16', 0, 1)
            self.images = [f_image]

        f2.close()