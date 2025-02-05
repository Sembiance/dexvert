#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Elf All Stars Datsui Jan

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Elf All Stars Datsui Jan" 
FORMATS_ARCHIVE = ['arc']
TYPES_ARCHIVE = [('Elf All Stars Datsui Jan', ('*.arc'))]
GAMES = ["Elf All Stars Datsui Jan"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["gp8",
                            "g16",
                            "bmp",
                            "000"]

        self.sup_types = {"gp8":1,
                          "g16":1,
                          "bmp":1,
                          "000":1}

        self.images = []  
        self.sound = None

        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "arc":
            self.OpenArchiveARC(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "gp8" or format == "g16":
            self.Unpack_GP(io.BytesIO(self.file.read(size)),format)

        elif format == "bmp":
            self.Unpack_BMP(io.BytesIO(self.file.read(size)),name)

        elif format == "000":
            self.Unpack_000(io.BytesIO(self.file.read(size)),name)

    def OpenArchiveARC(self,file):
        self.data = []

        f = open(file,"rb")
        f2 = io.BytesIO()
        xor_key = bytearray(b'\x88\xCF\x88\xCF\xBD\x44\xBD\x44') # XOR ключ
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        for i in range(col):
            fd = bytearray(f.read(20)) # Имя файла
            for i in range(len(fd)):
                fd[i] = (fd[i] ^ 0x66)

            fd2 = bytearray(f.read(8)) # Размер и оффсет
            for i in range(len(fd2)):
                fd2[i] = fd2[i] ^ xor_key[i]

            f2.write(fd)
            f2.write(fd2)

        f2.seek(0)
        for i in range(col):
            filename = f2.read(20).split(b"\x00")[0].decode("shift-jis").replace("\\\\","\\") # Имя файла
            size = struct.unpack("<I",f2.read(4))[0] # Размер
            offset = struct.unpack("<I",f2.read(4))[0] # Оффсет
            format = filename.split(".")[-1].lower()
            self.data.append((filename,offset,size,format))
        f2.close()
        self.file = f

    def Unpack_GP(self, f, format):
        f.seek(0,2)
        end_f = f.tell()
        f.seek(0)
        if f.read(4) != b'\x00\x00\x00\x00': # Проверка
            print("ЭТО НЕ КАРТИНКА")
            return(0) 

        w,h = struct.unpack("<HH",f.read(4)) # Высоты и ширина

        if format == 'gp8':
            Pal = b""
            for i in range(256):
                B = f.read(1)
                G = f.read(1)
                R = f.read(1)
                Pal += R+G+B
                f.read(1) # A

        output = self.decompression(f) # Распаковка сжатия

        f3 = io.BytesIO() # Распакованные байты
        f3.write(output) # Отрезаем пустые байты в начале файла
        size = f3.tell()
        if size == w*h or w*h*2:
            pass
        else:
            print("НЕПОНЯТНЫЙ РАЗМЕР РАСПАКОВАННОГО ФАЙЛА", mult_file, size)

        f3.seek(0) # Распакованный файл

        if format == 'gp8': # С палитрой 8 бит
            f_image = Image.frombuffer('P', (w,h), f3.read(w*h), 'raw', 'P', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
            f_image.putpalette(Pal)
            self.images.append(f_image)

        elif format == 'g16':   
            self.images.append(Image.frombuffer('RGB', (w,h), f3.read(w*h*2), 'raw', 'BGR;15', 0, 1).transpose(Image.FLIP_TOP_BOTTOM))

        f3.close()

    def decompression(self, f):
        src = iter(f.read()) # Сжатые данные Итерация
        f.close()
        output = bytearray(4096) # Распакованный файл, заполняем файл байтами 00

        try:
            while True:
                # Управляющий байт, биты читаются справа налево
                for i3 in bin(next(src))[2:].zfill(8)[::-1]: # Так незначительно быстрей
                    if i3 == "1": # Просто чтение 1 байта
                        output.append(next(src)) # Записываем в выходной файл

                    else: # Сжатый байты
                        byte1 = next(src) # EE
                        byte2 = next(src) # F0

                        offset_buffer = ((byte2 <<4) & 0xF00)+byte1 # Оффсет чтения в буффере, из EE F0 получаем 0F EE

                        col = (byte2 & 0x0F) + 3 # Правая половинка сколько прочитать байт байт 0F
                        #print("Два сжатых байта",byte1,byte2,"Оффсет",offset_buffer,"Прочитать байт",col)

                        len_output = len(output) # Узнаём длину распакованого файла Переменная ускоряет распаковку

                        #offset = len_output - ((len_output + 0xFEE - offset_buffer) & 0xFFF) # Получаем оффсет чтения байтов в распакованном файле 4.250 sec
                        offset = len_output - ((len_output - 18 - offset_buffer) & 0xFFF)

                        len_byte = len_output - offset # Получаем количество байт доступное с конца файла

                        if len_byte >= col: # Если количество байт в конце файла больше чем нужно надо взять, просто читаем нужное число байт сразу
                            output.extend(output[offset:offset+col]) # Записываем в выходной файл последовательность байт

                        else:
                            output.extend((output[offset:offset+len_byte]*((col//len_byte)+1))[:col])

        except StopIteration: # Остановка так быстрей
            pass
            # Остановка если кончились байты в итерации, так значительно быстрей чем вести подсчёт каждого прочтенного байта в сжатом файле

        return(output[4096:])

    def Unpack_BMP(self, f, name):
        if name == "CHARA.BMP":
            w = 640
            h = 480

        elif name == "MAP.BMP":
            w = 1280
            h = 960

        else:
            print("Непонятный файл",name)

        for ii in self.data:    
            if ii[0] == name[:-4]+".PAL": # Ищем палитру если нашли заходим
                offset = ii[1] # Достаём оффсет палитры
                break # Останавливаем перебор

        self.file.seek(offset) # Перейти на оффсет палитры в архиве

        Pal = b''
        for i in range(256): # Читаем палитру и переделаваем её
            Color = struct.unpack("H",self.file.read(2))[0] # Цвет
            r = ((Color >> 10) & 31) << 3
            g = ((Color >> 5) & 31) << 3
            b = (Color & 31) << 3
            Pal += struct.pack("BBB", r,g,b)

        f_image = Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
        f_image.putpalette(Pal)
        self.images.append(f_image)

    def Unpack_000(self, f, name):
        col_f = struct.unpack("<I",f.read(4))[0] # Количество файлов которое надо распаковать чтобы получить полностью файл
        size = struct.unpack("<I",f.read(4))[0] # Размер распакованого файла
        tip = f.read(4).split(b"\x00")[0].decode("utf8") # Тип файла
        # Типы файлов внутри bmp, BMP, ICO, mp3, wav, ini, INI, exe, scr, arc
        #print("Тип файла",tip)

        # Чтобы полностью собрать файл, читаются сжатые файлы 000, 001, 002, 003, 004, 005, 006, 007, 008

        output = self.decompression(f) # Распаковка сжатия
        f2 = io.BytesIO(output) # Записали первую часть файла
        f2.seek(0,2) # Нужно чтобы файл правельно распаковался

        for i in range(col_f-1): # Открываем и распаковывем следующие архивы
            name_next = name[:-4]+".00"+str(i+1) # Имя следующего архива

            for ii in self.data: # Ищем файл
                if ii[0] == name_next: # Нашли заходим
                    offset = ii[1] # Достаём оффсет файла
                    size_2 = ii[2] # Достаём размер файла
                    break # Останавливаем перебор

            self.file.seek(offset) # Перейти на оффсет в архиве
            fd = self.file.read(size_2) # Читаем сжатый файл
            f3 = io.BytesIO(fd) # Файл для распаковки
            output = self.decompression(f3) # Распаковка сжатия
            f2.write(output) # Запись части файла
            f3.close()

        f2.seek(0)
        if tip in ["bmp", "BMP", "ICO"]:
            image = Image.open(f2)
            self.images = [image]
            #self.images.append(image) # Если надо добавить несколько картинок

        #elif tip == "mp3": # Внутри заголовок RIFF WAVE непотдерживает такой формат
            #self.sound = f2

        #elif tip in ["ini", "INI"]: # Иза формата анимаций файл не открывается как текст это нерешаемая задача
            #self.text = f2.read().decode("shift-jis")

        else: # Если файл не используется закрываем его
            f2.close()