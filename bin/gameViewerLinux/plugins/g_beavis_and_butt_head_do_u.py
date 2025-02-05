#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# MTV's Beavis and Butt-Head Do U
# MTV's Beavis and Butt-Head Bunghole in One

import os, sys, io, struct
from PIL import Image

NAME = "Beavis and Butt-Head Do U"
FORMATS_ARCHIVE = ['act', 'bg', 'fnt']
TYPES_ARCHIVE = [('Beavis and Butt-Head Do U', ('*.act', '*.bg', '*.fnt'))]
GAMES = ["MTV's Beavis and Butt-Head Do U", 
         "MTV's Beavis and Butt-Head Bunghole in One"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["pic",
                            "pic_2",
                            "pic_3"]  

        self.sup_types = {"pic":1,
                          "pic_2":2,
                          "pic_3":1}

        self.images = []
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "act":
            self.OpenArchiveACT(file)
        elif format == "bg":
            self.OpenArchiveBG(file)
        elif format == "fnt":
            self.OpenArchiveFNT(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "pic":
            self.Unpack_PIC(io.BytesIO(self.file.read(size)), data_res[4], data_res[5])
        elif format == "pic_2":
            self.Unpack_PIC_2(io.BytesIO(self.file.read(size)))
        elif format == "pic_3":
            self.Unpack_PIC_3(io.BytesIO(self.file.read(size)), data_res[4], data_res[5])
    
    def OpenArchiveACT(self,file):
        f = open(file,"rb")
        size = struct.unpack("<I",f.read(4))[0] # Размер файла целиком

        unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно Почти вовсех файлах нули но в файлах 00060618.ACT, 00060619.ACT записанно 01 00
        col_44 = struct.unpack("<H",f.read(2))[0] # Количество строчек по 44 байта связанно с оффсетом на 16 (Позиция 6)
        col_unclear_1 = struct.unpack("<H",f.read(2))[0] # Количество чегото
        col_20 = struct.unpack("<H",f.read(2))[0] # Количество строчек по 20 байт

        unclear_3 = struct.unpack("<I",f.read(4))[0] # Непонятно 4 байта Всегда нули 00 00 00 00

        offset_44 = struct.unpack("<I",f.read(4))[0] # Оффсет на таблицу по 44 байта на строчку. (Позиция 16) Если оффсет неравен позиции 32 то читается ещё несколько оффсетов по 4 байта на данные

        offset_12 = struct.unpack("<I",f.read(4))[0] # Оффсет на таблицы по 12 байт
        offset_20 = struct.unpack("<I",f.read(4))[0] # Оффсет на таблицу по 20 байт

        # Таблица по 8 байт
        # 2 байта непонятно, 2 байта непонятно, 2 байта непонятно, 2 байта непонятно.

        data = [] # Список файлов
        # Таблица по 20 байт
        f.seek(offset_20)
        for i in range(col_20):
            unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно
            offset_76 = struct.unpack("<I",f.read(4))[0] # Оффсет на строчку размером в 76 байт
            size_0 = struct.unpack("<I",f.read(4))[0] # Размер распакованого файла
            w, h = struct.unpack("<HH",f.read(4)) # Ширина и высота
            offset_comp = struct.unpack("<I",f.read(4))[0] # Оффсет начало сжатых данных
            data.append((offset_comp, w, h))

        data.append((size, "", "")) # Для правельного расчёта размера файла.

        # Есть повторыные ссылки на картинки
        data = list(set(data)) # Удаляет одинаковые значения (множество) и делаем обратно список
        data.sort(key=lambda i: i[0]) # От сортировано data2 по i[1] второму элементу,по оффсету, можно полюбому

        data_2 = [] # Список файлов
        for i in range(len(data)-1):
            size = data[i+1][0] - data[i][0] # Получаем размер файла
            data_2.append((data[i][0], size, data[i][1], data[i][2]))
            self.data.append((str(data[i][0])+".pic", data[i][0], size, "pic", data[i][1], data[i][2])) 

        self.file = f

    def OpenArchiveBG(self,file):
        f = open(file,"rb")
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        self.data.append(("0.pic_2", 0, end_f, "pic_2"))
        self.file = f
        
    def OpenArchiveFNT(self,file):
        data = [] # Список файлов
        f = open(file,"rb")
        size_end = struct.unpack("<I",f.read(4))[0] # Размер файла
        #unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно
        # Куча информации читается по 2 байта

        f.seek(20) # На 20 байте
        offset_tab = struct.unpack("<I",f.read(4))[0] # Оффсет таблицу с данными
        # Непонятные данные могут отсутствовать

        f.seek(offset_tab)
        f.read(4) # Ширина буквы
        end = struct.unpack("<I",f.read(4))[0] # Читаем данные чтобы определить конец таблицы

        f.seek(offset_tab)

        while f.tell() != end: # Остановка когда достигним конца таблицы
            w = struct.unpack("<I",f.read(4))[0] # Ширина картинки
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет буквы
            data.append((w, offset))

        data.append(("", size_end)) # Для правельного расчёта размер файла

        for i in range(len(data)-1):
            size = data[i+1][1] - data[i][1] # Получаем размер файла
            whole, rest = divmod(size, data[i][0]) # Делит правельно сначало идёт целое число потом остаток
            self.data.append((str(data[i][1])+".pic_3", data[i][1], size, "pic_3", data[i][0], whole)) # Ширина data[i][0], высота whole

        self.file = f

    def Unpack_PIC(self, f, w, h):
        f2 = io.BytesIO()
        size_2 = (w*h) * 2 # Размер распакованного файла должен быть таким

        while f2.tell() != size_2: # Остановка когда достигним конца распакованного файла.
            byte = struct.unpack("<H",f.read(2))[0] # Управляющие байты

            if byte & 0x8000 == 0x8000: # Повторить следующий цвет
                col = (byte & 0x7FFF) + 1 # Повторить раз
                f2.write(f.read(2) * col)

            else: # Просто чтение цветов(2 байта)
                if byte == 0x0000 and f2.tell() == size_2: # Остановка распаковки
                    break
                f2.write(f.read((byte+1)*2))

        if f2.tell() == size_2: # Картинка правельно распаковалась
            f2.seek(0)
            f_image = Image.frombuffer('RGB', (w,h), f2.read(w*h*2), 'raw', 'BGR;16', 0, 1)
            self.images = [f_image]

        # В конце файла могут остатся 2 байта 00 00 остановки распаковки это нормально
        # Гольф игры файл 01 00100003.ACT сжатые данные 4 байта D3 AB 41 FF в конце нет байтов остановки распаковки 00 00 оффсет 83196

        f2.close()
        f.close()

    def Unpack_PIC_2(self, f):
        # Заголовок 80 байт потом уже читаются данные.
        size = struct.unpack("<I",f.read(4))[0] # Размер файла целиком
        f.read(4) # Непонятно всегда нули 00 00 00 00

        col_8 = struct.unpack("<H",f.read(2))[0] # Количество чегото Может быть 0,1.
        col_10 = struct.unpack("<H",f.read(2))[0] # Количество строчек по 28 байт Может быть 0,1,2. Связан с 32 оффсетом

        col_12 = struct.unpack("<H",f.read(2))[0] # Количество строчек по 8 байт котое надо прочитать. Может быть 0-43 в файле 0011002C.BG Связан с 36 оффсетом  Г 0011000B.BG

        col_14 = struct.unpack("<H",f.read(2))[0] # Количество строчек по 8 байт. Может быть 0,1,2. Связан с 40 оффсетом
        col_16 = struct.unpack("<H",f.read(2))[0] # Количество строчек по 8 байт. Может быть 0,1,2. Связан с 44 оффсетом
        col_18 = struct.unpack("<H",f.read(2))[0] # Количество строчек по 8 байт. Может быть 0,1,2. Связан с 48 оффсетом
        col_20 = struct.unpack("<I",f.read(4))[0] # Количество строчек по 12 байт. Может быть 0,1. Связан с 52 оффсетом
        col_24 = struct.unpack("<I",f.read(4))[0] # Количество палитр Может быть 1,2. Связан с 60 оффсетом
        col_28 = struct.unpack("<I",f.read(4))[0] # Количество строчек по 12 байт. Может быть 0-39 в файле 0011001B.BG  Связан с 68 оффсетом

        # Позиция 32 в архиве Дальше идут оффсеты
        offset_32 = struct.unpack("<I",f.read(4))[0] # Оффсет на строчек по 28 байт после заголовка на 80 байте.(Позиция 32) 
        offset_36 = struct.unpack("<I",f.read(4))[0] # Оффсет на строчки по 8 байт (94 03 07 00 09 06 9A 02) (Позиция 36)
        offset_40 = struct.unpack("<I",f.read(4))[0] # Оффсет Читается по 8 байт (Позиция 40) количество записанно в col_14  (03 00 00 00 00 03 00 00)
        offset_44 = struct.unpack("<I",f.read(4))[0] # Оффсет Читается по 8 байт (Позиция 44)  количество записанно в col_16  E0 01 00 00 0C 03 00 00 ширина и высота
        offset_48 = struct.unpack("<I",f.read(4))[0] # Оффсет Читается по 8 байт (Позиция 48)  количество записанно в col_18 (04 00 00 00 EC 04 00 00)
        offset_52 = struct.unpack("<I",f.read(4))[0] # Оффсет Читается по 12 байт (Позиция 52)   количество записанно в col_20 (90 06 D0 02 0C 1E 00 00 0C 05 00 00) Читается 2 байта ширина, 2 байта высота, 4 байта оффсет тайловой карты для картинки 8 бит, 4 байта оффсет картинок 8 бит (размер картинки 256 байт). 0011002C.BG

        f.read(4) # Непонятно всегда нули 00 00 00 00 (Позиция 56)
        offset_60_pal = struct.unpack("<I",f.read(4))[0] # Оффсет где надо читать ссылки на палитру 8 байт 00 01 00 00 0C 16 00 00. (Позиция 60)
        f.read(4) # Непонятно всегда нули 00 00 00 00 (Позиция 64)
        offset_byte_12 = struct.unpack("<I",f.read(4))[0] # Оффсет на строчки по 12 байт (Позиция 68)
        f.read(4) # Непонятно всегда нули 00 00 00 00 (Позиция 72)
        f.read(4) # 4 байта всегда равны байтам 04 00 BC FF
        # (Позиция 76) 4 байта всегда равны 04 00 BC FF
        # Заголовок 128 байт, после него уже идут другие данные

        for col_10_number in range(col_10): # Читаем информацию о картинках в файле
    # 01 00 00 00 01 00 02 00 00 B0 04 00 80 02 E0 01 00 00 00 00 74 04 00 00 DC 0D 00 00
            unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно
            unclear_2 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_3 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_4 = f.read(1)[0] # Непонятно
            unclear_5 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_6 = f.read(1)[0] # Непонятно
            w = struct.unpack("<H",f.read(2))[0] # Ширина кратинки
            h = struct.unpack("<H",f.read(2))[0] # Высота картинки
            unclear_7 = struct.unpack("<I",f.read(4))[0] # Непонятно нули

            offset_map = struct.unpack("<I",f.read(4))[0] # Оффсет на тайловую карту
            # ссылка на (количество тайлов в 2 байта ширину и 2 байта высоту картинки, 4 байта количество картинок в архиве, тайловая карта (размер тайловой карты расчитвается ширину умножить на высоту и умножить на 2))
            offset_picture = struct.unpack("<I",f.read(4))[0] # Оффсет на начало картинок
            #print(w,h, "оффсет на тайловую карту", offset_map, "оффсет на картинки", offset_picture)

            ##################
            f_pos = f.tell() # Запоминаем позицию для возврата сюда
            f.seek(offset_map) # Переход к тайловой карте
            w_col, h_col = struct.unpack("<HH",f.read(4)) # Ширина и высота Количество картинок по ширине и высоте картинки

            offset_picture_tiles = struct.unpack("<I",f.read(4))[0] # Количество картинок
            # Читаем тайловую карту
            number_sprite = struct.unpack("<{}H".format(w_col * h_col), f.read((w_col * h_col)*2)) # Выдаёт список в виде чисел Номер тайла

            #print(w_col, h_col, "получим картинку", w_col*32, h_col*8, "количество картинок", offset_picture_tiles)

            # Чтение картинок
            data_pic = ["0"] # Список картинок тайлов, Первый элемент пустой
            f.seek(offset_picture) # Переходим на начало картинок

            for i in range(offset_picture_tiles):
                f_image = Image.frombuffer('RGB', (32,8), f.read(512), 'raw', 'BGR;16', 0, 1) # 16 бит RGB 16
                data_pic.append(f_image)

            # Вставляем тайлы в картинку
            img = Image.new("RGB", (w,h),(255)) # Создание новой картинки с белым фоном в скобачках ширина и высота картинки
            wx = 0 # Позиция x вставления в картинки по ширине
            hy = 0 # Позиция y вставления в картинки по высоте
            Block_number = 0 # Номер блока на котором находимся

            for number in number_sprite:
                Block_number += 1 # Номер блока на котором находимся
                img.paste(data_pic[number],(wx,hy)) # Вставляем картинку в картинку

                wx += 32 # Делаем сдвиг по ширине на 32 пикселей
                if Block_number%w_col== 0: # Значит мы переходим на на новый строчку по высоте картинки
                    hy += 8 # Прибавляем к высоте
                    wx = 0  # Ставим на начало строки

            self.images.append(img) # Добавляем картинку
            f.seek(f_pos) # Возврат к таблице
        ##################

        if col_20 == 1: # Если в файле есть 8 битная картинка
            # Чёрно белая палитра
            Pal = b'' # Палитра
            for i in range(256):
                #Pal += struct.pack("BBB", i,i,i)
                dss = 255-i # Обратная палитра
                Pal += struct.pack("BBB", dss,dss,dss)

            #######################
            f.seek(offset_52) # Переходим на чтение 12 байт для картинки 8 бит

            # Оффсет Читается по 12 байт (Позиция 52)   количество записанно в col_20 (90 06 D0 02 0C 1E 00 00 0C 05 00 00) Читается 2 байта ширина, 2 байта высота, 4 байта оффсет тайловой карты для картинки 8 бит, 4 байта оффсет картинок 8 бит (размер картинки 256 байт). 0011002C.BG

            w = struct.unpack("<H",f.read(2))[0] # Ширина кратинки
            h = struct.unpack("<H",f.read(2))[0] # Высота картинки

            offset_map = struct.unpack("<I",f.read(4))[0] # Оффсет на тайловую карту
            offset_picture = struct.unpack("<I",f.read(4))[0] # Оффсет на начало картинок
            #print(w,h, "оффсет на тайловую карту", offset_map, "оффсет на картинки", offset_picture)

            f.seek(offset_map) # Переход к тайловой карте
            w_col, h_col = struct.unpack("<HH",f.read(4)) # Ширина и высота Количество картинок по ширине и высоте картинки

            offset_picture_tiles = struct.unpack("<I",f.read(4))[0] # Количество картинок
            # Читаем тайловую карту
            number_sprite = struct.unpack("<{}H".format(w_col * h_col), f.read((w_col * h_col)*2)) # Выдаёт список в виде чисел Номер тайла

            #print(w_col, h_col, "получим картинку", w_col*32, h_col*8, "количество картинок", offset_picture_tiles)

            # Чтение картинок
            data_pic = ["0"] # Список картинок тайлов, Первый элемен пустой
            f.seek(offset_picture) # Переходим на начало картинок

            for i in range(offset_picture_tiles):
                f_image = Image.frombuffer('P', (32,8), f.read(256), 'raw', 'P', 0, 1) # 8 бит RGB 8
                data_pic.append(f_image)

            # Вставляем тайлы в картинку
            img = Image.new("P", (w,h),(255)) # Создание новой картинки с белым фоном в скобачках ширина и высота картинки
            wx = 0 # Позиция x вставления в картинки по ширине
            hy = 0 # Позиция y вставления в картинки по высоте
            Block_number = 0 # Номер блока на котором находимся

            for number in number_sprite:
                Block_number += 1 # Номер блока на котором находимся
                img.paste(data_pic[number],(wx,hy)) # Вставляем картинку в картинку

                wx += 32 # Делаем сдвиг по ширине на 32 пикселей
                if Block_number%w_col== 0: # Значит мы переходим на на новый строчку по высоте картинки
                    hy += 8 # Прибавляем к высоте
                    wx = 0  # Ставим на начало строки

            img.putpalette(Pal) # Добавляем палитру в картинку
            self.images.append(img) # Добавляем картинку

        f.close()

    def Unpack_PIC_3(self, f, w,h):
        f_image = Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1)
        self.images.append(f_image) # Добавляем картинку
        f.close()