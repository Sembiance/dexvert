#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Год Зайца

import os, sys
import struct
import pygame
import io
from PIL import Image, ImageTk
import numpy as np
import array

NAME = "Год Зайца"
FORMATS_ARCHIVE = ['scr', 'snd', 'res', 'dll', 'dat', 'flm', 'exe']
TYPES_ARCHIVE = [('Год Зайца', ('*.scr', '*.snd', '*.res', '*.dll', '*.dat', '*.flm', '*.exe'))]
GAMES = ["Год Зайца"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["wav",
                            "bmp",
                            "pic",
                            "anm",
                            "pic_2"]

        self.sup_types = {"wav":3,
                          "bmp":1,
                          "pic":1,
                          "anm":2,
                          "pic_2":1}
        self.images = []
        self.sound = None
        self.Pal = "" # Для палитры
        self.fwav = io.BytesIO() # Соединенные звуки
        self.f_img = "" # Пуская картинка что бы создать картинку с нужными параметрами ширины и высоты

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        (dirname, filename) = os.path.split(file)
        if format == "scr":
            self.OpenArchiveSCR(file,filename)
        elif format == "snd":
            self.OpenArchiveSND(file,filename)
        elif format == "res":
            self.OpenArchiveRES(file,filename)
        elif format in ["dll", "dat", "exe"]:
            self.OpenArchiveDLL(file,filename)
        elif format == "flm":
            self.OpenArchiveFLM(file,filename)

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
        elif format == "bmp":
            self.Unpack_BMP(io.BytesIO(self.file.read(size)))
        elif format == "pic":
            self.ConvertPIC(io.BytesIO(self.file.read(size)),data_res[4],data_res[5])
        elif format == "anm":
            self.Unpack_ANM(io.BytesIO(self.file.read(size)))
        elif format == "pic_2":
            self.ConvertPIC_2(io.BytesIO(self.file.read(size)))

    def OpenArchiveSCR(self,file,filename):
        f = open(file,"rb")
        f.seek(0,2)
        size = f.tell()
        self.data.append((filename[:-4]+".bmp",0,size,"bmp"))
        self.file = f

    def OpenArchiveFLM(self,file,filename):
        f = open(file,"rb")
        f.seek(0,2)
        size = f.tell()
        self.data.append((filename[:-4]+".anm",0,size,"anm"))
        self.file = f

    def OpenArchiveSND(self,file,filename):
        f = open(file,"rb")
        f.seek(0,2)
        size = f.tell()
        self.data.append((filename[:-4]+".wav",0,size,"wav"))
        self.file = f

    def OpenArchiveRES(self,file,filename):
        f = open(file,"rb")
        self.data.append((filename[:-4]+" 1.wav",0,32708576,"wav"))
        self.data.append((filename[:-4]+" 2.wav",32708576,35233868,"wav"))
        self.file = f

    def OpenArchiveDLL(self,file, filename):
        (self.dirname, filename) = os.path.split(file)
        Name_file = filename[:-4]+".SCR"

        if os.path.exists(self.dirname+"\\"+Name_file) == True:
            f_image = Image.open(self.dirname+"\\"+Name_file) # Открытие картинки
            pal_list = f_image.getpalette() # Достоёт палитру в виде списка из чисел
            self.Pal = bytes(pal_list) # Конвертирвуем список из числа в строчку из байтов
            f_image.close()

        else:
            #print("Ошибка, нет такого файла в папке", Name_file)
            pass

        list_f = []
        f = open(file,"rb")

        if filename == "GAME1.DLL":
            list_f = [(20576,20,29),(21156,20,29),(21736,20,29),(22316,20,29),(22896,20,29),(23476,20,29),(24056,20,29),(24636,20,29),(25216,20,29),(25796,20,29),(26377,117,400)]

        elif filename == "GAME2.DLL":
            list_f = [(35712,16,23),(36080,16,23),(36448,16,23),(36816,16,23),(37184,16,23),(37552,16,23),(37920,16,23),(38288,16,23),(38656,16,23),(39024,16,23),(50232,8,16),(50472,8,8)]

        # GAME3.DLL Нет картинок
        # GAME4.DLL Нет картинок
        # GAME5.DLL Нет картинок

        elif filename == "GAME6.DLL":
            list_f = [(19808,73,98),(26962,73,98),(34116,73,98),(41270,73,98),(48424,73,98),(55578,73,98),(62732,73,98),(69886,73,98),(77040,73,98),(84194,73,98),(91348,73,98),(98502,73,98),(105656,73,98),(112810,73,98),(119964,73,98),(127118,73,98),(134272,73,98)]

        # GAME7.DLL Нет картинок

        elif filename == "GAME8.DLL":
            list_f = [(19840,16,23),(20208,16,23),(20576,16,23),(20944,16,23),(21312,16,23),(21680,16,23),(22048,16,23),(22416,16,23),(22784,16,23),(23152,16,23)]

        elif filename == "GAME9.DLL":
            list_f = [(21936,40,7),(22216,40,7),(22496,7,40),(22776,7,40),(23056,7,40),(23336,7,40),(23616,20,20),(24016,20,20),(24416,20,20),(24816,40,33),(26136,40,33),(27456,40,33),(28776,40,33),(30096,40,33),(31416,40,33),(32736,40,33),(34056,40,33),(35376,40,33),(36696,40,33),(38016,40,33),(39336,40,33),(40656,40,33),(41976,40,33),(43296,40,33),(44616,40,33),(45936,40,33),(47256,40,33),(48576,40,33),(49896,40,33),(51216,40,33),(52536,40,33),(53856,40,33),(55176,40,33)]

        # GAME10.DLL Нет картинок
        # GAME11.DLL Нет картинок

        elif filename == "GAME2.DAT":
            list_f = [(0,76,30),(2280,76,29),(4484,640,480),(311684,640,480)]

        elif filename == "GAME3.DAT":
            list_f = [(0,90,80),(7200,90,80),(14400,90,80),(21600,90,80),(28800,90,80),(36000,90,80),(43200,90,80),(50400,70,80),(56000,70,80),(61600,70,80),(67200,70,80),(72800,70,80),(78400,70,80),(84000,70,80),(89600,70,80),(95200,70,80),(100800,120,80),(110400,2560,100)]

        elif filename == "GAME4.DAT":
            list_f = [(0,35,35),(1225,35,35),(2450,35,35),(3675,35,35),(4900,35,35),(6125,35,35),(7350,35,35),(8575,35,35),(9800,35,35),(11025,35,35),(12250,35,35),(13475,35,35),(14700,35,35),(15925,35,35),(17150,35,35),(18375,35,35),(19600,35,35),(20825,35,35),(22050,35,35),(23275,35,35),(24500,35,35),(25725,35,35),(26950,35,35),(28175,35,35),(29400,35,35),(30625,35,35),(31850,35,35),(33075,35,35),(34300,35,35),(35525,35,35),(36750,35,35),(37975,35,35),(39200,35,35),(40425,479,370),(217655,479,370),(394885,479,370),(572115,479,370),(749345,479,370),(926575,479,370),(1103805,479,370),(1281035,479,370),(1458265,479,370),(1635495,479,370),(1812725,479,370)]

        elif filename == "GAME5.DAT":
            list_f = [(0,200,101),(20200,200,101),(40400,200,101),(60600,200,101),(80800,200,101),(101000,200,101),(121200,200,101),(141400,77,69),(146713,77,69),(152026,77,69),(157339,77,69),(162652,77,69),(167965,77,69),(173278,77,69),(178591,77,69),(183904,77,69),(189217,77,69),(194530,77,69),(199843,77,69),(205156,77,69),(210469,77,69),(215782,92,79),(223050,92,79),(230318,92,79),(237586,92,79),(244854,92,79),(252122,92,79),(259390,92,79),(266658,123,66),(274776,123,66),(282894,123,66),(291012,123,66),(299130,123,66),(307248,123,66),(315366,123,66),(323484,96,80),(331164,96,80),(338844,96,80),(346524,96,80),(354204,96,80),(361884,96,80),(369564,96,80),(377244,96,80),(384924,96,80),(392604,96,80),(400284,96,80),(407964,96,80),(415644,96,80),(423324,96,80),(431004,80,120),(440604,80,120),(450204,80,120),(459804,80,120),(469404,80,120),(479004,80,120),(488604,80,120),(498204,80,120),(507804,80,120),(517404,80,120),(527004,80,120),(536604,80,120),(546204,80,120),(555804,80,120),(565404,280,280),(643804,280,280),(722204,280,280),(800604,280,280),(879004,280,280),(957404,280,280),(1035804,280,280),(1114204,280,280)]

        elif filename == "GAME7.DAT":
            list_f = [(0,57,152),(8664,57,152),(17328,600,440),(281328,600,440),(545328,600,440)]

        elif filename == "GAME8.DAT":
            list_f = [(0,36,54),(1944,18,36),(2592,18,36),(3240,18,36),(3888,36,54),(5832,36,36),(7128,36,36),(8424,18,18)]

        elif filename == "GAME10.DAT":
            list_f = [(0,120,90),(10800,120,150),(28800,120,90),(39600,120,120),(54000,90,120),(64800,60,120),(72000,60,120),(79200,120,90)]

        elif filename == "GAME11.DAT":
            list_f = [(0,84,84),(7056,84,84),(14112,84,84),(21168,84,84),(28224,84,84),(35280,84,84),(42336,84,84),(49392,84,84),(56448,84,84),(63504,84,84),(70560,84,84),(77616,84,84),(84672,84,84),(91728,84,84),(98784,84,84)]

        elif filename == "HISCORE.DAT":
            list_f = [(0,25,30),(750,25,30),(1500,25,30),(2250,25,30),(3000,25,30),(3750,25,30),(4500,25,30),(5250,30,30),(6150,30,30),(7050,25,30),(7800,25,30),(8550,25,30),(9300,25,30),(10050,27,30),(10860,25,30),(11610,25,30),(12360,25,30),(13110,25,30),(13860,25,30),(14610,25,30),(15360,25,30),(16110,30,30),(17010,25,30),(17760,25,30),(18510,25,30),(19260,25,30),(20010,27,30),(20820,25,30),(21570,25,30),(22320,25,30),(23070,25,30),(23820,30,30),(24720,25,30),(25470,25,30),(26220,25,30),(26970,25,30),(27720,25,30),(28470,25,30),(29220,25,30),(29970,25,30),(30720,25,30),(31470,25,30),(32220,25,30)]

        elif filename == "MENU.DAT":
            list_f = [(0,227,167),(37909,246,146),(73825,274,125),(108075,289,121),(143044,114,81)]

        elif filename == "HARE.EXE":
            f_image = Image.open(self.dirname+"\\"+"MENU.SCR") # Открытие картинки
            pal_list = f_image.getpalette() # Достоёт палитру в виде списка из чисел
            self.Pal = bytes(pal_list) # Конвертирвуем список из числа в строчку из байтов
            f_image.close()

            list_f = [(30082,14,23),(30404,16,23),(30772,16,23),(31140,16,23),(31508,16,23),(31876,16,23),(32244,16,23),(32612,16,23),(32980,16,23),(33348,16,23),(33716,16,23),(34084,81,29)]
            self.data.append(("60084.pic_2", 60084, 2088, "pic_2"))
            
        elif filename == "AUTORUN.EXE":
            self.data.append(("20112.pic_2", 20112, 308264, "pic_2"))
            self.data.append(("328376.pic_2", 328376, 308264, "pic_2"))
            self.data.append(("636640.pic_2", 636640, 308264, "pic_2"))
            self.data.append(("944904.pic_2", 944904, 2088, "pic_2"))

        if len(list_f) > 0: # Если в списке есть записанные файлы картинок
            for i in list_f:
                size = i[1] * i[2] # w*h
                self.data.append((str(i[0])+".pic",i[0], size, "pic", i[1],i[2])) 

        self.file = f

    def Unpack_BMP(self, f):
        image = Image.open(f)
        self.images = [image]

    def ConvertWAV(self, f):
        check = f.read(4) # Проверка
        if check != b'RIFF':
            f.seek(0)
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
                numChannels = 1
                sampleRate = 22050
                byteRate = 44100
                blockAlign = 2
                bitsPerSample = 16

                wav += struct.pack("<IHHIIHH", subchunk1Size, audioFormat, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample)
                wav += b"data"
                wav += struct.pack("<I", size)
                wav += data # Данные
            finally:
                self.sound = io.BytesIO(wav)
        else:
            self.sound = f

    def ConvertPIC(self, f, w, h):
        f_image = Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1)
        f_image.putpalette(self.Pal) # Добавляем палитру в картинку
        self.images.append(f_image)

    def Unpack_ANM(self, f):
        f.seek(0,2)  
        end_f = f.tell()
        f.seek(0)

        List_sizes = [(0,end_f)]
        f.seek(1) # Переходим к началу палитры

        for it in List_sizes:
            #print("Анимация на", it[0],"размер",it[1])

            # Нормальная распаковка
            f.seek(it[0]) # Переходим на оффсет
            fd = f.read(it[1]) # Читаем файл
            f2 = io.BytesIO(fd)
            f2.read(1) # 03

            Pal = b''
            for j in range(256): # Палитра 1024 байта
                b = f2.read(1)
                g = f2.read(1)
                r = f2.read(1)
                a = f2.read(1)
                Pal += r+g+b

            # Вначале данных первые байты всегда 05 01
            Block_number = 0 # Номер анимации
            #f_img = "" # Посылаем пустую что бы создать картинку с нужными параметрами ширины и высоты
            
            while True:
                if f2.tell() == it[1]: # Конец распаковки это нужно для файлов 00 24 13521148.anm и 04 2 308510.anm уних нет стоп байта 00
                    #print("Остановка в конце файла нет байт 00:", it)
                    break

                poz = f2.tell()
                check = f2.read(1) # Проверка

                if check == b'\x00': # Остановка конец файла
                    # Этого байта остановки нет в файлах
                    # Имя файла 00 24 13521148.anm позиция 401717 последний байт который там есть это 05
                    # Имя файла 04 2 308510.anm позиция 1503439 последний байт который там есть это 05
                    break

                # Возможно перд анимации стоит байт 05    # 05 01 это начало анимации
                elif check == b'\x01':
                    size = struct.unpack("<I",f2.read(4))[0] # Размер блока дальше

                    Block_number += 1
                    #print("Блок 01",poz,size,"Размер без заголовка",size,"Анимация номер",Block_number)
                    self.decompression(f2, Pal)

                    f2.seek(poz)
                    f2.seek(5+size, 1) # Пропускаем байты, пропускаем файл с анимациями

                elif check == b'\x02':
                    #print("Блок 02 pass")
                    pass

                elif check == b'\x03': # Звук
                    size = struct.unpack("<I",f2.read(4))[0] # Размер звука дальше
                    fd = f2.read(size) # Запись без заголовка
                    #print("Блок 03 звук позиция",poz,size,"Размер без заголовка",size)
                    self.fwav.write(fd) # Запись

                elif check == b'\x05': # Пустой байт без действия
                    #print("Блок 05 pass")
                    # Бывает вариации что после 05 идёт байт 01 но байт 01 запускает распаковку анимаций, при этом перед байтом 01 может небыть байта 05 файл 01 8 9268102.anm позиция 27291
                    # Бывает вариации что после 05 идёт байт 02 но байт 02 тоже нечего не делает
                    pass

                else:
                    print("Позиция файла", it[0], "размер файла", it[1])
                    print("    Ошибка непонятные байты", check, f2.tell()-1,"\n")
                    return(0)

            f2.close()
            self.f_img = "" # Очищяем картинку
        f.close()
        self.Unpack_NEW_WAV()

    def decompression(self, f, Pal):
        block_w = f.read(1)[0] # Количество блоков в ширину
        block_h = f.read(1)[0] # Количество блоков в высоту
        w = block_w * 8 # Ширина картинки
        h = block_h * 8 # Высота картинки

        #print("Количество блоков в ширину",block_w,"Высоту",block_h,"Всего блоков",block_w*block_h)
        #print("Реальная ширина картинки",w,"Высоту",h)

        if self.f_img == "": # Создать картинку
            self.f_img = io.BytesIO(b'\x00\x00\x00\x00'*(w*h)) # Создание файла картинки

        wx = 0 # Это оффсет наложения в ширину на одной линии по ширине картинки
        hy = 0 # Это оффсет наложения в высоту
        stop_end = block_w*block_h # Нужно для остановки

        control_bytes = struct.unpack("<H",f.read(2))[0]-2 # Сколько прочетать управляющих байтов

        # Третий алгоритм Две его вариации
        # Зарание сгенерирвать команды и записать их в список
        # Записывать команды не в список а в bytearray

        #BIT = [] # Список с битовыми командами
        BIT = bytearray(stop_end) # 0.328 sec но больше получается запусков с 0.344 sec

        Main_Number_Bits = 0 # Число из которого читаются биты
        Col_Bits_Main = 0 # Количество бит в числе

        ss = 0 # Количество команд определенно

        while True:
            if ss == stop_end: # Когда прочитаются все команды на блоки
                break

            if Col_Bits_Main >= 1 and Main_Number_Bits >> (Col_Bits_Main - 1) == 0: # 1 бит
                BIT[ss] = 0

                ss += 1
                #BIT.append(0) # Кладём в список

                # Удаляем 1 бита
                Col_Bits_Main -= 1 # Количество бит которое надо оставить
                Main_Number_Bits &= (1 << Col_Bits_Main)-1 # Создаём маску для обрезания до нужных бит

            elif Col_Bits_Main >= 4: # 4 бита
                BIT[ss] = Main_Number_Bits >> (Col_Bits_Main - 4) # Получаем число из 4 бит кладём их в список

                ss += 1
                #BIT.append(Main_Number_Bits >> (Col_Bits_Main - 4)) # Получаем число из 4 бит кладём их в список

                # Удаляем 4 бита
                Col_Bits_Main -= 4 # Количество бит которое надо оставить
                Main_Number_Bits &= (1 << Col_Bits_Main)-1 # Создаём маску для обрезания до нужных бит

            else: # Нехватает бит, читаем байты
                #""" Попытка ускорить считав сразу много байт а не по одному
                if control_bytes >= 8: # Читаем по 8 байт
                    Main_Number_Bits = (Main_Number_Bits << 64) + struct.unpack(">Q",f.read(8))[0]
                    Col_Bits_Main += 64 # Увеличиваем количество бит в числе
                    control_bytes -= 8 # Чтобы потом правельно зайти

                else: # Читаем по 1 байту
                    Main_Number_Bits = (Main_Number_Bits << 8) + f.read(1)[0]
                    Col_Bits_Main += 8 # Увеличиваем количество бит в числе
                    control_bytes -= 1
                #"""

                #Main_Number_Bits = (Main_Number_Bits << 8) + f.read(1)[0]
                #Col_Bits_Main += 8 # Увеличиваем количество бит в числе
                #control_bytes -= 1

        # Старого алгоритма время было 0.328 sec
        # Время второго алгоритма работы 0.328 sec
        # Время третьего алгоритма работы 0.328 sec но больше получается запусков с 0.344 sec


        # Биты читаются слева на права
        #print("Позиция",f.tell())

        Main_Number_Bits = 0 # Число из которого читаются биты
        Col_Bits_Main = 0 # Количество бит в числе

        ss = 0 # Блок который распаковываем
        while True:
            if ss == stop_end: # Когда распакуем все блоки
                break

            number = BIT[ss] # По номеру блока получаем число (команду)
            ss += 1 # Для чтения следующий команды

            if number == 0: # Пропускаем блок
                #print("  Зашли в бит 0")
                wx += 8
                if ss%block_w == 0: # Значит мы переходим на на новый блок в высоту Номер блока ss
                    hy += 8 # Прибавляем к высоте
                    wx = 0  # Ставим оффсет начало строчки

                continue # Возврат в начало нужно для того чтобы другие функции работали правельно

            # Дальше читается только по 4 бита

            elif number == 0b1001: # Повторить 64 раза 1 байт
                #print("  Зашли в 1001")
                buffer_bytes = b'' # Нужно чтобы не зайти в код
                f2 = io.BytesIO(f.read(1)*64) # 1 Байт который надо повторить 64 раза

            elif number == 0b1010: # Биты 0, 1
                #print("  Зашли в 1010")
                buffer_bytes = f.read(2) # Это используемые байты для распаковки
                col_bit = 1 # Сколько бит используется чтоб опредилить байт
                #control_bytes = 8 # Сколько прочетать управляющих байт

            elif number == 0b1011: # Биты 0, 10, 11
                #print("  Зашли в 1011")
                buffer_bytes = b''

                # Используется 3 байта для распаковки
                # Тут используется перменное количество байт для битового потока. Может быть от 8 байт (64 бита) до 16 байт(128 бита)

                f2 = io.BytesIO()

                bx1 = f.read(1) # Бит 0 # Это используемые байты для распаковки
                bx2 = f.read(1) # Бит 10
                bx3 = f.read(1) # Бит 11

                Main_Number_Bits_2 = 0 # Число из которого читаются биты
                Col_Bits_Main_2 = 0 # Количество бит в числе

                while True:
                    if f2.tell() == 64:
                        #print("Достигли конца распаковки")
                        break

                    if Col_Bits_Main_2 >= 1 and Main_Number_Bits_2 >> (Col_Bits_Main_2 - 1) == 0:
                        Col_Bits_Main_2 -= 1
                        f2.write(bx1)

                    elif Col_Bits_Main_2 >= 2 and Main_Number_Bits_2 >> (Col_Bits_Main_2 - 2) == 0b10:
                        Col_Bits_Main_2 -= 2
                        f2.write(bx2)

                    elif Col_Bits_Main_2 >= 2 and Main_Number_Bits_2 >> (Col_Bits_Main_2 - 2) == 0b11:
                        Col_Bits_Main_2 -= 2
                        f2.write(bx3)

                    else: # Нехватает бит, один бит 1 или два бита 2
                        # Берём наше число делаем битовый сдвиг на 8 прибавляем новое число
                        Main_Number_Bits_2 = (Main_Number_Bits_2 << 8) + f.read(1)[0]
                        Col_Bits_Main_2 += 8 # Увеличиваем количество бит в числе
                        continue

                    Main_Number_Bits_2 &= (1 << Col_Bits_Main_2)-1 # Создаём маску для обрезания до нужных бит

            elif number == 0b1100: # Биты 00, 01, 10, 11
                #print("  Зашли в 1100")
                buffer_bytes = f.read(4) # Это используемые байты для распаковки
                col_bit = 2 # Сколько бит используется чтоб опредилить байт
                #control_bytes = 16 # Сколько прочетать управляющих байт

            elif number == 0b1101: # Биты 000, 001, 010, 011, 100, 101, 110, 111
                #print("  Зашли в 1101")
                col = f.read(1)[0] # Сколько прочетать байтов
                buffer_bytes = f.read(col) # Это используемые байты для распаковки
                col_bit = 3 # Сколько бит используется чтоб опредилить байт
                #control_bytes = 24 # Сколько прочетать управляющих байт

            elif number == 0b1110: # Биты 0000, 0001, 0010, 0011, 0100, 0101, 0110, 0111, 1000, 1001, 1010, 1011, 1100, 1101, 1110, 1111
            # Эти биты обозначают номер в списке байтов
                #print("  Зашли в 1110")
                # Отправить строчку байт которые будут использоватся (брать срезами),
                # Отправить сколько должно бит быть в сравнении комбинаций col_bit (используется для среза)
                # Отправить файл
                # Сколько прочетать управляющих байт
                # Вернуть распакованный файл f2

                col = f.read(1)[0] # Сколько прочетать байтов
                buffer_bytes = f.read(col) # Это используемые байты для распаковки
                col_bit = 4 # Сколько бит используется чтоб опредилить байт
                #control_bytes = 32 # Сколько прочетать управляющих байт

            elif number == 0b1111: # Просто прочетать 64 байта
                #print("  Зашли в 1111")
                buffer_bytes = b''
                f2 = io.BytesIO(f.read(64)) # Просто прочетать байты

            else:
                print("Ошибка непонятная команда Позиция",f.tell())
                return(0)

            ###########################
            # Новый алгоритм выполняется за 0.328 sec
            # Заместо функции

            if buffer_bytes != b'': # Если есть байты то заходим
                f2 = io.BytesIO()
                Main_Number_Bits_3 = 0 # Число из которого читаются биты
                Col_Bits_Main_3 = 0 # Количество бит в числе

                for i in range(64): # Надо выполнить 64 команды и битового потока
                    if Col_Bits_Main_3 < col_bit: # Если бит меньше чем нужно читаем байт
                        # Берём наше число делаем битовый сдвиг на 8 прибавляем новое число
                        Main_Number_Bits_3 = (Main_Number_Bits_3 << 8) + f.read(1)[0]
                        Col_Bits_Main_3 += 8 # Увеличиваем количество бит в числе

                    Col_Bits_Main_3 -= col_bit # Количество бит которое надо оставить

                    number = Main_Number_Bits_3 >> Col_Bits_Main_3 # Избавляемся от ненужных бит, получаем нужное число
                    #number # Номер байта который надо записать

                    f2.write(buffer_bytes[number:number+1]) # Берём срезам нужный 1 байт и записываем его
                    #print("Читаем байт номер",number)

                    Main_Number_Bits_3 &= (1 << Col_Bits_Main_3)-1 # Создаём маску для обрезания до нужных бит
            ###########################

            #f2.seek(0)
            #fd = f2.read()
            #f1 = open(path+"\\Unpack\\"+str("%03d" %ss)+".bin8", "wb") # Без типа блока
            #f1.write(fd)
            #f1.close()

            #####################
            # Накладываем блок 8 на 8 картинки на большую картинку
            # 64 байта занимает один блок
            f2.seek(0) # Для начало чтения

            # Время работы 0.219 sec
            offset = wx + (hy*w)
            # К wx прибавил уже 8

            for i in range(8):
                self.f_img.seek(offset) # Переход на новую строчку по высоте
                self.f_img.write(f2.read(8)) # Сколько байт записать на строчку
                offset += w # Переход на новую строчку по высоте

            f2.close()
            #####################

            wx += 8
            if ss%block_w == 0: # Значит мы переходим на на новый блок в высоту Номер блока ss
                hy += 8 # Прибавляем к высоте
                wx = 0  # Ставим оффсет на чало строчки

        #print("Коцец распаковки сжатия",f.tell(),"\n")

        # Читаем картинку
        self.f_img.seek(0)
        img = Image.frombuffer('P', (w, h), self.f_img.read(w*h), 'raw', 'P', 0, 1)
        img.putpalette(Pal)

        # Сохраняем картинку с наложениями блоков
        self.images.append(img) # добавляем картинку

    def Unpack_NEW_WAV(self):
        size = self.fwav.tell()
        if size > 0: # Если записан звук
            self.fwav.seek(0)
            fd = self.fwav.read()

            wav = b""
            wav += b"RIFF"
            wav += struct.pack("<I", size+44-8)# chunkSize размер файла-8
            wav += b"WAVE" # format WAVE
            wav += b"fmt " # subchunk1Id fmt 0x666d7420    
            subchunk1Size = 16 
            audioFormat = 1 
            numChannels = 1    # Количество каналов
            sampleRate = 22050 # Частота файла
            byteRate = 44100   # Частота выхода звука, для расчёта длины звучания
            blockAlign = 2
            bitsPerSample = 16 # Битность звука
            wav += struct.pack("<IHHIIHH", subchunk1Size, audioFormat, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample)
            wav += b"data"
            wav += struct.pack("<I", size)
            wav += fd # Данные
            f3 = io.BytesIO(wav)
            self.sound = f3
            self.fwav = io.BytesIO() # Чистиим память

    def ConvertPIC_2(self, f):
        type = f.read(4) # Тип архива 28 00 00 00
        w, h = struct.unpack("<II",f.read(8)) # Ширина и высота
        unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно
        tip = struct.unpack("<H",f.read(2))[0] # Тип битности картинки
        f.seek(40)

        Pal = b'' # Палитра
        for i in range(256):
            B = f.read(1)
            G = f.read(1)
            R = f.read(1)
            Pal += R+G+B # RGB
            f.read(1) # A прозрачность

        if w == 32 and h == 64: # Картинка 944904
            h = 32 # Высота неправельная

        f_image = Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
        f_image.putpalette(Pal) # Добавляем палитру в картинку
        self.images.append(f_image)
        f.close()
