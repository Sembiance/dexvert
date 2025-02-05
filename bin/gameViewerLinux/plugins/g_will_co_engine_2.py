#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Mote Sugite Shuraba na Ore      [ARC, WIP, MSK, MOS, OGG, PNG]
# Vampire Sweetie                 [ARC, WIP, MSK, MOS, OGG, PNG]
# Otome ga Tsumugu Koi no Canvas  [ARC, WIP, MOS, OGG, PNG]
# Wanna. SpartanSex Spermax!!!    [ARC, WIP, MOS, OGG, PNG, TXT]
# Tokoya no Oba-chan              [ARC, WIP, MOS, OGG, PNG, TXT]
# Kanojo to Ore to Koibito to     [ARC, WIP, MSK, MOS, OGG, PNG]
# Duelist x Engage                [ARC, WIP, MSK, MOS, OGG, PNG]
# Anata no Koto o Suki to Iwasete [ARC, WIP, MSK, MOS, OGG, PNG]

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Will Co. Engine 2"
FORMATS_ARCHIVE = ['arc']
TYPES_ARCHIVE = [('Will Co. Engine 2', ('*.arc'))]
GAMES = ["Mote Sugite Shuraba na Ore",
         "Vampire Sweetie",
         "Otome ga Tsumugu Koi no Canvas",
         "Wanna. SpartanSex Spermax!!!",
         "Tokoya no Oba-chan",
         "Kanojo to Ore to Koibito to",
         "Duelist x Engage",
         "Anata no Koto o Suki to Iwasete"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["wip",
                            "msk",
                            "mos",
                            "png",
                            "ogg",
                            "txt"]

        self.sup_types = {"wip":2,
                          "msk":2,
                          "mos":2,
                          "png":1,
                          "ogg":3,
                          "txt":4}
        self.images = []   
        self.sound = None 
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "arc":
            self.OpenArchive(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format in ["wip", "msk", "mos"]:
            self.Unpack_WIP(io.BytesIO(self.file.read(size)))
        elif format == "ogg":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))
        elif format == "png":
            self.Unpack_PNG(io.BytesIO(self.file.read(size)))
            
        elif format == "txt":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))
            
    def OpenArchive(self,file):
        f = open(file,"rb")

        file_format = [] # Форматы файлов
        col_format = struct.unpack("<I",f.read(4))[0] # Количество форматов внутри архива
        #print("Количество форматов внутри архива",col_format)
        for i in range(col_format):#
            format = f.read(4).split(b"\x00")[0].decode("cp1251").replace("\\\\","\\").lower()# Формат файлов
            col_f = struct.unpack("<I",f.read(4))[0]  # Количество файлов с этим форматом
            offset = struct.unpack("<I",f.read(4))[0] # Начало таблицы к которым надо присвоить формат
            #print(format,col_f,offset)
            file_format.append((format,col_f,offset))

        for i in file_format:
            f.seek(i[2]) # Начало таблицы
            for j in range(i[1]): # Количество файлов
                filename = f.read(13).split(b"\x00")[0].decode("cp1251").replace("\\\\","\\")+"."+i[0] # Имя файла
                size = struct.unpack("<I",f.read(4))[0] # Размер
                offset = struct.unpack("<I",f.read(4))[0] # Оффсет
                self.data.append((filename,offset,size,i[0]))
        self.file = f
        return 1

    def Unpack_WIP(self,f):
        data = [] # Список картинок
        Pal = [] # Палитра

        type = f.read(4) # WIPF
        if type == b'WIPF' or type ==  b'WAPF': # Проверка на картинку WAPF это картинки 32 бита
            pass
        else:
            print("ЭТО НЕ КАРТИНКА")
            return(0)

        col_pic = struct.unpack("<H",f.read(2))[0] # Количество картинок ?
        bit = struct.unpack("<H",f.read(2))[0] # Битность картинки 8hex 8 бит с палитрой,   18hex 24 бита
        #print("Количество картинок",col_pic,"Битность",bit)

        if bit == 8 or bit == 24 or bit == 0:
            pass
        else:
            print("Непонятно",bit,"########################")

        ss = 0 # Номер картинки     
        for i in range(col_pic):
            ss += 1
            w,h = struct.unpack("<II",f.read(8))
            unclear1,unclear2,unclear3 = struct.unpack("<III",f.read(12)) # x y z Позиция на экране BGM_P1G.WIP
            size_comp = struct.unpack("<I",f.read(4))[0] # Размер сжатых данных
            data.append((w,h,size_comp,ss))
            #print(w,h,size_comp)

        for i in data:
            posf1 = f.tell() # Проверка на палитру для каждой картинки
            type = f.read(4) # Тип 
            if type == b'\x00\x00\x00\x00' and bit == 8 or type == b'\xFF\xFF\xFF\x00' and bit == 8:
                f.seek(posf1)
                Pal = b'' # Для чтенения палитры
                for j in range(256): # Палитра 1024 байта
                    b = f.read(1)
                    g = f.read(1)
                    r = f.read(1)
                    a = f.read(1)
                    Pal += r+g+b
            else:
                f.seek(posf1)

            f5 = io.BytesIO()
            ww = i[0]
            hh = i[1]
            if i[2] == ((i[0]*i[1]) *3)+8: # Проверка на не сжатую картинку
                #print("Не сжатая картинка",f.tell())
                f.read(8) # Проверить байты ПРОВЕРИТЬ БАЙТЫ7777777 EPI_01.WIP +8 байт в распакованных картинках
                fd = f.read(i[2]-8)  # -8 чтоб нечитать лишнии байты
                f5.write(fd)

            else:
                f2 = io.BytesIO(f.read(i[2])) # Файл сжатыми данными
                output = bytearray(1) # Распакованный файл, заполняем файл байтами 00

                while f2.tell() != i[2]-2: # В конце файла 2 байта всегда 00 00
                    # Получаем строчку Обратный порядок бит
                    for ii in bin(f2.read(1)[0])[2:].zfill(8)[::-1]: # Перебрать биты управляющего байта справо на лево
                        if f2.tell() == i[2]-2: # Проверка на конец файла
                            #print("Конец",f2.tell())
                            break

                        if ii == "1": # Не сжатый байт
                            bytes = f2.read(1) # Прочитать один байт
                            output.append(bytes[0]) # Записываем в выходной файл

                        else: # Сжатый байты
                            data_byte = struct.unpack(">H",f2.read(2))[0] # Сжатые байты
                            col = (data_byte & 0x0F) + 2 # Правая половинка сколько прочитать байт байт 000F
                            offset = data_byte >> 4 # Оффсет байт для повторение, из FFF0 получаем 0FFF
                            #print("Сжатые байты",data_byte,"Оффсет",offset,"Прочитать байт",col)

                            len_output = len(output) # Узнаём длину распакованого файла Переменная ускоряет распаковку

                            offset = len_output - ((len_output - offset) & 0xFFF) # Получаем оффсет чтения байтов в распакованном файле

                            #for ii in range(offset, offset+col):
                                #output.append(output[ii]) # Записываем в выходной файл

                            # Время 2.203 sec EV31.WIP
                            len_byte = len_output - offset # Получаем количество байт доступное с конца файла

                            if len_byte >= col: # Если количество байт в конце файла больше чем нужно надо взять, просто читаем нужное число байт сразу
                                output.extend(output[offset:offset+col]) # Записываем в выходной файл последовательность байт

                            else:
                                output.extend((output[offset:offset+len_byte]*((col//len_byte)+1))[:col]) 

                #check = f2.read() # Проверка байт остановки сжатия
                #if check != b'\x00\x00':
                    #print("    Ошибка последнии 2 байта не нули", check)
                f2.close() # Сжатые данные
                f5.write(output[1:])

            f5.seek(0)
            if bit == 8: # 8 бит
                #print("8 бит")
                f_image = Image.frombuffer('P', (ww,hh), f5.read(ww*hh), 'raw', 'P', 0, 1)
                f_image.putpalette(Pal)
                self.images.append(f_image)

            elif bit == 24: # R G B цвета 24 бит
                #print("24 бит")
                b = np.frombuffer(f5.read(ww*hh), dtype = np.uint8) # Каналы BGR
                g = np.frombuffer(f5.read(ww*hh), dtype = np.uint8)
                r = np.frombuffer(f5.read(ww*hh), dtype = np.uint8)

                rgb = np.dstack((r,g,b))
                rgb = np.array(rgb,np.uint8).reshape(hh, ww, 3)
                self.images.append(Image.fromarray(rgb,"RGB"))                 

            elif bit == 0: # R G B A цвета 32 бит
                #print("32 бит")
                a = np.frombuffer(f5.read(ww*hh), dtype = np.uint8) # Каналы ARGB  Альфа канал
                r = np.frombuffer(f5.read(ww*hh), dtype = np.uint8)
                g = np.frombuffer(f5.read(ww*hh), dtype = np.uint8)
                b = np.frombuffer(f5.read(ww*hh), dtype = np.uint8)
                rgb = np.dstack((r,g,b,a))
                rgb = np.array(rgb,np.uint8).reshape(hh, ww, 4)
                self.images.append(Image.fromarray(rgb,"RGBA"))

            else:
                print("Непонятно")
            f5.close()
        #print()
        
    def Unpack_WAV(self, f):
        self.sound = f
        
    def Unpack_PNG(self, f):
        image = Image.open(f)
        self.images = [image]
        
    def Unpack_TXT(self, f):
        self.text = f.read().decode("shift-jis")