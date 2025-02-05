#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Остров Сокровищ

import os, sys, io, struct
from PIL import Image

NAME = "Остров Сокровищ"
FORMATS_ARCHIVE = ['dat']
TYPES_ARCHIVE = [('Остров Сокровищ', ('*.dat'))]
GAMES = ["Остров Сокровищ"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["bmp",
                            "tga",
                            "wav",
                            "ogg",
                            "scn",
                            "txt",
                            "bta"]

        self.sup_types = {"bmp":1,
                          "tga":1,
                          "wav":3,
                          "ogg":3,
                          "scn":4,
                          "txt":4,
                          "bta":2}

        self.images = []
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "dat":
            self.OpenArchiveDAT(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "bmp" or format == "tga":
            self.Unpack_TGA(io.BytesIO(self.file.read(size)))
        elif format == "wav" or format == "ogg":
            self.Unpack_OGG(io.BytesIO(self.file.read(size)))
        elif format in ["scn", "txt"]:
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))
        elif format == "bta":
            self.Unpack_BTA(io.BytesIO(self.file.read(size)))

    def OpenArchiveDAT(self,file):
        self.data = [] # Список файлов
        f = open(file,"rb")

        type = f.read(4)
        if type != b'\xD0\x34\x90\xDF': 
            print("Это не архив!")
            return(0) # Остановка скрипта

        f.seek(0)

        f3 = io.BytesIO() # Расшифрованные байты
        fd = b'\xcb\xa3\xff\x13\xf8O\xb3`E\xe4\x1e\x7f\x1d0\x99\xdc\xb1\xe31f\xa2G\xb0}XS\x1b\x95"\x03Mr\xe0CV\xc0\n\\)Ij\xdb,\xb2\'c\x91Y\xbe\xae\x14A\xfcl\xa5\xbc\xd2\xf0\xcc\x15\xdd\xfe\xdf\xacK>\xd1\xd8\xbb93Rd+b\xecU\x1c\xd6\xe8i\xc4\xb6\xba|\x8fs\xe9H\xab\x10g7@D\xe1\xda8\xd7\x1f\x89\x87NF\x04\x9e\x08\xb9y\xf3\xb7\x9c\xa6\x17\x0f\xfb\xaa(Jh\x05&\xe5.\xb4;\x00\x9dw\xf1\xd9\xc8\xc5\xce\xaf2\x84\r\x12\xed\x02\x9at#\xe2\x9b\xf4\xa0P~\x83\xe6$5[\xf6\xb8\x88k\x07\xbf\x85\xfaQ{\xd3\x8c!\x11^\x0b\x9f*\xef\x8e\xd4\x18\x19\xa4Bz\x92m\x90\xc3\xa1\x06\xc2\x97\xbd\xeb\x16?\x86\xcf\x8d_\xc6\x8aZ\xa9:]\xf9-%\xf2\xe7<\xfd\xc1\x93x\x98v\te\xd04/\xea\x96\xde\xd5\xc7\x01o\x1a\x8bq=\x94\xf7T\x0cna6\xee\xf5\xad\xa7\x81\xc9\x80\x0ep\xca\xcduW\xa8L\xb5 \x82\x00\x00'
        f2 = io.BytesIO(fd) # Байты ключи для расшифровки

        (self.dirname, filename) = os.path.split(file)

        # Сколько расшифровать байт 
        if filename == "Chapter1.dat":
            col = 17440
        elif filename == "Chapter2.dat":
            col = 18720
        elif filename == "Chapter3.dat":
            col = 16288
        elif filename == "Common.dat":
            col = 92832
        elif filename == "Music.dat":
            col = 4768
        elif filename == "Script.dat":
            col = 44448
        elif filename == "Sound.dat":
            col = 45472
        elif filename == "Speech.dat":
            col = 22816
        else:
            print("Непонятно сколько надо расшифровать байт", filename)
            return(0) # Остановка скрипта

        b256 = 0x00 # Этот байт 256
        b257 = 0x00 # Этот байт 257

        while col != 0: # Остановка когда расшифровали все байты.
            b256 = (b256 + 1) & 0xFF # Плюс +1   Изначально число 16 +1= 17
            f2.seek(b256)
            v8 = f2.read(1)[0] # Читаем 1 байт E3

            b257 = (v8 + b257) & 0xFF # Читаем 1 байт 0xE3 + b257 Получаем байт AF
            f2.seek(b257)
            v11 = f2.read(1)[0] # Достаём по адресу 1 байт B3

            f2.seek(b256)
            f2.write(struct.pack("B", v11)) # Записываем заместо байта E3 байт B3

            f2.seek(b257)
            f2.write(struct.pack("B", v8)) # Записываем заместо байта B3 байт E3

            f2.seek((v8 + v11) & 0xFF) # Адрес байта расшифровки
            byte = f.read(1)[0] ^ f2.read(1)[0] # Расшифровка байта
            f3.write(struct.pack("B", byte)) # Запись расшифрованного байта

            col -= 1 # Минус -1 от количество файлов

        #print("Конец расшифровки.")
        f2.close()

        f3.seek(0)
        # 16 байт
        type = f3.read(4) # Тип архива PACK
        size = struct.unpack("<I",f3.read(4))[0] # Размер таблицы +16 байт данных после заголовока
        size_2 = struct.unpack("<I",f3.read(4))[0] # Размер всего архива
        unclear = struct.unpack("<I",f3.read(4))[0] # Непонятно всегда нули

        # 16 байт
        col = struct.unpack("<I",f3.read(4))[0] # Количество файлов
        unclear = struct.unpack("<I",f3.read(4))[0] # Непонятно
        unclear = struct.unpack("<I",f3.read(4))[0] # Непонятно всегда число 64
        unclear = struct.unpack("<I",f3.read(4))[0] # Непонятно всегда число 128 размер одной строчки для файла 128 байт ?

        for i in range(col):
            f_path = f3.read(104).split(b"\x00")[0].decode("cp1251") # Имя файла
            unclear = struct.unpack("<I",f3.read(4))[0] # Непонятно маленькие числа
            unclear_2 = struct.unpack("<I",f3.read(4))[0] # Непонятно Может это хеш ?
            offset = struct.unpack("<I",f3.read(4))[0] # Оффсет
            size = struct.unpack("<I",f3.read(4))[0] # Размер
            fd = f3.read(8) # Непонятно всегда нули
            format = f_path.split(".")[-1].lower()
            self.data.append((f_path, offset, size, format))

        self.file = f

    def Unpack_OGG(self, f): 
        self.sound = f

    def Unpack_TXT(self, f): 
        self.text = f.read().decode("cp1251")

    def Unpack_TGA(self, f):
        try: # Исключения
            image = Image.open(f)
            self.images = [image]
        except :
            print("Не поддерживается")

    def Unpack_BTA(self, f):
        data = [] # Список файлов
        type = f.read(4) # 4 байта индефикатор CTA1

        # Позиция 32
        # 4 байта размер непонятного файла если он есть стоит число больше 0
        f.seek(32)
        size = struct.unpack("<I",f.read(4))[0] # Размер непонятного файла
        # Если он есть то он начинается с оффсета 60
        # Файлы 02 EP.BTA, BLOW.BTA, PAUK.BTA

        f.seek(44)
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        offset_tab = struct.unpack("<I",f.read(4))[0] # Оффсет таблицы
        f.read(8) # 8 байт непонятно
        # Если есть непонятный файл начинается непонятный файл, посленего таблица
        # Если нет непонятного файла начинается таблица

        if size > 0: # Если есть непонятный файл 02 EP.BTA, BLOW.BTA, PAUK.BTA
            #print("Тут непонятный файл размером в", size)
            pass

        f.seek(offset_tab) # Оффсет 60 если нет непонятного файла.
        for i in range(col):
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size = struct.unpack("<I",f.read(4))[0] # Размер
            data.append((offset,size))

        for i in data:
            f.seek(i[0])
            fd = f.read(i[1])

            # Чтение и разбивка на файлы FRAM
            data_FRAM = [] # Список внутрених файлов
            f2 = io.BytesIO(fd)
            # Заголовок занимает 20 байт
            col = struct.unpack("<H",f2.read(2))[0] # Количество файлов Читается именно по 2 байта
            unclear = struct.unpack("<H",f2.read(2))[0] # Непонятно
            size_comp = struct.unpack("<I",f2.read(4))[0] # Размер всех сжатых файлов
            size_2 = struct.unpack("<I",f2.read(4))[0] # Размер файла между таблицыми если он есть
            offset_2 = struct.unpack("<I",f2.read(4))[0] # Оффсет файла между таблицыми если он есть
            f2.read(4) # FRAM

            for ii in range(col):
                # Занимает 16 байт
                frames_col = struct.unpack("<H",f2.read(2))[0] # Количество кадров в картинке, сколько строчек прочитать по 28 байт в начале файла
                unclear_2 = struct.unpack("<H",f2.read(2))[0] # Непонятно
                size = struct.unpack("<I",f2.read(4))[0] # Размер
                offset = struct.unpack("<I",f2.read(4))[0] # Оффсет
                unclear_3 = struct.unpack("<H",f2.read(2))[0] # Непонятно
                unclear_4 = struct.unpack("<H",f2.read(2))[0] # Непонятно
                data_FRAM.append((offset, size, frames_col))
                #print("Кол кадров", frames_col, unclear_2, " размер оффсет", size,offset, " ", unclear_3, unclear_4)

            #if offset_2 > 0: # Если между таблицами есть непонятный файл, такой есть долько в файле BLOW.BTA там 25 таких файлов увсех размер 7348 байт 
                # Этот файл читается сразу после таблицы
                #print("Между таблицами непонятный файл", mult_file, "оффсет", offset_2, "размер",size_2)
                #f2.seek(offset_2)
                #fd = f2.read(size_2)

            for j in data_FRAM:
                f2.seek(j[0])
                fd = f2.read(j[1])

                f3 = io.BytesIO(fd)
                self.Pic(f3, j[2]) # Для распаковки картинок
                f3.close()

            f2.close()
        f.close()

    def Pic(self, f, frames_col):
        data = [] # Список картинок внутри

        for i in range(frames_col):
            unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно
            unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно
            w, h = struct.unpack("<II",f.read(8)) # Ширина и высота
            unclear_3 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_4 = struct.unpack("<H",f.read(2))[0] # Непонятно
            size_comp = struct.unpack("<I",f.read(4))[0] # Размер сжатых данных
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            if w > 0 and h > 0 and size_comp > 0: # Если строчка не пуста
                #print("Ширина и высота", w, h, "Оффсет", offset, "Размер сжатых данных", size_comp)
                #print("Непонятно", unclear_1, unclear_2, unclear_3, unclear_4, "Картинка должна быть размером в",(w*h)*2)
                #print()
                data.append((offset, size_comp, w, h))

        for i in data:
            f.seek(i[0])
            f2 = io.BytesIO(f.read(i[1]))
            self.Decompression(f2, i[2], i[3])
            f2.close()

    def Decompression(self, f, w, h):
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)
        f2 = io.BytesIO()

        while True:
            if f.tell() == end_f:
                break

            fd = f.read(1)
            if fd[0] >= 0x80: # Сжатые байты проверка на старший бит байта
                byte_2 = f.read(1)
                #byte_1 = f.read(1)
                byte = f.read(1) + byte_2
                f2.write(byte * ((fd[0]-0x80)+1))
                #print("Повторить",(fd[0]-0x80)+1)

            else: # Не сжатый
                f2.write(f.read(1)+fd) # byte_1 + byte_2

        if f2.tell() != w*h*2:
            pos = f2.tell()
            #print("Ширина и высота", w, h)
            #print("Распакованный файл должен быть размером в", (w*h)*2)
            #print("    # Ошибка неправельное количество распакованных байт", pos)

            if f2.tell() < w*h*2:
                need = (w*h*2)-pos
                #print("    Надо ещё байт", need, "Размер сжатых данных", end_f)
                f2.write(b'\x00' * need) # Просто дописываем нужное число байт.

            elif f2.tell() > w*h*2:
                pass
                #print("    Распаковались лишние байты в количестве", f2.tell()-(w*h*2), "Размер сжатых данных", end_f)
                # Эти мусорные байты не нужны, можно их не учитывать.

            f2.seek(0)
            f_image = Image.frombuffer('RGB', (w,h), f2.read(w*h*2), 'raw', 'BGR;15', 0, 1)
            self.images.append(f_image)
            f2.close()

        else:
            f2.seek(0)
            f_image = Image.frombuffer('RGB', (w,h), f2.read(w*h*2), 'raw', 'BGR;15', 0, 1)
            self.images.append(f_image)
            f2.close()