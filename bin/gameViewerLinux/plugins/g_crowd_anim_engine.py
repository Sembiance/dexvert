#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# GARbro https://github.com/morkt/GARbro
# https://github.com/talestra/talestra/tree/master/tests/brave

# Doushin - Same Heart                           [CWL, PCK]
# Tokimeki Check-In!                             [ZBM, INX]
# X-Change                                       [ZBM, BDT]
# X-Change R                                     [CWL, CWP, PCK, EOG]
# X-Change 2                                     [CWL, PCK]
# X-Change 2R                                    [CWL, CWP, PCK, EOG]
# X-Change 3                                     [CWL, CWP, PCK, EOG]
# Yin-Yang! X-Change Alternative                 [CWL, CWP, PCK, EOG]
# Yin-Yang! X-Change Alternative 2               [CWD, CWP, PCK, EOG]
# Yin-Yang! XChange-eX                           [CWD, GAX, PCK, EOG]
# Three Methods to Conquer the World             [CWD, CWP, PCK, EOG]
# Maou o Seifuku Suru Tame no 666 no Houhou     [CWD, CWP, PCK, EOG]
# Attack tentacles 2                             [CWD, CWP, PCK, EOG]
# Attack tentacles 3                             [CWD, CWP, PCK, EOG]
# Attack tentacles 4 + Extra Scenario            [CWD, GAX, PCK, EOG]
# Attack tentacles 5                             [CWD, GAX, PCK, EOG]
# Futari wa My Angel                             [CWD, GAX, PCK, EOG]
# Eve to Iu Na no Omocha                         [CWD, CWP, PCK, EOG, BMP]
# Zetsuboushi                                    [CWD, CWP, PCK, EOG]
# Hirusagari no Danchi In Tsuma                  [GAX, PCK, EOG]
# Hirusagari no Danchi In Tsuma 2                [GAX, PCK, EOG]
# Hirusagari no Danchi In Tsuma 3                [CWD, GAX, PCK, EOG]
# Wife-Swap Diaries                              [CWD, CWP, PCK, EOG]
# Musuko no Tomodachi ni Okasarete               [CWD, CWP, PCK, EOG]
# Hissatsu Chikannin II                          [CWD, CWP, PCK, EOG]
# Brave Soul                                     [CRP, PCK]
# Shinjin Kangofu Miho                           [PCK, EOG] (Картинки внутри архива)
# Sister Maria no Momoiro Seika                  [CWL, CWP, PCK, EOG]
# NTR Kanojo wa Ijimerarekko                     [CWD, GAX, PCK, EOG]
# Niehime - Sengoku Kanraku Emaki                [CWD, CWP, PCK, EOG]
# Itsu made mo Musuko no Mama ja Irarenai!       [GAX, PCK, EOG, DAT]
# Itsu made mo Musuko no Mama ja Irarenai! 2     [CWD, GAX, PCK, EOG, DAT]
# Itsu made mo Musuko no Mama ja Irarenai! 3     [CWD, GAX, PCK, EOG, DAT]
# Itsu made mo Boku dake no Mama no Mama de ite! [CWD, GAX, PCK, EOG, DAT]
# Chinmoku no Jogakuen                           [CWD, GAX, PCK, EOG]
# Joushi no Oku-san no Yokkyuu Fuman o Kaishou Sasete [GAX, PCK, EOG, DAT]
# Kouhai no Okusan ni Mukashi no Yoshimi de Amaete Mi mo Kokoro mo Netoru Hanashi [GAX, PCK, EOG, DAT]
# Senpai to Joushi to Kouhai no Oku-san o Mi mo Kokoro mo Netoru Pack [CWD, GAX, PCK, EOG, DAT]
# Kabe no Mukou no Tsuma no Koe                  [CWD, GAX, PCK, EOG]
# Kabe no Mukou no Tsuma no Koe 2                [CWD, GAX, PCK, EOG, DAT]
# Kanojo no Karada ni Tsuita Aitsu no Kiss Ato   [CWD, GAX, PCK, EOG, DAT]
# Kanrinin-san wa Miboujin                       [CWD, GAX, PCK, EOG]
# Mesu Ochi Kyonyuu Tsuma wa Ore no Mono         [CWD, GAX, PCK, EOG, DAT]
# Mesu Ochi! Miwaku no Hitozuma Life             [GAX, PCK, EOG, DAT]
# Omae no Mono wa Ore no Mono                    [CWD, GAX, PCK, EOG]
# Princess Collection                            [CWD, GAX, PCK, EOG, DAT]
# Saimin Counselor                               [CWD, GAX, PCK, EOG]
# Senpai no Oku-san ni Yuuwaku                   [CWD, GAX, PCK, EOG]
# Tsuma no Biniku o Ijiru Chichi no Futoi Yubi   [CWD, GAX, PCK, EOG, DAT]
# Tsuma no Niku Ana ni Homestay Suru Macho Ryuugakusei [CWD, GAX, PCK, EOG, DAT]
# Moshimo Youmuin no Ojisan ga Saimin wo Oboetara [CWD, GAX, PCK, EOG]
# Sodatete Miryu?                                [CWD, CWP, PCK, EOG]
# Kunoichiban!                                   [CWD, CWP, PCK, EOG]
# Heisei Nenkin Gekijou Erodake                  [CWD, CWP, PCK, EOG]
# How to Fudol                                   [CWD, CWP, PCK, EOG]
# Kyou*shi                                       [CWD, CWP, PCK, EOG]
# Intrigue of Attending                          [CWD, CWP, PCK, EOG]
# Tokumei Sentai Sirenger                        [CWD, CWP, PCK, EOG]
# Tokumei Sentai Yuzu Ranger                     [CWL, CWP, PCK, EOG]

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Crowd Anim Engine" 
FORMATS_ARCHIVE = ['zbm', "cwl", "cwd", "cwp", "dat", "bdt", "pck", "inx", "eog", "gax", "bmp", "crp", "psb"] 
TYPES_ARCHIVE = [('Crowd Anim Engine', ('*.zbm', '*.cwl', '*.cwd', '*.cwp', '*.dat', '*.bdt', '*.pck', '*.inx', '*.eog', '*.gax', '*.bmp', '*.crp', '*.psb'))]
GAMES = ["X-Change",
         "X-Change R",
         "X-Change 2",
         "X-Change 2R",
         "X-Change 3",
         "Yin-Yang! X-Change Alternative",
         "Yin-Yang! X-Change Alternative 2",
         "Yin-Yang! XChange-eX",
         "Tokimeki Check-In!",
         "Three Methods to Conquer the World",
         "Maou o Seifuku Suru Tame no 666 no Houhou",
         "Doushin - Same Heart",
         "Attack tentacles 2",
         "Attack tentacles 3",
         "Attack tentacles 4",
         "Attack tentacles 5",
         "Futari wa My Angel",
         "Eve to Iu Na no Omocha",
         "Zetsuboushi",
         "Hirusagari no Danchi In Tsuma",
         "Hirusagari no Danchi In Tsuma 2",
         "Hirusagari no Danchi In Tsuma 3",
         "Wife-Swap Diaries",
         "Musuko no Tomodachi ni Okasarete",
         "Hissatsu Chikannin II",
         "Brave Soul",
         "Shinjin Kangofu Miho",
         "Sister Maria no Momoiro Seika",
         "NTR Kanojo wa Ijimerarekko",
         "Niehime - Sengoku Kanraku Emaki",
         "Itsu made mo Musuko no Mama ja Irarenai!",
         "Itsu made mo Musuko no Mama ja Irarenai! 2",
         "Itsu made mo Musuko no Mama ja Irarenai! 3",
         "Itsu made mo Boku dake no Mama no Mama de ite!",
         "Chinmoku no Jogakuen",
         "Joushi no Oku-san no Yokkyuu Fuman o Kaishou Sasete",
         "Kouhai no Okusan ni Mukashi no Yoshimi de Amaete Mi mo Kokoro mo Netoru Hanashi",
         "Senpai to Joushi to Kouhai no Oku-san o Mi mo Kokoro mo Netoru Pack",
         "Kabe no Mukou no Tsuma no Koe",
         "Kabe no Mukou no Tsuma no Koe 2",
         "Kanojo no Karada ni Tsuita Aitsu no Kiss Ato",
         "Kanrinin-san wa Miboujin",
         "Mesu Ochi Kyonyuu Tsuma wa Ore no Mono",
         "Mesu Ochi! Miwaku no Hitozuma Life",
         "Omae no Mono wa Ore no Mono",
         "Princess Collection",
         "Saimin Counselor",
         "Senpai no Oku-san ni Yuuwaku",
         "Tsuma no Biniku o Ijiru Chichi no Futoi Yubi",
         "Tsuma no Niku Ana ni Homestay Suru Macho Ryuugakusei",
         "Moshimo Youmuin no Ojisan ga Saimin wo Oboetara",
         "Sodatete Miryu?",
         "Kunoichiban!",
         "Heisei Nenkin Gekijou Erodake",
         "How to Fudol",
         "Kyou*shi",
         "Intrigue of Attending",
         "Tokumei Sentai Sirenger",
         "Tokumei Sentai Yuzu Ranger"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["zbm",
                            "cwl",
                            "cwd",
                            "cwp",
                            "bmp",
                            "bdt",
                            "wav",
                            "eog",
                            "gax",
                            "crp",
                            "psb"]

        self.sup_types = {"zbm":1,
                          "cwl":1,
                          "cwd":1,
                          "cwp":1,
                          "bmp":1,
                          "bdt":4,
                          "wav":3,
                          "eog":3,
                          "gax":1,
                          "crp":1,
                          "psb":2}
        self.images = []   
        self.sound = None 
        self.text = None
        self.settings = [] # Настройки частоты звука

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "pck" or format == "dat":
            f = open(file,"rb")
            fd = f.read(4)
            f.close()
            if fd == b'PKWV': # С заголовком
                self.OpenArchivePCK(file)
            else:
                self.OpenArchivePCK_bez(file) # Без заголовка

        elif format in ['zbm', "cwl", "cwd", "cwp", "bmp", "bdt", "eog", "gax", "crp", "psb"]:
            self.Unpack_TIP(file)
        elif format == "inx":
            self.OpenArchiveINX(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "zbm":
            self.Unpack_ZBM(io.BytesIO(self.file.read(size))) 
        elif format == "cwl" or format == "cwd":
            self.Unpack_CWL(io.BytesIO(self.file.read(size)))
        elif format == "cwp" or format == "bmp":
            self.Unpack_CWP(io.BytesIO(self.file.read(size)))
        elif format == "bdt":
            self.Unpack_BDT(io.BytesIO(self.file.read(size)))
        elif format == "wav":
            if len(data_res) == 5:
                self.Unpack_NEW_WAV(io.BytesIO(self.file.read(size)),data_res[4])
            else:
                self.Unpack_WAV(io.BytesIO(self.file.read(size)))
        elif format == "eog":
            self.Unpack_EOG(io.BytesIO(self.file.read(size)))
        elif format == "gax":
            self.Unpack_GAX(io.BytesIO(self.file.read(size)))
        elif format == "crp":
            self.Unpack_CRP(io.BytesIO(self.file.read(size)))
        elif format == "psb":
            self.Unpack_PSB(io.BytesIO(self.file.read(size)))

    def OpenArchiveINX(self, file):
        self.data = []
        dirname, filename = os.path.split(file)
        arch = dirname+"\\"+filename[:-3]+"snn"
        if not os.path.exists(arch):
            raise Exception("Файл {} не найден".format(arch))
        f = open(file,"rb")
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        for i in range(col):
            filename = f.read(64).split(b"\x00")[0].decode("shift-jis").replace("\\\\","\\") # Имя файла
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size = struct.unpack("<I",f.read(4))[0] # Размер
            format = filename.split(".")[-1].lower()
            self.data.append((filename,offset,size,format))

        f.close()
        self.file = open(arch,"rb")

    def OpenArchivePCK(self, file):
        f = open(file,"rb")
        if f.read(4) != b'\x50\x4B\x57\x56': # Проверка на архив PKWV
            print("ЭТО НЕ АРХИВ")
            return(0) # Остановка скрипта 

        unclear_blok = struct.unpack("<H",f.read(2))[0] # Количество блоков
        col = struct.unpack("<H",f.read(2))[0] # Количество файлов
        f.read(2) # Непонятно 01 00
        for i in range(unclear_blok): # Блок с параметрами звука
            unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно
            frequency_1 = struct.unpack("<I",f.read(4))[0] # Частота 1
            frequency_2 = struct.unpack("<I",f.read(4))[0] # Частота 2
            unclear_2 = struct.unpack("<H",f.read(2))[0] # Битность звука
            unclear_3 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_4 = struct.unpack("<I",f.read(4))[0] # Непонятно
            unclear_5 = struct.unpack("<H",f.read(2))[0] # Непонятно
            self.settings.append((unclear_1,frequency_1,frequency_2,unclear_2,unclear_3,unclear_4,unclear_5))

        posf = f.tell() # Позиция в файле
        Start_offset = (col*24) + posf # Расчён начало звуков

        for i in range(col):
            filename = f.read(10).split(b"\x00")[0].decode("shift-jis").replace("\\\\","\\")+".wav"
            size = struct.unpack("<I",f.read(4))[0]
            offset = struct.unpack("<I",f.read(4))[0] + Start_offset # Добавляем конец таблицы файлов

            f.read(4) # Нули
            ddd = struct.unpack("<H",f.read(2))[0] # Поэтому номеру берутся данные из Блока с параметрами звука
            format = filename.split(".")[-1].lower()
            self.data.append((filename,offset,size,format,ddd))
            #print(filename,offset,size,ddd)
        self.file = f

    def OpenArchivePCK_bez(self, file):
        data2 = [] # Список оффсет и размер файла
        f = open(file,"rb")
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов

        for i in range(col):
            unclear = struct.unpack("<I",f.read(4))[0] # Непонятно
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size = struct.unpack("<I",f.read(4))[0] # Размер
            data2.append((offset,size))

        for i in range(col):
            f_path = b'' # Читаем имя файла до байта 00
            while True: 
                bait = f.read(1) # Байт строчки
                if bait == b'\x00':
                    filename = f_path.split(b"\x00")[0].decode("shift-jis").replace("\\\\","\\") # Имя файла
                    format = filename.split(".")[-1].lower()
                    self.data.append((filename,data2[i][0],data2[i][1],format))
                    break
                else:
                    f_path += bait # Прибавляем байт
        self.file = f

    def Unpack_NEW_WAV(self, f,tip):
        fd = f.read()
        size = f.tell()

        wav = b""
        wav += b"RIFF"
        wav += struct.pack("<I", size+44-8)# chunkSize размер файла-8
        wav += b"WAVE" # format WAVE
        wav += b"fmt " # subchunk1Id fmt 0x666d7420

        subchunk1Size = 16 # 
        audioFormat = 1 #
        numChannels = self.settings[tip][0]# 2 # Количкство каналов
        sampleRate = self.settings[tip][1] #11025  # Первая частота frequency_1
        byteRate = self.settings[tip][2]   #22050  # Вторая частота frequency_2
        blockAlign = 2
        bitsPerSample = self.settings[tip][3] # 16 битность звука

        wav += struct.pack("<IHHIIHH", subchunk1Size, audioFormat, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample)
        wav += b"data"
        wav += struct.pack("<I", size)
        wav += fd # Данные
        f2 = io.BytesIO(wav)
        self.sound = f2
        f.close()

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_EOG(self, f):
        fd_1 = f.read(4)
        if fd_1 == b'CRM\x00': # Звук ogg
            f.read(4)
            fd = f.read()
            f2 = io.BytesIO(fd)
            self.sound = f2
        else:
            print("ЭТО НЕ ЗВУК",fd_1)
            return(0)

    def Unpack_TIP(self, file):
        f = open(file,"rb")
        f.seek(0,2)
        size = f.tell()
        (dirname, filename) = os.path.split(file)
        format = file.split(".")[-1].lower()
        self.data.append((filename,0,size,format))
        self.file = f

    def Unpack_BDT(self, f):
        fd = bytearray(f.read())
        for i in range(len(fd)):
            fd[i] = fd[i] ^ 0xFF # XOR байт FF
        f2 = io.BytesIO(fd)
        f2.seek(0)
        try: # Исключения
            self.text = f2.read().decode("cp1251")
        except:
            print("Не поддерживается")
            try: # Исключения
                f2.seek(0)
                self.text = f2.read().decode("shift-jis")
                print("работает")
            except:
                print("Не поддерживается 2")

    def decompression(self, f,end_f): # Распаковка сжатых данных
        f3 = io.BytesIO() # Распакованные байты
        f4 = io.BytesIO() # Буфер
        for j2 in range(4096): # Буфер заполняем нулями
            f4.write(b'\x00')
        f4.seek(4080) # Начало записи в буфер с байта 4080

        while f.tell() != end_f: # В конце файла LZ77
            control_byte = struct.unpack("B",f.read(1))[0] # Прочитать уравляющий байт
            control_bit = d = [(control_byte & (2 ** i))>> i for i in range(8)]
            for ii in control_bit: # Перебрать биты управляющего байта справо на лево
                if f.tell() == end_f: # Проверка на конец файла
                    #print("Конец сжатия",f.tell())
                    break

                if int(ii) == 1: # Не сжатый байт
                    bytes = f.read(1) # Прочитать один байт
                    f4.write(bytes) # Запись в буфер
                    f3.write(bytes) # Записать байт в файл
                    if f4.tell() == 4096: # Перейти на буфере на 0
                        f4.seek(0)

                else: # Сжатый байты  
                    bait1 = f.read(1)[0]
                    bait2 = f.read(1)[0]
                    repeat_byte = (bait2 & 15) +3 # Правая половинка сколько прочитать байт байт 00 0F
                    offset_byte = (((bait2 & 240)>>4)<<8)+bait1 # Оффсет байт для повторение, из FF F0 получаем 0F FF
                    #print("С1",repeat_byte)
                    #print("С2",offset_byte) 
                    #print("Два сжатых байта",bait1,bait2,"Оффсет",offset_byte,"Прочитать байт",repeat_byte)#

                    offset_byte -= 1
                    for j3 in range(repeat_byte): # Сколько прочетать байт
                        posf4 = f4.tell() # Позиция в буфере нужно чтоб потом вернутся сюда и записатьт дальше байты
                        offset_byte += 1 # +1 к оффсету байта в буфере для чтения
                        if offset_byte == 4096: # Специально надо когда с конца буфера переходим на начало
                            offset_byte = 0 # Меняем оффсет на правельный
                        f4.seek(offset_byte) # Перейти на байты чтения
                        bytes = f4.read(1) # Читаем байт из буфера
                        f4.seek(posf4) # Переходим обратно на позицию в буфере
                        #print("Позиция для чтения",offset_byte,bytes,posf4) 
                        f4.write(bytes) # Запись в буфер
                        f3.write(bytes) # Записать байт в файл
                        if f4.tell() == 4096: # Перейти на буфере на 0	
                            f4.seek(0)
        f4.close()
        return(f3) 

    def Unpack_ZBM(self, f):
        f.seek(0,2)
        end_f = f.tell()

        f.seek(0)
        type = f.read(2) # Тип 
        if type == b'\xBD\xB2': # Это картинка без сжатия
            f.seek(0)
            fd = f.read()
            f3 = io.BytesIO(fd)
        else:
            f.seek(14) # Сжатый файл
            f3 = self.decompression(f,end_f)

        f3.seek(0) # Расшифровываем заголовок
        fd = bytearray(f3.read(100))
        for i in range(100):
            fd[i] = fd[i] ^ 0xFF # XOR байт FF
        f3.seek(0)
        f3.write(fd)
        image = Image.open(f3)
        self.images = [image]
        f.close()

    def Unpack_CWL(self, f):
        f.seek(0,2)
        end_f = f.tell()
        if end_f == 82:
            print("ЭТО НЕ КАРТИНКА")
            return(0)

        f.seek(0)
        type = f.read(28) # Тип 
        if type == b'cwd format  - version 1.00 -': # Это картинка без сжатия
            f3 = f
        else:
            f.seek(14) # Сжатый файл
            f3 = self.decompression(f,end_f)

        f3.seek(52)
        key = struct.unpack("B",f3.read(1))[0] + 9626
        f3.seek(44)
        w = struct.unpack("<H",f3.read(2))[0] # Читаем ширину
        w = (w+key)&65535
        f3.seek(48)
        h = struct.unpack("<H",f3.read(2))[0] # Читаем высоту
        h = (h+key)&65535

        f3.seek(56)
        rgb = np.frombuffer(f3.read(w*h*2), dtype=np.uint16)
        rgb = np.array(rgb, np.uint16).reshape(h, w)
        r,g,b = self.Color(rgb)
        rgb = np.dstack((r,g,b))
        rgb = np.uint8(rgb)

        self.images.append(Image.fromarray(rgb,"RGB"))
        f.close()

    def Color(self,p):
        r = ((p >> 10) & 31) << 3
        g = ((p >> 5) & 31) << 3
        b = (p & 31) << 3
        return (r,g,b)

    def Unpack_CRP(self, f):
        f.seek(0,2)
        end_f = f.tell()

        f.seek(14) # Сжатый файл
        f3 = self.decompression(f,end_f)
        f3.seek(0)
        # Расшифровываем заголовок
        Key_1 = [132, 65, 222, 72, 8, 207, 207, 111, 98, 81, 100, 223, 65, 223, 226, 225] # Ключ шифрования
        Key_2 = [] # Ключ шифрования

        type = f3.read(14) # Тип
        if type != b'(C)CROWD ARPG\x00': # Проверка
            print("ЭТО НЕ картинка",type)
            return(0) # Остановка скрипта 

        for i in range(8):
            byte = struct.unpack("B",f3.read(1))[0]
            Key_2.append(byte)

        f2 = io.BytesIO()
        fd = bytearray(f3.read(16)) # Читаем зашифрованный заголовок
        for i in range(16):
            fd[i] = (~(fd[i] & Key_1[i]) & (fd[i] | Key_1[i])) & 255

        for i in range(16):
            octatok = i % 8 # Получаем останок
            Key2 = Key_2[octatok]
            fd[i] = (~(fd[i] & Key2) & (fd[i] | Key2)) & 255

        f2 = io.BytesIO(fd)
        w,h = struct.unpack("<II",f2.read(8)) # Ширина и высота
        offset = struct.unpack("<I",f2.read(4))[0]+38 # Оффсет начало картинки
        #print("Высота и ширина картинки",w,h,"Насколько отойти",offset)
        f3.seek(offset) # Переход на начало картинки

        rgb = np.frombuffer(f3.read(w*h*2), dtype=np.uint16)
        rgb = np.array(rgb, np.uint16).reshape(h, w)
        r,g,b = self.Color_CRP(rgb)
        rgb = np.dstack((r,g,b))
        rgb = np.uint8(rgb)

        self.images.append(Image.fromarray(rgb,"RGB"))
        f3.close()
        f.close()

    def Color_CRP(self,p):
        r = ((p >> 11) & 31) << 3
        g = ((p >> 5) & 63) << 2
        b = (p & 31) << 3
        return (r,g,b)

    def Unpack_CWP(self, f):
        f2 = io.BytesIO()
        type = f.read(4) # Тип 
        if type != b'CWDP': # Проверка
            print("ЭТО НЕ картинка",type)
            return(0) # Остановка скрипта 

        fd_1 = f.read(21) # Читаем данные заголовка
        fd_2 = f.read() # Сжатые данные
        f.close()

        # Соединение PNG
        f2.write(b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A\x00\x00\x00\x0D\x49\x48\x44\x52') # 16 байтов заголовок
        f2.write(fd_1)
        f2.write(b'\x49\x44\x41\x54') # IDAT
        f2.write(fd_2)
        f2.write(b'\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82') # Конец файла

        img = Image.open(f2) # Это картинка PNG вней перепутаны каналы и канал альфа закрывает картинку
        b,g,r,a = img.split()
        rgb = np.dstack((r,g,b))
        rgb = np.uint8(rgb)
        self.images.append(Image.fromarray(rgb,"RGB"))
        img.close()
        f2.close()

    def Unpack_GAX(self, f):
        Key = [] # Ключ шифрования
        f.seek(0,2)
        end_f = f.tell()
        f.seek(0)

        type = f.read(4) # Тип
        if type != b'\x00\x00\x00\x01': # Проверка
            print("ЭТО НЕ КАРТИНКА",type)
            return(0) # Остановка скрипта
        for i in range(16):
            byte = struct.unpack("B",f.read(1))[0]
            Key.append(byte)

        f2 = io.BytesIO()

        while True:
            if f.tell() == end_f:
                break

            if end_f-f.tell() >= 16: # Если больше 16 читает 16 байтов
                Read_bytes = 16
            else: # Если меньше читаетм оставшиеся байты
                Read_bytes = end_f-f.tell()

            fd = bytearray(f.read(Read_bytes))
            for i in range(Read_bytes):
                fd[i] = fd[i] ^ Key[i]
            f2.write(fd)

            f2.seek(-2,2) 
            bit = struct.unpack("B",f2.read(1))[0] # Читаем байт для изменения ключа
            f2.seek(0,2)
            tip = bit & 7

            if tip == 0:
                Key[0] = Key[0] + bit
                Key[3] = Key[3] + bit + 2
                Key[4] = Key[2] + bit + 11
                Key[8] = Key[6] + 7

            elif tip == 1:
                Key[2] = Key[9] + Key[10]
                Key[6] = Key[7] + Key[15]
                Key[8] = Key[8] + Key[1]
                Key[15] = Key[5] + Key[3]

            elif tip == 2:
                Key[1] = Key[1] + Key[2]
                Key[5] = Key[5] + Key[6]
                Key[7] = Key[7] + Key[8]
                Key[10] = Key[10] + Key[11]

            elif tip == 3:
                Key[9] = Key[2] + Key[1]
                Key[11] = Key[6] + Key[5]
                Key[12] = Key[8] + Key[7]
                Key[13] = Key[11] + Key[10]

            elif tip == 4:
                Key[0] = Key[1] + 111
                Key[3] = Key[4] + 71
                Key[4] = Key[5] + 17
                Key[14] = Key[15] + 64

            elif tip == 5:
                Key[2] = Key[2] + Key[10]
                Key[4] = Key[5] + Key[12]
                Key[6] = Key[8] + Key[14]
                Key[8] = Key[11] + Key[0]

            elif tip == 6:
                Key[9] = Key[11] + Key[1]
                Key[11] = Key[13] + Key[3]
                Key[13] = Key[15] + Key[5]
                Key[15] = Key[9] + Key[7]

                Key[1] = Key[9] + Key[5]
                Key[2] = Key[10] + Key[6]
                Key[3] = Key[11] + Key[7]
                Key[4] = Key[12] + Key[8]

            else: # 7
                Key[1] = Key[9] + Key[5]
                Key[2] = Key[10] + Key[6]
                Key[3] = Key[11] + Key[7]
                Key[4] = Key[12] + Key[8]

            for i in range(16):
                if Key[i] > 255: # Если байт будет больше 256
                    Key[i] = Key[i] % 256      

        f.close()
        image = Image.open(f2)
        self.images = [image]

    def Unpack_PSB(self, f):
        data = [(67108864,4096,4096),(33554432,4096,2048),(16777216,2048,2048),(8388608,2048,1024),(4194304,1024,1024),(2097152,1024,512),(1048576,512,512),(524288,512,256),(262144,256,256)] # размеры и ширина и высота картинки
        f.seek(0,2)
        posf = f.tell() # Размер файла
        ti = 0 # Номер для списка
        while len(data) != ti:
            if posf >= data[ti][0] and posf-262144 > 171518: # and posf-262144 > 171518 чтоб не создавались не сушествующие картинки из данных
                w = data[ti][1]
                h = data[ti][2]
                f.seek(posf-(w*h*4))
                posf = f.tell() # Запоминаем новую позицию
                #print("Позиция",posf,w,h)
                rgb = np.frombuffer(f.read(w*h*4), dtype = np.uint8)
                rgb = np.array(rgb,np.uint8).reshape(h, w, 4)
                b,g,r,a = np.rollaxis(rgb, axis = -1)
                rgb = np.dstack([r,g,b,a])
                self.images.append(Image.fromarray(rgb,"RGBA"))
            else:
                ti += 1 # Если нет такого размера перходим к другому размеру
