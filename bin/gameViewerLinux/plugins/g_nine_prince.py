#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Девять принцев Амбера
# Alex kalumb1@ya.ru
# ZetpeR xax007@yandex.ru

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Девять принцев Амбера"
FORMATS_ARCHIVE = ['dir', 'npa.exe']
TYPES_ARCHIVE = [('Nine prince Pack', ('*.dir','npa.exe'))]
GAMES = ["Девять принцев Амбера"]
AUTHOR = "Alex kalumb1@ya.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["but",
                            "crd",
                            "dat",
                            "flp",
                            "flz",
                            "fnc",
                            "fnt",
                            "lbb",
                            "lic",
                            "sbj",
                            "scn",
                            "see",
                            "spr",
                            "txt",
                            "txt2",
                            "vrn",
                            "wav"]

        self.sup_types = {"but":1,
                          "crd":1,
                          "dat":2,
                          "flp":2,
                          "flz":2,
                          "fnc":2,
                          "fnt":2,
                          "lbb":1,
                          "lic":2,
                          "sbj":1,
                          "scn":2,
                          "see":1,
                          "spr":2,
                          "txt":4,
                          "txt2":4,
                          "vrn":1,
                          "wav":3}

        self.images = []
        self.sound = None
        self.text = [] # Список для текста

    def open_data(self,file):
        (dirname, filename) = os.path.split(file)
        format = file.split(".")[-1].lower()
        if format == "dir":
            self.OpenArchiveDIR(file)
        elif filename.lower() == "npa.exe":
            self.OpenArchiveEXE(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format in ["but", "crd", "lbb", "sbj", "see"]:
            self.Unpack_SBJ_LBB(io.BytesIO(self.file.read(size)))
        elif format == "dat" or format == "flp" :
            self.Unpack_DAT_FLP(io.BytesIO(self.file.read(size)))
        elif format == "flz":
            self.Unpack_FLZ(io.BytesIO(self.file.read(size)))
        elif format == "fnc":
            self.Unpack_FNC(io.BytesIO(self.file.read(size)))
        elif format == "fnt":
            self.Unpack_FNT(io.BytesIO(self.file.read(size)))
        elif format == "lic":
            self.Unpack_LIC(io.BytesIO(self.file.read(size)))
        elif format == "scn":
            self.Unpack_SCN(io.BytesIO(self.file.read(size)))
        elif format == "spr":
            self.Unpack_SPR(io.BytesIO(self.file.read(size)))
        elif format == "txt":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))
        elif format == "txt2":
            self.Unpack_TXT2(io.BytesIO(self.file.read(size)))
        elif format == "vrn":
            self.Unpack_VRN(io.BytesIO(self.file.read(size)))
        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))

    def OpenArchiveDIR(self,file):
        self.data = [] # Список файлов
        p,f = os.path.split(file)
        arch = p+"\\"+f[:-3]+"vol"
        if not os.path.exists(arch):
            raise Exception("Файл {} не найден".format(arch))

        f = open(file,"rb")
        head = f.read(30)
        if head != b"Saturn Volume-File Format v1.0":
            raise Exception("Это не архив!")

        unclear_1 = struct.unpack("B",f.read(1))[0] # Непонятно
        unclear_2 = struct.unpack("B",f.read(1))[0] # Непонятно
        col_files = struct.unpack("<I",f.read(4))[0] # Количество файлов

        for i in range(col_files):
            decode = bytearray(f.read(16))
            v5 = decode[12]

            for j in range(8): # Это расшифровка имени
                decode[j] ^= v5
                decode[j] -= j

            for j in range(3): # Это расшифровка типа файла
                decode[8+j] ^= v5
                decode[8+j] -= j

            name = decode[:8].split(b"\x00")[0].decode("utf8")
            format = decode[8:11].decode("utf8")
            size = struct.unpack("<I",f.read(4))[0]
            offset = struct.unpack("<I",f.read(4))[0]
            self.data.append((name+"."+format,offset,size,format.lower()))
        f.close()

        self.file = open(arch,"rb")
        return 1

    def OpenArchiveEXE(self,file):
        f = open(file,"rb")
        self.data.append(("1.txt2",0,652280,"txt2"))
        self.file = f

    def Unpack_SBJ_LBB(self,f):
        w,h = struct.unpack("HH",f.read(4))
        self.images.append(Image.frombuffer('RGB', (w,h), f.read(w*h*2), 'raw', 'BGR;16', 0, 1))

    def Unpack_DAT_FLP(self,f):
        f.seek(0,2)
        end_f = f.tell()
        f.seek(0)

        # Файл ANIM1.DAT он внутри как FLP
        size_f = struct.unpack("<I",f.read(4))[0]  # Размер файла
        if size_f == end_f: # Проверка на анимацию FLP
            w,h = struct.unpack("<HH",f.read(4))       # Ширина и высота
            col_ani = struct.unpack("<H",f.read(2))[0] # Количество кадров
            offset = struct.unpack("<I",f.read(4))[0]  # Оффсет в конца байтов наложения,  
            # В конце файла на каждый кадр выделено 404 байт 
            #print("Оффсет",offset)

        else: # Анимация DAT
            f.seek(0)
            col_ani = struct.unpack("<H",f.read(2))[0] # Количество кадров
            w,h = struct.unpack("<HH",f.read(4))       # Ширина и высота
            #size_all = 0 # Общий размер данных
            for i in range(col_ani):
                # Первый размер это размер картинки
                # Второй и последующие это размер кадров наложения данных
                size = struct.unpack("<I",f.read(4))[0] # Размер
                #size_all += size
                #print("Размеры наложения", "%6d" %size)
            #print("Общий размер данных",size_all,"Позиция начало файла",f.tell())

        #print(w,h,"Количество кадров",col_ani)
        fd = f.read((w*h)*2)
        end_pic = f.tell()
        #print("Конец картинки",end_pic)
        buffer_pic = io.BytesIO(fd) # Нужно для распакованной картинки и для наложения анимации

        self.images.append(Image.frombuffer('RGB', (w,h), buffer_pic.read(w*h*2), 'raw', 'BGR;16', 0, 1))

        end_ani = end_f-(col_ani*404) # Узнаём конец наложения, на каждый кадр выделено 404 байт в конце файла
        size = end_ani-end_pic # Размер байтов наложения на картинку

        fd = f.read(size)
        f2 = io.BytesIO(fd)
        self.Unpack_ANI(w,h,buffer_pic,f2,col_ani)
        f.close()
        f2.close()
        buffer_pic.close()

    def Unpack_FLZ(self,f):
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)
        data = [] # Список
        col = struct.unpack("<H",f.read(2))[0] # Количество картинок и анимаций
        w,h = struct.unpack("<HH",f.read(4)) # Ширина и высота
        size = struct.unpack("<I",f.read(4))[0] # Первый размер это размер картинки
        #print("Высота и ширина",w,h,"Размер распакованной картинки",size)
        for i in range(col-1):
            unclear = struct.unpack("<I",f.read(4))[0] # Размер кадров наложения данных 
            data.append(unclear)
            #print("Размеры наложения", "%6d" %unclear)

        if end_f == 245760: # Если размер файла равен файлу B22.FLZ
            fd = f.read(242207) # Читаем правельный размер файла сжатия comp
            #fd2 = f.read(3139) # Непонятные байты
        else:
            fd = f.read()   

        f.close()
        f3 = io.BytesIO(fd)
        f2 = self.Unpack_comp(f3) # Распаковка сжатия

        fd = f2.read((w*h)*2)
        buffer_pic = io.BytesIO(fd) # Нужно для распакованной картинки и для наложения анимации
        self.images.append(Image.frombuffer('RGB', (w,h), buffer_pic.read(w*h*2), 'raw', 'BGR;16', 0, 1))

        for i in data:
            if i == 2:
                f2.read(2) # Читаем 2 байта
            else:
                self.Unpack_ANI(w,h,buffer_pic,f2,2)

    def Unpack_FNC(self,f):
        type = f.read(4)
        if type != b'FCL\x00': # Проверка на картинку FCL.
            print("ЭТО НЕ картика",type)
            return(0)
        col = struct.unpack("<I",f.read(4))[0] # Количество картинок
        w = struct.unpack("<I",f.read(4))[0] # Ширина
        h = struct.unpack("<I",f.read(4))[0] # Высота
        f.read(2048) # Непонятно читается по 4 байта

        for i in range(col):
            w,h = struct.unpack("HH",f.read(4)) # Ширина и высота
            self.images.append(Image.frombuffer('RGB', (w,h), f.read(w*h*2), 'raw', 'BGR;16', 0, 1))

    def Unpack_FNT(self,f):
        type = f.read(4) # Тип
        if type != b'\x4D\x4B\x4C\x08': # Проверка на шрифт
            print("ЭТО НЕ ШРИФТ",type)
            return(0)
        w = 8
        h = 16
        Pal = [(255,255,255,00),(128,132,128,255)]
        unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_2 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_3 = struct.unpack("B",f.read(1))[0] # Непонятно
        for i in range(256):
            rgb = []
            for j in range(w*h):
                fd = struct.unpack("B",f.read(1))[0]
                rgb.extend(Pal[fd])
            rgb = np.array(rgb,np.uint8).reshape(h, w, 4)
            self.images.append(Image.fromarray(rgb,"RGBA"))

    def Unpack_LIC(self,f):
        data2 = [] # Список файлов
        col = struct.unpack("<H",f.read(2))[0] # Количество картинок
        for i in range(col):
            f_path = f.read(13) # Имя картинки
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            unclear = struct.unpack("<I",f.read(4))[0] # Непонятно номер картинки ?
            data2.append(offset)

        for i in data2:
            f.seek(i)
            w,h = struct.unpack("HH",f.read(4)) # Ширина и высота
            self.images.append(Image.frombuffer('RGB', (w,h), f.read(w*h*2), 'raw', 'BGR;16', 0, 1))

    def Unpack_SCN(self, f):
        f.seek(0,2)
        end_f = f.tell()
        f.seek(0)
        type = f.read(32) # Тип архива
        if type != b'Saturn Scenas-File Format v1.0\x00\x00': # Проверка на архив
            print("ЭТО НЕ АРХИВ",type)
            return(0) 

        col = struct.unpack("<H",f.read(2))[0] # Количество блоков в начеле которое надо прочетать
        # Это скорей всего относится только к первой картинки фона в файле SCN4_07.SCN есть только фон, без дополнительных картинок
        for i in range(col): # Читаем блоки по 7 байт если они есть
            unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_2 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_3 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_4 = struct.unpack("B",f.read(1))[0]  # Непонятно
            #print("Данные о блоках",unclear_1,unclear_2,unclear_3,unclear_4)

        #print()
        # Всего читается 12 байт
        posf = f.tell()
        unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_2 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_3 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_4 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_5 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_6 = struct.unpack("<H",f.read(2))[0] # Непонятно
        #print("Непонятно",unclear_1,unclear_2,unclear_3,unclear_4,unclear_5,unclear_6,"Позиция байт",posf)

        offset_background = struct.unpack("<I",f.read(4))[0] # Оффсет сжатого фона 
        offset_tab = struct.unpack("<I",f.read(4))[0] # Оффсет ссылается на таблицу с файлами картинок
        offset_file_end = struct.unpack("<I",f.read(4))[0] # Оффсет одного файла в конце файла, может не быть 
        size_blok = struct.unpack("<I",f.read(4))[0] # Размер первой сжатой картинки
        zero = struct.unpack("B",f.read(1))[0] # Всегда 00
        #print("Оффсет сжатого фона",offset_background,"Оффсет таблицы файлов картинок",offset_tab)
        #print("Оффсет файла в конце",offset_file_end,"Размер первой сжатой картинки фона",size_blok,zero)

        offset_posf = f.tell() # Позиция сжатой картинки
        fd = f.read(size_blok)

        w = 560
        h = 360
        f3 = io.BytesIO(fd)
        buffer_pic = self.Unpack_comp(f3) # Нужно для распакованной картинки
        f3.close()

        self.images.append(Image.frombuffer('RGB', (w,h), buffer_pic.read(w*h*2), 'raw', 'BGR;16', 0, 1))
        #print("Конец данных сжатых первой картинки фона",f.tell(),"\n")

        """
        # Читаем непонятные данные после сжатой картинки
        col_blok = struct.unpack("<H",f.read(2))[0] # Повторить непонятных блоков с данными
        for i in range(col_blok):
            col_u = struct.unpack("<H",f.read(2))[0] # Количество повторений по 4 байта
            for i in range(col_u):
                byte = f.read(4) # Скорей всего читается по 2 байта возможно даже это флот с плавающей точкой
        posf_blok = f.tell()
        """
        ##################
        data = [] # Список оффсетов на файлы
        f.seek(offset_tab) # Оффсет таблицы
        col2 = struct.unpack("B",f.read(1))[0] # Количество файлов
        for i in range(col2):
            offset = struct.unpack("<I",f.read(4))[0] + offset_tab # Оффсет
            data.append(offset)
            #print("Оффсет файлов картинки",offset)

        if end_f != offset_file_end+2: # Если оффсет конечного файла неравен концу файла то значит в конце есть конечный файл с картинками
            data.append(offset_file_end) # Добавляем оффсет конечного файла с картинками

        #print()
        block = 0 # Номер блока со сжатыми файлами

        for offset_i in data:
            f.seek(offset_i)
            col_block_pictures = struct.unpack("B",f.read(1))[0] # Количество файлов блоков с картинками дальше
            #print("Блоков с картинками",col_block_pictures,"Оффсет блока с картинками",offset_i)   

            for i2 in range(col_block_pictures):
                #if i2 > 0:
                    #print("    Распаковка дополнительного блока",i2+1,"на",f.tell())

                # Это сделанно специально чтоб прочетать конецный файл если он есть
                if offset_i == offset_file_end: # Если есть конецный файл в .SCN
                    f.read(1) # Читает один лишний байт, а потом как нормальную картинку
                    #print("Чтение последнего файла на",offset_file_end)

                else: # Это для нормальных картинок
                    coordinates_h, coordinates_w = struct.unpack("<HH",f.read(4)) # 2 байта координаты картинки по ширине экрана, 2 байта координаты картинки по высоте экрана

                col_ani = struct.unpack("<H",f.read(2))[0] # Количество кадров
                w,h = struct.unpack("<HH",f.read(4)) # Ширина и высота
                decompSize_1 = struct.unpack("<I",f.read(4))[0] # Размер распакованной картинки
                #print("Количество картинок+кадры",col_ani,"Высота и ширина картинки",w,h)
                #print("Размер распакованной картинки",decompSize_1)

                if col_ani-1 > 0: # Есть второй сжатый файл с наложениями на картинку
                    decompSize_2 = 0 # Размер распакованного наложения сжатого файла 2 целиком
                    for i in range(col_ani-1):
                        size_frame = struct.unpack("<I",f.read(4))[0] # Распакованный размер кадра наложения на картинку
                        decompSize_2 += size_frame
                        #print("Кадр",i+1,size_frame)
                    #print("Количество кадров наложения",col_ani-1)
                    #print("Размер распакованного второго файла с наложениями",decompSize_2)

                size_1 = struct.unpack("<I",f.read(4))[0] # Размер первых сжатых данных картинки
                zero1 = struct.unpack("B",f.read(1))[0] # Всегда 00
                size_2 = struct.unpack("<I",f.read(4))[0] # Размер вторых сжатых данных наложения
                # Если записанн размер 03 00 00 00 значи второго сжатого файла нет
                zero2 = struct.unpack("B",f.read(1))[0] # Всегда 00

                block += 1
                stroka = str(block)+" Ширина и высота "+str(w)+" "+str(h)+" Размер без сжатия "+str(decompSize_1)

                offset_posf = f.tell() # Позиция сжатой картинки
                fd = f.read(size_1)     

                f3 = io.BytesIO(fd)
                buffer_pic = self.Unpack_comp(f3) # Нужно для распакованной картинки и для наложения анимации
                f3.close()

                self.images.append(Image.frombuffer('RGB', (w,h), buffer_pic.read(w*h*2), 'raw', 'BGR;16', 0, 1))

                if col_ani-1 > 0:
                    stroka = str(block)+" Размер без сжатия "+str(decompSize_2)

                    offset_posf = f.tell() # Позиция сжатой наложений на картинку
                    fd = f.read(size_2)

                    f3 = io.BytesIO(fd)
                    f2 = self.Unpack_comp(f3) # Нужно для распакованной картинки и для наложения анимации
                    f3.close()
                    ss = 1
                    self.Unpack_ANI(w,h,buffer_pic,f2,col_ani)
                    buffer_pic.close()

                #print("Конец сжатых данных картинок и наложений",f.tell())

                # Читаем непонятные данные в конце файла и ищем начало нового блока
                while True:
                    posf_blok = f.tell() # Для перехода на начало картинки
                    if posf_blok == end_f: # Если достигли конца файла останавливаемся
                        #print("Конец файла .SCN")
                        break

                    col_u = struct.unpack("B",f.read(1))[0] # Количество повторений по 4 байта
                    check = struct.unpack("B",f.read(1))[0] # Проверка Должен быть 00
                    #print("  Позиция",posf_blok,"Число",col_u,check)

                    # Это повторить раз 4 байта
                    if col_u in [0,3,4,5,6] and check == 0: # 00 00, 03 00, 04 00, 05 00, 06 00
                        for i in range(col_u):
                            byte = f.read(4) # Скорей всего читается по 2 байта возможно даже это флот с плавающей точкой

                    elif col_u == 88 and check == 0 : # 58 00 FF
                        byte = f.read(1) # Читается  1 байт

                    # Если дальше идёт новый файл с картинками в следующем файле могут быть блоки 2 или 8
                    # SCENA08.SCN там есть 8 блоков с картинками
                    elif col_u in [1,2,8]: # Это начало файла с картинками
                        #print("    Позиция начало файла с картинками",posf_blok,"Число",col_u,"  ",check)
                        f.seek(posf_blok) # Если нашли начало файла картинки
                        break # Преравает цикл

                    elif col_block_pictures == 1: # Это скорей всего ошибка так как в блоке нет друних картинок и следующий файл будет начинатся с 1 или 2 или 8
                        print("  НЕПОНЯТНО ПРОВЕРИТЬ1",col_u,check)
                        print(offset_i,data) # для теста потом удалить
                        exit(0)

                    elif col_block_pictures >= 2: # Тут скорей всего начало втого блока с картинками
                        #print("  НЕПОНЯТНО ПРОВЕРИТЬ2",col_u,check)
                        #print("  ТУТ СКОРЕЙ НАЧАЛО ВТОРОГО БЛОКА С КАРТИНКАМИ",posf_blok,"Номер блока",block + 1,"\n")
                        f.seek(posf_blok) # Нашли начало втого файла картинки
                        break

                    else: # Ошибка
                        print("  НЕПОНЯТНО ПРОВЕРИТЬ3",col_u,check)
                        exit(0)
            print()
        f.close()

    def Unpack_SPR(self, f):
        data = [] # Список файлов
        col = struct.unpack("<H",f.read(2))[0] # Количество сжатых файлов
        #print("Количество сжатых файлов",col)
        for i in range(col):
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            unclear_1 = struct.unpack("<I",f.read(4))[0] # Всегда нули
            size = struct.unpack("<I",f.read(4))[0] # Размер сжатых данных
            size_Unpack = struct.unpack("<I",f.read(4))[0] # Размер распакованных данных
            data.append((i,offset,size))
            #print("Оффсет %7d" %offset,"Непонятно",unclear_1,"размер сжатого файла%7d" %size)
            #print("Размер распакованного файла%7d" %size_Unpack,"\n")

        for i in data:
            f.seek(i[1])
            fd = f.read(i[2])

            f2 = io.BytesIO(fd)
            f3 = self.Unpack_comp(f2) # Нужно для распакованной
            # Новые распакованные файлы назвал .sprf
            self.Unpack_SPRF(f3) # Чтение файла .sprf
            f3.close()
        f.close()

    def Unpack_SPRF(self, f):
        data = [] # Список таблиц
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)
        col = struct.unpack("<H",f.read(2))[0] # Количество оффсетов на таблицы
        #print("Количество оффсетов на таблицы",col)

        for i in range(col):
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет на таблицы
            data.append(offset)
        #print("Офсеты на таблицы",data,"\n")

        data3 = [] # Список всех файлов для расчёта размера файлов наложений

        blok = 0
        for ioffset in data:
            data3.append((ioffset,0,0,0)) # Добавляем оффсет таблицы для расчёта размера файла
            blok += 1
            #data2 = [] # Список файлов
            f.seek(ioffset) # Переход на таблицу
            col_f = struct.unpack("<H",f.read(2))[0] # Количество файлов в таблице
            w = struct.unpack("<H",f.read(2))[0] # Ширина картинки
            h = struct.unpack("<H",f.read(2))[0] # Высота картинки
            unclear_3 = struct.unpack("<H",f.read(2))[0] # Непонятно
            #print("Оффсет таблицы",ioffset,"Количество файлов",col_f)
            #print("Ширина и высота картинки",w,h,"Непонятно",unclear_3)

            for i in range(col_f):
                offset = struct.unpack("<I",f.read(4))[0] + ioffset # Оффсет на файлы
                #data2.append(offset)
                data3.append((offset,w,h,blok))
            #print("Оффсеты на файлы",data2)
            #print("###############\n")

        data3.append((end_f,0,0,0)) # Добавляем конец файла для правельного расчёта последнего файла

        # Расчёт размера файла
        #print(data3,"\n")
        #print("Расчёт размера файла")
        data4 = [] # Список всех файлов с размерами
        for i in range(len(data3)):
            if data3[i][3] > 0: # Если записанно номер блока расчитать размер файла если нет то это начало таблиц или конец файла
                size = data3[i+1][0]-data3[i][0]
                data4.append((data3[i][0], size, data3[i][1], data3[i][2], data3[i][3]))
                #print(data3[i][0],data3[i][1],data3[i][2],data3[i][3],size)

        for i in data4:
            f.seek(i[0])
            fd = f.read(i[1])
            # Новые распакованные файлы назвал .ani

            # Распаковка кадров .ani
            f3 = io.BytesIO(fd) # Загружаем файл в память Для быстрой работы
            f3.seek(0,2)
            end_f = f3.tell() # Конец файла
            f3.seek(0)

            unclear_1 = struct.unpack("<H",f3.read(2))[0] # Непонятно
            unclear_2 = struct.unpack("<H",f3.read(2))[0] # Непонятно
            #print("Непонятно",unclear_1,unclear_2)

            f2 = io.BytesIO()
            while True:
                check = f3.read(1)[0] # Действие
                #print("Действие",check,"позиция",f3.tell()-1)

                if check >= 0xC0: # Просто читает цвета
                    col = check - 0xC0 # Сколько прочетать цветов
                    fd = f3.read(col*2)
                    f2.write(fd)
                    #print("Прочетать цветов",col)

                elif check >= 0x80: # Повторить два следующих байта
                    col = check - 0x80
                    fd = f3.read(2) # Читаем цвет
                    f2.write(fd*col)
                    #print("Повторить 2 байта цвета",col)

                elif check <= 0x7F and check != 0: # Повторить байты прозрачности
                    #print("Повторить байты прозрачности раз",check)
                    byte = b'\xC0\x07' # Байты прозрачности Ядовитый зелёный цвет
                    fd = byte*(check)
                    f2.write(fd)

                elif check == 0 and f3.tell() == end_f:
                    #print("Конец файла")
                    break

                else:
                    print("ОШИБКА %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                    break
                #print()

            f2.seek(0)
            w = i[2]
            h = i[3]
            self.images.append(Image.frombuffer('RGB', (w,h), f2.read(w*h*2), 'raw', 'BGR;16', 0, 1))
            f2.close()
            f3.close()

        f.close()

    def Unpack_TXT(self, f): 
        self.text = f.read().decode("cp866")

    def Unpack_TXT2(self, f):
        def read_txt(col): # Читает строчки
            for i in range(col):
                text0 = txt.readline() # Так читает одну строчку
                self.text.append(text0) # Добавляем строчку

        def skip_txt(col_2): # Пропустить строчек
            for i in range(col_2):
                txt.readline() # Читаем в постоту строчку

        f.seek(0,2)
        end_f = f.tell() # Конец файла

        # Читаем английский текст
        f.seek(0)
        txt = io.StringIO() # Виртуальный файл для текста
        line_text = b'' # Строчка с текстом из байтов
        for i in range(end_f):
            bait = f.read(1) # Байт 
            if bait[0] >= 32 and bait[0] <= 126: # bait[0] != неправельный байт или байты and
                line_text += bait # Прибавляем байт
            else:
                if line_text != b'': # Если текст не равен пустой строчки то это строчка
                    if len(line_text) > 5: # Тут можно указать длину менемум строчки
                        line_w = line_text.decode("ascii") # Декодирвуем текст
                        #print("Строчка",line_w)
                        txt.write(line_w+"\n")
                    line_text = b''

        txt.seek(0) # Переход на начало текста

        read_txt(6) # Читаем строчки
        skip_txt(1046) # Пропускаем строчки
        read_txt(1)
        skip_txt(57)
        read_txt(1291)
        txt.close()

        # Читаем руссский текст
        f.seek(0)
        txt = io.StringIO() # Виртуальный файл для текста
        line_text = b'' # Строчка с текстом из байтов
        for i in range(end_f):
            bait = f.read(1) # Байт 
            if bait[0] >= 128 and bait[0] <= 239 or bait[0] in [0x20,0x21,0x25,0x2C,0x2D,0x2E]: #
            # в [0x20,0x21,0x25,0x2C,0x2D,0x2E] записаны байты которые добавить в текст
                line_text += bait # Прибавляем байт
            else:
                if line_text != b'': # Если текст не равен пустой строчки то это строчка
                    if len(line_text) > 4: # Тут можно указать длину менемум строчки 5
                        line_w = line_text.decode("cp866") # Декодирвуем текст
                        #print("Строчка",line_w)
                        txt.write(line_w+"\n")
                    line_text = b''

        txt.seek(0) # Переход на начало текста

        skip_txt(883) # Пропускаем строчки
        read_txt(97) # Читаем строчки
        txt.close()
        f.close()

    def Unpack_VRN(self,f):
        w = 560
        h = 360
        rgb = np.frombuffer(f.read(w*h*4), dtype = np.uint8)
        rgb = np.array(rgb,np.uint8).reshape(h, w, 4)
        r,g,b,a = np.rollaxis(rgb, axis = -1)
        rgb = np.dstack([r,g,b]) # Специально записанно без a чтоб можно было увидеть картинку 
        self.images.append(Image.fromarray(rgb,"RGB"))

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_ANI(self,w,h,buffer_pic,f2,col_ani):
        for i in range(col_ani-1): # Количество кадров которое прочитать
            ss2 = 0     # Номер строки
            offset = 0  # На каком оффсете начало строчки находимся
            changed = 0 # Количество прочинанных изменёных строк
            col = struct.unpack("<H",f2.read(2))[0] # Количество изменённых строчек
            #print("Количество изменённых строчек",col,f2.tell()-2)

            while True:
                offset = w*ss2
                if changed == col: # Конец чтения линии в ширину
                    break
                number_command = f2.read(1)[0] # Количество на одну строчку в ширену
                unclear2 = f2.read(1)[0] # Номеру строки с которой начать
                if unclear2 == 128 or unclear2 == 129: # Если байт 128(80 hex)
                    #print("Байта 80 или 81 пропустить от начало",number_command,f2.tell()-2)
                    ss2 += number_command + (unclear2-128) # Прибавляем к номеру строки с которой начать
                    continue

                elif unclear2 > 0:
                    print("   ОШИБКА Непонятная команда",unclear2,f2.tell()-2,"%%%%%")
                    return(0)

                #print("Количество команд позиция",number_command,unclear2,f2.tell()-2)
                for i in range(number_command):
                    line_number = f2.read(1)[0] # Количество байт *2 на которое надо от ступить от начало строчки чтоб записать новую строчку
                    line_b = f2.read(1)[0] # Сколько прочетать байт *2
                    fd = f2.read(line_b*2)
                    #print("Номер строчки в байтах",ss2,offset,"Прибавить",line_number,"Сколько прочетать",line_b,"Позиция",f2.tell())

                    offset += line_number # 
                    buffer_pic.seek(offset*2) # Начало записи байтов наложения
                    buffer_pic.write(fd)
                    offset += line_b # Прибавить прочитанные данные
                ss2 += 1
                changed += 1 # Прочетали изменёную строку
                #print("Количество изменёных строк",changed)
            buffer_pic.seek(0)

            self.images.append(Image.frombuffer('RGB', (w,h), buffer_pic.read(w*h*2), 'raw', 'BGR;16', 0, 1))

    def Unpack_comp(self,f):
        fd = f.read()
        end_f = f.tell()
        f.close()
        f = iter(fd) # Итерация

        out = bytearray() # Распакованные данные

        # main_number главное число # BIT Потоковый накопитель бит
        main_number = next(f) | (next(f)<<8) # Читаем управляющие байты получаем число
        col_bit = 16 # Количество бит в данный момент

        while True: # Проверка управляющих бит
            # Придётся делать две проверки на число и сколько доступно бит в байт
            if main_number & 0b11 == 0b10 and col_bit >= 2: # Больше или равно двум битам
                main_number >>= 2 # Битовый сдвиг
                col_bit -= 2 # Удаляем количество прочитанных бит

                if col_bit == 0: # Пусто читаем управляющие байты
                    main_number = next(f) | (next(f)<<8) # Читаем управляющие байты получаем число
                    col_bit = 16
                    # Это нужно здесь чтобы правильно прочитать следующий байт

                out.append(next(f))
                continue # Продолжить сначало цикла

            elif main_number & 0b11 == 0b01 and col_bit >= 2: # БИТЫ 01 чтение 2 байт
                read_bytes = 2 # Сколько прочетать байтов
                del_bits = 2 # Делаем битовый сдвиг и удаляем количество прочитанных бит

            elif main_number & 0b11 == 0b11 and col_bit >= 2: # БИТЫ 11 чтение 3 байт
                read_bytes = 3
                del_bits = 2

            elif main_number & 0b1111 == 0b0000 and col_bit >= 4: # БИТЫ 00 00 чтение 4 байт
                read_bytes = 4
                del_bits = 4

            elif main_number & 0b11111 == 0b00100 and col_bit >= 5: # БИТЫ 0 01 00 чтение 5 байт
                read_bytes = 5
                del_bits = 5

            elif main_number & 0b11111 == 0b10100 and col_bit >= 5: # БИТЫ 1 01 00 чтение 6 байт
                read_bytes = 6
                del_bits = 5

            elif main_number & 0b11111 == 0b01100 and col_bit >= 5: # БИТЫ 0 11 00 чтение 7 байт
                read_bytes = 7
                del_bits = 5

            elif main_number & 0b111111 == 0b011100 and col_bit >= 6: # БИТЫ 01 11 00 чтение 8 байт
                read_bytes = 8
                del_bits = 6

            elif main_number & 0b111111 == 0b111100 and col_bit >= 6: # БИТЫ 11 11 00 чтение 9 байт
                read_bytes = 9
                del_bits = 6

            elif main_number & 0b111111 == 0b111000 and col_bit >= 6: # БИТЫ 11 10 00 чтение 10 байт
                read_bytes = 10
                del_bits = 6

            elif main_number & 0b1111111 == 0b0001000 and col_bit >= 7: # БИТЫ 0 00 10 00 чтение 11 байт
                read_bytes = 11
                del_bits = 7

            elif main_number & 0b1111111 == 0b1001000 and col_bit >= 7: # БИТЫ 1 00 10 00 чтение 12 байт
                read_bytes = 12
                del_bits = 7

            elif main_number & 0b1111111 == 0b0101000 and col_bit >= 7: # БИТЫ 0 10 10 00 чтение 13 байт
                read_bytes = 13
                del_bits = 7

            elif main_number & 0b1111111 == 0b1101000 and col_bit >= 7: # БИТЫ 1 10 10 00 чтение 14 байт
                read_bytes = 14
                del_bits = 7

            elif main_number & 0b1111111 == 0b0011000 and col_bit >= 7: # БИТЫ 0 01 10 00 чтение 15 байт
                read_bytes = 15
                del_bits = 7

            elif main_number & 0b1111111 == 0b1011000 and col_bit >= 7: # БИТЫ 1 01 10 00 чтение 16 байт + col
                if col_bit == 7: # Пусто читаем управляющие байты
                #if main_number & 0b1111111 == 0b1011000 and col_bit == 7: # Пусто читаем управляющие байты
                    main_number = ((next(f) | (next(f)<<8))<<col_bit) # Читаем управляющие байты получаем число
                    col_bit += 16 # Увеличиваем количество бит
                    # Это нужно здесь чтобы правильно прочитать следующий байт

                read_bytes = 16 + next(f) # Сколько прочетать байтов, может писатся как FE
                if read_bytes == 271: # Это конец сжатого файла, этот байт FF.
                    break
                del_bits = 7

            else: # Нехватает бит для индефикации
                # Делаем битовый сдвиг влево на столько бит сколько унас есть <<col_bit
                main_number = ((next(f) | (next(f)<<8))<<col_bit) + main_number # Читаем управляющие байты получаем число
                col_bit += 16 # Увеличиваем количество бит
                continue # Продолжить сначало цикла



            # Удаляем использованный биты
            main_number >>= del_bits # Битовый сдвиг
            col_bit -= del_bits # Удаляем количество прочитанных бит

            if col_bit == 0: # Пусто читаем управляющие байты
                main_number = next(f) | (next(f)<<8) # Читаем управляющие байты получаем число
                col_bit = 16


            # Тут узнаём насколько отойти назад чтобы прочитать байты
            while True: # Узнаём насколько отойти назад влево надо
                if main_number & 0b11 == 0b11 and col_bit >= 2: # Биты 11
                    Back_left = 1 # 0 # Насколько отойти назад влево
                    del_bits = 2 # Сколько удалить битов

                elif main_number & 0b111 == 0b001 and col_bit >= 3: # Биты 0 01
                    Back_left = 257 # 256
                    del_bits = 3

                elif main_number & 0b111 == 0b101 and col_bit >= 3: # Биты 1 01
                    Back_left = 513 # 512
                    del_bits = 3

                elif main_number & 0b1111 == 0b0000 and col_bit >= 4: # Биты 00 00
                    Back_left = 769 # 768
                    del_bits = 4

                elif main_number & 0b1111 == 0b1000 and col_bit >= 4: # Биты 10 00
                    Back_left = 1025 # 1024
                    del_bits = 4

                elif main_number & 0b1111 == 0b0100 and col_bit >= 4: # Биты 01 00
                    Back_left = 1281 # 1280
                    del_bits = 4

                # Оптимизация если бит будет меньше 5 то не проверяем дальше биты а сразу читаем управляющие байты
                # За счёт этого скорость распаковки уменьшеается
                # Если поставить выше на 3, 4 то скорость только упадёт
                elif col_bit < 5: # Дальше меньше чем нужно бит для сравнения
                    main_number = ((next(f) | (next(f)<<8))<<col_bit) + main_number # Читаем управляющие байты получаем число
                    col_bit += 16 # Увеличиваем количество бит
                    continue # Продолжить сначало цикла

                elif main_number & 0b11111 == 0b01100 and col_bit >= 5: # Биты 0 11 00
                    Back_left = 1537 # 1536
                    del_bits = 5

                elif main_number & 0b11111 == 0b11100 and col_bit >= 5: # Биты 1 11 00
                    Back_left = 1793 # 1792
                    del_bits = 5

                elif main_number & 0b11111 == 0b00010 and col_bit >= 5: # Биты 0 00 10
                    Back_left = 2049 # 2048
                    del_bits = 5

                elif main_number & 0b11111 == 0b10010 and col_bit >= 5: # Биты 1 00 10
                    Back_left = 2305 # 2304
                    del_bits = 5

                elif main_number & 0b11111 == 0b01010 and col_bit >= 5: # Биты 0 10 10
                    Back_left = 2561 # 2560
                    del_bits = 5

                elif main_number & 0b11111 == 0b11010 and col_bit >= 5: # Биты 1 10 10
                    Back_left = 2817 # 2816
                    del_bits = 5 

                elif main_number & 0b11111 == 0b00110 and col_bit >= 5: # Биты 0 01 10
                    Back_left = 3073 # 3072
                    del_bits = 5

                elif main_number & 0b11111 == 0b10110 and col_bit >= 5: # Биты 1 01 10
                    Back_left = 3329 # 3328
                    del_bits = 5

                elif main_number & 0b11111 == 0b01110 and col_bit >= 5: # Биты 0 11 10
                    Back_left = 3585 # 3584
                    del_bits = 5

                elif main_number & 0b11111 == 0b11110 and col_bit >= 5: # Биты 1 11 10
                    Back_left = 3841 # 3840 # Насколько отойти назад влево
                    del_bits = 5 # Сколько удалить битов

                else:
                    main_number = ((next(f) | (next(f)<<8))<<col_bit) + main_number # Читаем управляющие байты получаем число
                    col_bit += 16 # Увеличиваем количество бит
                    continue # Продолжить сначало цикла

                break

            # Удаляем использованный биты
            main_number >>= del_bits # Битовый сдвиг
            col_bit -= del_bits # Удаляем количество прочитанных бит

            if col_bit == 0: # Пусто читаем управляющие байты
                main_number = next(f) | (next(f)<<8) # Читаем управляющие байты получаем число
                col_bit = 16

            #print("Насколько отойти назад влево",Back_left)
            # 1 байт читается насколько отойти назад

            # Для ускорения # Время распаковки 9.750 sec
            offset = len(out) - (next(f)+Back_left) # Оффсет чтения байт + насколько отойти назад
            # Увеличил скорость за счёт того что +1 добавил не к строчки кода а в писал в числа заместо 256 теперь стоит 257

            len_byte = len(out) - offset # Получаем количество байт доступное с конца файла

            if len_byte >= read_bytes: # Если количество байт в конце файла больше чем нужно надо взять, просто читаем нужное число байт сразу
                out.extend(out[offset:offset+read_bytes]) # Записываем в выходной файл последовательность байт

            else:
                # Время распаковки 9.937 sec   9.750 sec
                for i in range(offset, offset+read_bytes):
                    out.append(out[i]) # Читаем 1 байт по оффсету и записываем его в конец

        f2 = io.BytesIO(out)
        return(f2)