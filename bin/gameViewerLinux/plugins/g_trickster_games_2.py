#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Trickster Games 2
# Алиса в Стране Чудес
# Весёлые картинки - Незнайка идёт в школу
# Ералаш Лэнд
# Красная Шапочка
# Петрович и все все все
# Смешарики Параллельные миры

import os, sys, io, struct
from PIL import Image
import lzma

NAME = "Trickster Games 2"
FORMATS_ARCHIVE = ['toc', 'ogg', 'ogm']
TYPES_ARCHIVE = [('Trickster Games 2', ('*.toc', '*.ogg', '*.ogm'))]
GAMES = ["Алиса в Стране Чудес",
         "Весёлые картинки - Незнайка идёт в школу",
         "Ералаш Лэнд",
         "Красная Шапочка",
         "Петрович и все все все",
         "Смешарики Параллельные миры"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["dds",
                            "dds_comp",
                            "ogg",
                            "wav"]

        self.sup_types = {"dds":1,
                          "dds_comp":1,
                          "ogg":3,
                          "wav":3}

        self.images = []
        self.sound = None
        self.text = None
        self.dirname = "" # Путь до архивов игры

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "toc":
            self.OpenArchiveTOC(file)

        elif format == "ogg" or format == "ogm":
            self.OpenArchiveBIN(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        archive_number = data_res[4] # Номер архива который надо открыть

        if archive_number == "Нету": # Для архивов ogg и ogm
            self.file.seek(offset)
        else:
            self.file.close() # Закрыть преведущий файл
            # Это сделанно специально чтобы можно было сохранить файл на диск правельно, что бы именно из этого архива считался файл на сохранение
            self.file = open(self.dirname+"\\Resource"+str(archive_number)+".pak", "rb")
            self.file.seek(offset)

        if format == "dds_comp":
            self.Unpack_DDS_COMP(io.BytesIO(self.file.read(size)))

        elif format == "dds":
            self.Unpack_DDS(io.BytesIO(self.file.read(size)))

        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))
            
        elif format == "ogg":
            self.Unpack_OGG(io.BytesIO(self.file.read(size)))

    def OpenArchiveBIN(self,file):
        f = open(file,"rb")
        (dirname, filename) = os.path.split(file) # Достаём имя файла
        # Первый байт ненужен в большенстве файлов

        f.seek(0,2)
        size = f.tell() # Конец файла

        f.seek(58) # Для Петрович и все все все
        check_1 = f.read(4) # Проверка

        f.seek(59)
        check_2 = f.read(4) # Проверка

        if check_1 == b'OggS':
            offset = 0
            tip = "ogg"

        if check_2 == b'OggS':
            tip = "ogg"
            offset = 1
            size -= 1

        else:
            tip = "ogm" # Видео
            offset = 1
            size -= 1

        self.data.append(("1 "+filename, offset, size, tip, "Нету"))
        self.file = f

    def OpenArchiveTOC(self,file):
        self.data = [] # Список файлов

        (dirname, filename) = os.path.split(file) # Достаём путь где лежат архивы
        self.dirname = dirname

        f = open(file,"rb")
        col = struct.unpack("<I",f.read(4))[0] # Количество архивов для распаковки
        col_block = struct.unpack("<I",f.read(4))[0] # Количество таблиц

        for ii in range(col_block):
            f.read(4) # Непонятно Это значение постоянно растёт
            size_block = struct.unpack("<I",f.read(4))[0] # Количетво строчек которые надо прочитать до следующего блока строчек

            for i in range(size_block): # Одна строчка занимает 52 байта
                f.seek(8, 1) # Пропускаем байты для ускорения распаковки
                #unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно
                #unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно Это значение похоже зависит от количество файлов в этом блоке таблицы последний файл в этом блоке будет значится как FF FF FF FF но невсегда иногда меняются значения на другие.
                archive_number = struct.unpack("<I",f.read(4))[0] # Номер архива
                size_unpacked = struct.unpack("<I",f.read(4))[0] # Размер распакованного файла
                size = struct.unpack("<I",f.read(4))[0]   # Размер
                offset = struct.unpack("<I",f.read(4))[0] # Оффсет
                tip = struct.unpack("<I",f.read(4))[0]    # Тип файла
                f.seek(24, 1) # Пропускаем байты для ускорения распаковки
                """
                unclear_4 = struct.unpack("<I",f.read(4))[0] # Ширина картинки, Количество каналов
                unclear_5 = struct.unpack("<I",f.read(4))[0] # Высота картинки, Частота
                unclear_6 = struct.unpack("<I",f.read(4))[0] # Ширина картинки, Битность звука
                unclear_7 = struct.unpack("<I",f.read(4))[0] # Высота картинки, Первая часть размера файла
                unclear_8 = struct.unpack("<I",f.read(4))[0] # Непонятно1  0
                unclear_9 = struct.unpack("<I",f.read(4))[0] # Непонятно0  Вторая часть размера файла
                """

                if tip in [0, 1]: # Открыть проверку файлов если типы равны 0 или 1
                    f2 = open(self.dirname+"\\Resource"+str(archive_number)+".pak", "rb")
                    f2.seek(offset)
                    check_1 = f2.read(4) # Проверка

                if tip == 0:
                    if check_1 == b'RGN0':
                        f_type = "RGN0"

                    else: # Алиса в Стране Чудес, Весёлые картинки - Незнайка идёт в школу
                        f_type = "wav"
                    f2.close()

                elif tip == 1: # Сжатые картинки
                    #f2.seek(offset+1)
                    #check_2 = f2.read(3) # Проверка

                    if check_1 == b'DDS ': # Не сжатые файлы, Весёлые картинки - Незнайка идёт в школу, Ералаш Лэнд, Красная Шапочка
                        f_type = "dds"

                        """
                    elif check_2 == b'DDS': # Петрович и все все все, Смешарики Параллельные миры, Красная Шапочка.
                        #f_type = "dds.hp"
                        f_type = "dds_comp"

                    else: # Ералаш Лэнд, Весёлые картинки - Незнайка идёт в школу, Алиса в Стране Чудес
                        #f_type = "DDS.LZMA"
                        f_type = "dds_comp"
                        """
                    else:
                        f_type = "dds_comp"
                    f2.close()

                elif tip == 2: # Ералаш Лэнд, Красная Шапочка, Петрович и все все все, Смешарики
                    f_type = "wav"

                else: # Непонятные файлы, их нет
                    f_type = "bin"

                self.data.append((str(archive_number)+" "+str(offset)+"."+f_type, offset, size, f_type, str(archive_number)))

        self.file = f

    def Unpack_WAV(self, f):
        try: # Исключения
            f.write(b'RIFF') # Правим заголовок звука wav для Ералаш Лэнд
            self.sound = f
        except :
            print("Не поддерживается")

    def Unpack_OGG(self, f):
        self.sound = f

    def Unpack_DDS_COMP(self, f):
        f.seek(1)
        check = f.read(3) # Проверка

        if check == b'DDS': # Это для Петрович и все все все, Смешарики Параллельные миры, Красная Шапочка. "DDS.hp"
            f2 = io.BytesIO()

            f.seek(0,2)
            end_f = f.tell() # Конец файла
            f.seek(0)

            breaks = f.read(1) # Байтом которым будет отделятся команды

            while f.tell() != end_f: # Остановка когда достигним конца файла.
                f_pos = f.tell()
                byte = f.read(1) # Байт

                if byte == breaks: # Дальше идут сжатые байты
                    byte_repeat = f.read(1) # Байт который будут повторять

                    if byte_repeat == breaks: # Если байт разделитель и байт чтения одинаковый то просто записываем один байт
                        f2.write(byte_repeat) # Запись одного байта

                    else:
                        byte_1 = f.read(1)[0] # Байт количество повторений
                        if byte_1 > 0x80:
                            repeat = byte_1 & 0x7F # Сколько раз повторить байт

                        else: # Если значение байта 0x80 или ниже то число двух байтное
                            repeat = (byte_1 << 8) + f.read(1)[0] # Сколько раз повторить байт

                        f2.write(byte_repeat * repeat)
                else:
                    f2.write(byte) # Запись одного байта

            try: # Исключения
                self.images = [Image.open(f2)]
            except:
                f2.seek(0,2)
                end_f = f2.tell() # Узнаём размер файла

                f2.seek(12)
                h, w = struct.unpack("<II",f2.read(8)) # Ширина и высота

                if 128+((w*h)*4) == end_f: # DDS 32 битный
                    f2.seek(128)
                    self.images = [Image.frombuffer('RGBA', (w,h), f2.read(w*h*4), 'raw', 'BGRA', 0, 1)]
                else:
                    print("Не поддерживается .hp")

        else: # Ералаш Лэнд, Весёлые картинки - Незнайка идёт в школу, Алиса в Стране Чудес. "DDS.LZMA"
            f.seek(0)
            f.read(1) # Непоняоно
            fd_2 = f.read(5) # Настройки, первый байт должен быть 5D
            fd = f.read()
            f.close()

            filter_1 = lzma._decode_filter_properties(lzma.FILTER_LZMA1, fd_2)
            dec = lzma.LZMADecompressor(lzma.FORMAT_RAW, None,[filter_1])
            decompressed_data = dec.decompress(fd) # Распаковка сжатых данных
            f2 = io.BytesIO(decompressed_data)
            try: # Исключения
                self.images = [Image.open(f2)]
            except:
                f2.seek(0,2)
                end_f = f2.tell() # Узнаём размер файла

                f2.seek(12)
                h, w = struct.unpack("<II",f2.read(8)) # Ширина и высота

                # В Алиса после распаковки файла, файл на один байт больше 
                if 128+((w*h)*4) == end_f or 128+((w*h)*4)+1 == end_f: # DDS 32 битный
                    f2.seek(128)
                    self.images = [Image.frombuffer('RGBA', (w,h), f2.read(w*h*4), 'raw', 'BGRA', 0, 1)]
                else:
                    print("Не поддерживается .LZMA")

    def Unpack_DDS(self, f):
        try: # Исключения
            image = Image.open(f)
            self.images = [image]
        except:
            print("Не поддерживается")