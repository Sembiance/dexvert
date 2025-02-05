#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# The Sting!(Der Clou! 2)(Ва-банк!)

import os, sys, io, struct
from PIL import Image

NAME = "The Sting!"
FORMATS_ARCHIVE = ['wld', 'exe']
TYPES_ARCHIVE = [('The Sting!', ('*.wld', '*.exe'))]
GAMES = ["The Sting!"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["page",
                            "node",
                            "tif",
                            "pic"]

        self.sup_types = {"page":1,
                          "node":1,
                          "tif":1,
                          "pic":1}

        self.images = []
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "wld":
            self.OpenArchiveWLD(file)
        elif format == "exe":
            self.OpenArchiveEXE(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "page":
            self.Unpack_PAGE(io.BytesIO(self.file.read(size)))
        elif format == "node":
            self.Unpack_NODE(io.BytesIO(self.file.read(size)))
        elif format == "tif":
            self.Unpack_TIF(io.BytesIO(self.file.read(size)))
        elif format == "pic":
            self.Unpack_PIC(io.BytesIO(self.file.read(size)))

    def OpenArchiveWLD(self,file):
        self.data = [] # Список файлов
        f = open(file,"rb")
        path_folder = "" # Путь до файла

        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)

        while True:
            f_pos = f.tell()
            check = f.read(4).decode("utf8") # Индефикатор

            if check in ['WRLD', 'TEXP', 'GROU', 'OBGR', 'LIST', 'OBJS', 'MAKL', 'TREE', 'END ', 'EOF ']:
                path_folder += check+"\\" # Добавляем путь

                fd = f.read(4) # 4 байта нулей 00 00 00 00
                if fd != b'\x00\x00\x00\x00':
                    print("Непонятные байты", fd)

                if check == 'END ': # Конец блока с данными
                    path_folder = "" # Возврат в начальную папку

                if f.tell() == end_f: # EOF
                    #print("Конец файла")
                    break

            elif check in ['PAGE', 'ENTR', 'MODL', 'OBJ ', 'NODE']:
                size = struct.unpack(">I",f.read(4))[0] + 8 # Размер файла прямой понядок байтов
                f.seek(f_pos) # Переходим к началу файла
                f.seek(size, 1) # Пропускаем байты файла
                self.data.append((path_folder+str(f_pos)+"."+check, f_pos, size, check.lower()))
            else:
                print("    Ошибка непонятно что делать, позиция", f_pos, check)
                break
        self.file = f

    def OpenArchiveEXE(self,file):
        self.data = [] # Список файлов
        f = open(file,"rb")
        dataf = f.read() # Читаем весь файл и записываем его в dataf для поиска

        offset_tif = dataf.find(b'\x49\x49\x2A\x00\x08\x03\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF', 0) # Оффсет первой картинки tif

        if offset_tif == -1: # Зашита если в файле .exe нет картинки то это явно другой файл.
            #print("Это не тот файл")
            return(0) # Остановка скрипта

        offset = 0 # Начало поиска оффсет
        while True:
            offset = dataf.find(b'\xD6\x03\x00\x00', offset) # Поиск значения Search_byte, по месту нахождения в файле offset Найденная позиция байта

            f.seek(offset+8)
            check = f.read(4) # Проверка
            if check == b'\x00\x00\x00\x00': # Нашли таблицу
                offset -= 4 # Получаем оффсет начало таблицы
                #print("Позиция таблицы файлов", offset)

                f.seek(offset) # Переходим на начало таблицы
                offset_f_1 = struct.unpack("<I",f.read(4))[0] # Оффсет первого файла неправельный
                difference = offset_f_1 - offset_tif # Разница между оффсетами, найденым оффсетом первой картинки и записанным оффсетом этой картинки
                # Это число надо отнимать от оффсета файлов
                break

            if offset == -1: # Если не нашли байты остановка
                break

            offset += 1

        f.seek(offset) # Переходим на начало таблицы
        while True:
            offset_f = struct.unpack("<I",f.read(4))[0] - difference # Оффсет
            size = struct.unpack("<I",f.read(4))[0] # Размер
            f.read(2) # Непонятно
            check = f.read(6)
            f_pos = f.tell() # Запоминаем позицию для возврата

            if check != b'\x00\x00\x00\x00\x00\x00': # Если тут не 6 байт нулей то это конец таблицы файлов
                break

            f.seek(offset_f)
            check_2 = f.read(4) # Проверка

            if check_2 == b'\x49\x49\x2A\x00': # Это кратинка TIF
                tip = "tif" # 65 штук

            elif check_2 == b'NMF ': # Models
                tip = "NMF"

            elif check_2 == b'\x28\x00\x00\x00': # Картинки
                tip = "pic" # 59 штук

            elif check_2 == b'\xC0\x00\xC8\x80': # Какието тексты невнятные
                tip = "bin_txt"

            elif check_2 == b'\x00\x00\x00\x00' and f.read(4) == b'\x28\x00\x00\x00': # Это иконки
                offset_f += 4 # Это лишний заголовок 4 байта нулей
                size -= 4
                tip = "pic" # Всего тут две картинки
            else:
                tip = "bin"

            self.data.append((str(offset_f)+"."+tip, offset_f, size, tip))
            f.seek(f_pos) # Возврат к таблице

        self.file = f

    def Unpack_PAGE(self, f):
        type = f.read(4) # Тип архива
        size = struct.unpack(">I",f.read(4))[0] + 8 # Размер всего файла
        unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно
        w, h = struct.unpack("<II",f.read(8)) # Ширина и высота
        unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно
        col = struct.unpack("<I",f.read(4))[0] # Количество

        for i in range(col):
            # Имя файла с байтом 00 выровненно к 4 байтам
            ss = 0
            f_path = b'' # Читаем имя файла до байта 00
            while True:
                ss += 1
                bait = f.read(1) # Байт строчки
                if bait == b'\x00':
                    f_path = f_path.decode("cp1251") # Переделаваем байты в строчку "utf8"
                    break
                f_path += bait # Прибавляем байт

            whole, rest = divmod(ss, 4) # Делит правельно сначало идёт целое число потом остаток

            if rest != 0: # Если есть остаток надо прочитать байты
                f.read(4-rest) # Читаем пустые байты, для выравнивания

            # Непонятные значения тоже какието координаты или ширина и высота вырезаемой картинки

            # Координаты по ширине и высоте для начало вырезания.
            coordinates_w, coordinates_h = struct.unpack("<II",f.read(8))
            # Координаты по ширине и высоте для конец вырезания.
            coordinates_ww, coordinates_hh = struct.unpack("<II",f.read(8))

            fd = f.read(16) # Читаем и записываем непонятные байты

        type = f.read(4) # Тип картинки
        #if type != b'TXPG': # Проверка на архив
            #print("ЭТО НЕ картинка", type)
            #return(0) # Остановка скрипта

        f.read(4) # Нули 00 00 00 00
        f_image = Image.frombuffer('RGB', (w,h), f.read(w*h*2), 'raw', 'BGR;15', 0, 1)
        self.images = [f_image]
        f.close()

    def Unpack_NODE(self, f):
        dataf = f.read() # Читаем весь файл и записываем его в dataf для поиска
        offset = dataf.find(b'SHAD', 0) # Поиск значения b'SHAD', по месту нахождения в файле offset Найденная позиция байта
        # В одном файле может быть только одна текстура, проверил на всех файлах.

        if offset != -1: # Если нашли картинку
            f.seek(offset+4) # Предположительный оффсет данных
            #f.read(4) # Индефикатор SHAD
            w = struct.unpack("<I",f.read(4))[0] # Ширина
            h = struct.unpack("<I",f.read(4))[0] # Высота

            if w > 0:
                f_image = Image.frombuffer('RGB', (w,h), f.read(w*h*2), 'raw', 'BGR;15', 0, 1)
                self.images = [f_image]
        f.close()

    def Unpack_TIF(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_PIC(self, f):
        type = f.read(4) # 28 00 00 00 это размер заголовка файла. Всегда такой.
        w, h = struct.unpack("<II",f.read(8)) # Ширина и высота
        planes = struct.unpack("<H",f.read(2))[0] # 01 00 Устанавливает число плоскостей для целевого устройства. Это значение должно быть 1.
        bit = struct.unpack("<H",f.read(2))[0] # Битность картинки
        # Может быть только 0, 1, 4, 8, 16, 24, 32 # 0 Обозначает форматом PNG или JPEG.

        compression = struct.unpack("<I",f.read(4))[0]
        #print("Ширина и высота", w, h, "Битность", bit)
        f.seek(40)

        col_byte, rest_bit = divmod(w * bit, 8) # Делит правельно сначало идёт целое число потом остаток
        if rest_bit != 0: # Есть остаток бит значит надо прочитать ещё +1 байт
            col_byte += 1 # +1 байт

        #print("Прочитать байт в ширину", col_byte, "остаток бит", rest_bit)

        whole, rest = divmod(col_byte, 4) # Делит правельно сначало идёт целое число потом остаток
        if rest != 0: # Количество байт не делится на 4 байта есть остаток
            junk_bytes = 4 - rest # Лишние байты
            #print("    Лишние байты которые надо прочитать", junk_bytes)
        else: # Остаток 0
            junk_bytes = 0 # Нужно для алгоритма чтения, чтобы когда нет значения не выдало ошибку.

        # Исправление для иконок .ico

        if w == 16 and h == 32: # Высота неправельная
            h = 16 # Правельная

        if w == 32 and h == 64: # Высота неправельная
            h = 32 # Правельная

        if bit == 1:
            Pal = b'' # Палитра
            for i in range(2): # Палитра 8 байта
                B = f.read(1)
                G = f.read(1)
                R = f.read(1)
                f.read(1) # A прозрачность
                Pal += R+G+B # RGB

            f2 = io.BytesIO() # Файл картинки без лишних байт

            for i in range(h):
                f2.write(f.read(col_byte))
                f.read(junk_bytes) # Читаем ненужные байты

            f2.seek(0)
            f_image = Image.frombuffer('1', (w,h), f2.read(w*h//8), 'raw', '1', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
            self.images = [f_image]
            f2.close()

        elif bit == 4: # Биты читаются как SEGA
            Pal = b'' # Палитра
            for i in range(16): # Палитра 64 байта
                B = f.read(1)
                G = f.read(1)
                R = f.read(1)
                f.read(1) # A прозрачность
                Pal += R+G+B # RGB

            f2 = io.BytesIO() # Файл картинки без лишних байт

            for i in range(h):
                f2.write(f.read(col_byte))
                f.read(junk_bytes) # Читаем ненужные байты

            # Ошибка в PIL
            # Ширина 4 битной картинки должна всегда равнятся кратной 2 иначе программа будет выдовать ошибку что данных нехватает для чтения, Оригенальная ширина 39, ширина которую он может прочитать 40
            check = 0
            whole, rest = divmod(w, 2) # Делит правельно сначало идёт целое число потом остаток
            if rest == 1:
                w += 1
                check = 1 # Чтобы понять что мы поменяли ширину
                #print("    Дописал в ширину +1 к картинки и за PIL")

            f2.seek(0)
            f_image = Image.frombuffer('P', (w,h), f2.read(w*h//2), 'raw', 'P;4', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)

            if check == 1: # Если поменяли ширину, вырезаем картинку
                f_image = f_image.crop((0,0, w-1, h)) # Вырезаем картинку

            f_image.putpalette(Pal) # Добавляем палитру в картинку
            self.images = [f_image]
            f2.close()

        elif bit == 8:
            Pal = b'' # Палитра
            for i in range(256):
                B = f.read(1)
                G = f.read(1)
                R = f.read(1)
                f.read(1) # A прозрачность
                Pal += R+G+B # RGB

            f2 = io.BytesIO() # Файл картинки без лишних байт

            for i in range(h):
                f2.write(f.read(col_byte))
                f.read(junk_bytes) # Читаем ненужные байты

            f2.seek(0)
            f_image = Image.frombuffer('P', (w,h), f2.read(w*h), 'raw', 'P', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
            f_image.putpalette(Pal) # Добавляем палитру в картинку
            self.images = [f_image]
            f2.close()

        elif bit == 24: # Проверил всё нормально распаковывается.
            f2 = io.BytesIO() # Файл картинки без лишних байт

            for i in range(h):
                f2.write(f.read(col_byte))
                f.read(junk_bytes) # Читаем ненужные байты

            f2.seek(0)
            f_image = Image.frombuffer('RGB', (w,h), f2.read(w*h*3), 'raw', 'BGR', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
            self.images = [f_image]
            f2.close()