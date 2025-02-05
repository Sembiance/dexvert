#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Sakura Wars SPR

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Sakura Wars"
FORMATS_ARCHIVE = ['spr','bin','tab'] 
TYPES_ARCHIVE = [('Sakura Wars', ('*.spr', '*.bin', '*.tab'))]
GAMES = ["Sakura Wars"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["pic",
                            "pic2",
                            "txt",
                            "txt2"]
        self.sup_types = {"pic":1,
                          "pic2":1,
                          "txt":4,
                          "txt2":4}
        self.images = [] 
        self.sound = None
        self.list_pal = [] # Список палитр для BE_JCZ2.SPR
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "spr":
            self.OpenArchiveSPR(file)
        elif format == "tab":
            self.OpenArchiveTAB(file)
        elif format == "bin":
            self.OpenArchiveBIN(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "pic":
            self.Unpack_PIC(io.BytesIO(self.file.read(size)),data_res[4],data_res[5],size) # w, h, size
        elif format == "pic2":
            self.Unpack_PIC2(io.BytesIO(self.file.read(size)),data_res[4],data_res[5],data_res[6])
        elif format == "txt":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))
        elif format == "txt2":
            self.Unpack_TXT2(io.BytesIO(self.file.read(size)))

    def OpenArchiveSPR(self,file):
        dirname, mult_file = os.path.split(file)
        f = open(file,"rb")
        data2 = [] # Список внутрених файлов
        f.seek(0,2)
        end_f = f.tell()
        f.seek(0)

        type = f.read(16) # Тип
        if type in [b'SEGA SPRED 02.00', b'SEGA SPRED 02.0M']:
            pass
        else:
            print("ЭТО НЕ АРХИВ",type)
            return(0) # Остановка скрипта

        for i in range(15):
            offset = struct.unpack(">I",f.read(4))[0] # Оффсет  смещение вложенные папки
            size1 = struct.unpack(">I",f.read(4))[0]  # Размер файла 
            tip = struct.unpack(">I",f.read(4))[0]    # Номер файла непонятно ?
            zero = struct.unpack(">I",f.read(4))[0]   # Всегда нули
            if offset > 0:
                data2.append((offset,size1))
        ss = 0         
        for i in data2:
            ss += 1
            f.seek(i[0])
            fd = f.read(i[1])

            f4 = io.BytesIO(fd)
            col_f = struct.unpack(">H",f4.read(2))[0] # Количество файлов
            b1, b2 = struct.unpack(">HH",f4.read(4)) # Всегда 1 1
            b01 = f4.read(10) # Непонятные 10 байт
            end_table = (col_f * 16)+16 # Это надо прибавить к оффсету из таблицы чтоб узнать правельный оффсет
            #print("Количество картинок",col_f,"Прибавть к оффсету",end_table)

            if b1 == 1 and b2 == 1: # если это файл с картинкой
                for i2 in range(col_f): # Считаем информацию о картинках 16 байт строчка
                    posf4 = f4.tell()
                    w,h = struct.unpack(">HH",f4.read(4)) # Высоты и ширина
                    unclear1 = struct.unpack(">H",f4.read(2))[0] # Непонятно
                    unclear2 = struct.unpack(">H",f4.read(2))[0] # Непонятно
                    offset = struct.unpack(">I",f4.read(4))[0] + end_table + i[0]# Оффсет сжатого файла расчёт оффсета идёт от конца таблицы
                    size = struct.unpack(">I",f4.read(4))[0] # Размер файла 
                    if size > 0 and end_f > offset:
                        self.data.append((str(ss)+" "+str(offset)+".pic",offset,size,"pic",w,h))
                        #print(offset,size,w,h)

                    else:
                        f4.seek(posf4)
                        incomprehensible_line = f4.read(16) # Строчка с непонятной картинкой
                        if incomprehensible_line == b'\x00'*16: # Тут нет файла
                            pass

                        elif mult_file == "EV19S03.SPR": # Тут записан текстовый файл заместо строчек картинок
                        # Первый текстовый файл занимает 39 строчек это 624 байт, второй занимает 190 строчек это 3040 байт.
                            pass
                        else:
                            # Кроме этих непонятных строчек в файле блока нет других ненужных данных
                            #print("Непонятно",f_path,"Оффсет и размер блока",i[0],i[1])
                            pass

            elif mult_file == "BE_JCZ2.SPR" and ss == 1: # Это палитра
                self.data.append((str(ss)+".pal",i[0],i[1],"pal"))
                f.seek(i[0]+16) # Пропускаем заголовок
                for jj1 in range(8):
                    Pal = b'' # Идут в BGR
                    for j2 in range(256): # Читаем палитру и переделаваем её
                        Color = struct.unpack(">H",f.read(2))[0] # Цвет
                        b = ((Color >> 10) & 31) << 3
                        g = ((Color >> 5) & 31) << 3
                        r = (Color & 31) << 3
                        Pal += struct.pack("BBB", r,g,b)
                    self.list_pal.append(Pal)

            elif mult_file == "BE_JCZ2.SPR" and ss == 2: # Это не сжатые картинки
                self.data.append((str(ss)+".pic3",i[0],i[1],"pic3")) # Файл с картинками

                f.seek(i[0]) 
                col_f = struct.unpack(">H",f.read(2))[0] # Количество файлов
                f.read(14) # Нули
                end_table2 = (col_f * 16)+16 # Это надо прибавить к оффсету из таблицы чтоб узнать правельный оффсет начало картинок
                for iy in range(col_f):
                    w,h = struct.unpack(">HH",f.read(4)) # Высоты и ширина
                    unclear1 = struct.unpack(">H",f.read(2))[0] # Непонятно возможно это координаты ?
                    unclear2 = struct.unpack(">H",f.read(2))[0] # Непонятно
                    offset = struct.unpack(">I",f.read(4))[0] + end_table2 + i[0] # Оффсет сжатого файла расчёт оффсета идёт от конца таблицы
                    size = struct.unpack(">I",f.read(4))[0] # Размер файла
                    self.data.append((str(ss)+" "+str(offset)+".pic2",offset,w*h,"pic2",w,h,iy+1)) # iy+1 нужен для правельной палитры
            else:
                self.data.append((str(ss)+".bin",i[0],i[1],"bin"))

            f4.close()
        self.file = f

    def OpenArchiveTAB(self,file):
        f = open(file,"rb")
        f.seek(0,2)
        size = f.tell() # Конец файла
        self.data.append(("1.txt2",0,size,"txt2"))
        self.file = f

    def OpenArchiveBIN(self,file):
        f = open(file,"rb")
        dirname, mult_file = os.path.split(file)
        gg = mult_file.lower() # Преобразование строки к нижнему регистру
        if gg in ['0100tbl.bin', '0101tbl.bin', '0102tbl.bin', '0103tbl.bin', '0107tbl.bin', '0108tbl.bin', '0109tbl.bin', '0201tbl.bin', '0202tbl.bin', '0203tbl.bin', '0204tbl.bin', '0205tbl.bin', '0206tbl.bin', '0301tbl.bin', '0302tbl.bin', '0303tbl.bin', '0304tbl.bin', '0305tbl.bin', '0306tbl.bin', '0307tbl.bin', '0308tbl.bin', '0309tbl.bin', '0400tbl.bin', '0401tbl.bin', '0402tbl.bin', '0403tbl.bin', '0501tbl.bin', '0502tbl.bin', '0503tbl.bin', '0504tbl.bin', '0601tbl.bin', '0602tbl.bin', '0603tbl.bin', '0604tbl.bin', '0605tbl.bin', '0606tbl.bin', '0607tbl.bin', '0700tbl.bin', '0701tbl.bin', '0702tbl.bin', '0801tbl.bin', '0802tbl.bin', '0803tbl.bin', '0804tbl.bin', '0805tbl.bin', '0806tbl.bin', '0807tbl.bin', '0900tbl.bin', '0901tbl.bin', '0902tbl.bin', '0903tbl.bin', '0904tbl.bin', '0905tbl.bin', '1001tbl.bin', '1002tbl.bin', '1003tbl.bin', '1004tbl.bin', '1008tbl.bin', '1009tbl.bin', 'm01mes.bin', 'm02mes.bin', 'm03mes.bin', 'm04mes.bin', 'm05mes.bin', 'm06mes.bin', 'm07mes.bin', 'm08mes.bin', 'm09mes.bin', 'm10mes.bin', 'm11mes.bin', 'm12mes.bin', 'm13mes.bin', 'm14mes.bin', 'm15mes.bin', 'm16mes.bin', 'm17mes.bin', 'm18mes.bin', 'm19mes.bin', 'm20mes.bin', 'm21mes.bin', 'm22mes.bin', 'm23mes.bin', 'm24mes.bin', 'm25mes.bin', 'm26mes.bin', 'm27mes.bin']: # Список файлов с текстом
            f.seek(0,2)
            size = f.tell() # Конец файла
            self.data.append(("1.txt",0,size,"txt"))
        self.file = f

    def Unpack_PIC(self,f,w,h,size):
        src = iter(f.read(size)) # Сжатые данные
        f.close()

        output = bytearray(4096) # Распакованный файл

        try:
            while True:
                bits = bin(next(src))[2:].zfill(8)[::-1] # Управляющий байт, биты читаются справа налево
                for i3 in bits:
                    if i3 == "1": # Просто чтение 1 байта
                        output.append(next(src)) # Записываем в выходной файл

                    else: # Сжатый байты
                        byte1 = next(src)
                        byte2 = next(src)

                        offset = byte1 | ((byte2 & 0xF0) << 4)
                        repeat = (byte2 & 0x0F) + 3 # Правая половинка сколько прочитать байт байт 0F

                        len_output = len(output) # Узнаём длину распакованого файла
                        ref = len_output - ((len_output - 18 - offset) & 0xFFF)

                        for i in range(ref, ref+repeat):
                            output.append(output[i]) # Записываем в выходной файл

        except StopIteration: # Остановка так быстрей
            pass

        f2 = io.BytesIO(output[4096:])
        self.images.append(Image.frombuffer('RGB', (w,h), f2.read((w*h)*2), 'raw', 'BGR;15', 0, 1))
        f2.close()

    def Unpack_PIC2(self,f,w,h,iy):
        if iy == 3 or iy == 4: # Указываем какой картинки какая палитра
            number = 6 # Номер палитры, для разных картинок может использоватся одна палитра
        elif iy == 5 or iy == 6:
            number = 7
        else:
            number = 7

        f_image = Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1)
        f_image.putpalette(self.list_pal[number])
        self.images.append(f_image)

    def Unpack_TXT(self,f):
        data = [] # Список файлов
        fd = f.read(4)
        f.seek(0)
        pointer_size = struct.unpack(">H",f.read(2))[0] * 2 # Размер таблицы поинтеров
        size_pointer_text = struct.unpack(">H",f.read(2))[0] *2 # Размер таблицы поинтеров и текста в месте

        whole, rest = divmod(pointer_size,4) # Делит правельно сначало идёт целое число потом остаток # Количество поинтеров получаем
        #print("Количество поинтеров",whole,"Размер таблицы поинтеров и текста в месте",size_pointer_text)
        for i in range(whole):
            unclear = struct.unpack(">H",f.read(2))[0] #
            offset = struct.unpack(">H",f.read(2))[0] * 2 # Оффсет от начало текста
            if offset != 0:
                offset += 4 + pointer_size # Заголовок + таблица поинтеров
                data.append(offset)

        if fd in [b'\x002\x02b', b'\x00\x88\x05\x94', b'\x00\xa8\x06\r', b'\x00\xbc\n\xe6', b'\x00\xbe\tw', b'\x00\xc0\x06\xd7', b'\x00\xc4\x06\x88', b'\x00\xcc\x07G', b'\x00\xcc\x0bH', b'\x00\xda\x08\xde', b'\x00\xe0\x07\x1c', b'\x00\xe6\x07\x9d', b'\x00\xf0\n\x17', b'\x00\xf4\x08\x85', b'\x00\xf6\r\x15', b'\x00\xf8\x08\xc6', b'\x01\x04\n\xd9', b'\x01\x04\n\xe7', b'\x01\x0e\t\xfe', b'\x01\x1a\x11\x95', b'\x01\x1e\r\xf0', b'\x01\x1e\x0e\x8c', b'\x01(\x0e\xdd', b'\x01*\x0e(', b'\x010\x0f4', b'\x012\n\xc1', b'\x012\x0c\xb0', b'\x016\x0c?', b'\x01<\x0b\xcc', b'\x01Z\x11<', b'\x01j\x0f\xcb', b'\x01~\x13l', b'\x01\x86\x0e0', b'\x01\x86\x0e0', b'\x01\x88\x11\xf3', b'\x01\x8c\x0er', b'\x01\x8c\x13\xa9', b'\x01\xaa\x19\x00', b'\x01\xb4\x17\xe8', b'\x01\xc8\x18u', b'\x01\xce\x14\x82', b'\x01\xda\x12\xdc', b'\x01\xe6\x18\xbc', b'\x01\xe8\x1c\xb2', b'\x02"\x1d\xba', b'\x02f\x17m', b'\x02\xbc&5', b'\x02\xc8!\xd8', b'\x02\xca!\x16', b'\x03h*&', b'\x03\x800\xf9', b'\x03\x88+a', b'\x03\x90+\xcb', b'\x03\xc8.\xe3', b'\x03\xca.z', b'\x04\x0e4E', b'\x04t0n', b'\x04\xae=0', b'\x04\xb2?\xc8', b'\x04\xbcE\x83', b'\x04\xce9H', b'\x06\xa4[\x8a', b'\x06\xecO3', b'\x06\xf8Z\xce', b'\x07\x16P\x1d', b'\x07*e\x14', b'\x07\x80^=', b'\x08\nf\xcf', b'\x08Rbz', b'\x08dv\x10', b'\x08~c\x17', b'\x08\xe0f\xac', b'\x08\xf2v\xab', b'\tp~\x97', b'\tp~\x9a', b'\t\xa6\x84\x1b', b'\t\xc0\x81"', b'\n\x18\x863', b'\n\xa8\x8d%', b'\x0b\x08\x82Y', b'\x0b"\x80\xca', b'\x0b8\x87\x8e', b'\x0bl\x8a\xc8', b'\x0c8\x9d!', b'\x0cT\x9c\xa3', b'\x0cb\xa3\xe8']:
            text_encoding = "cp1251" # Русский текст

        elif fd in [b'\x002\x02h', b'\x00\x88\x06\\', b'\x00\xa8\x06\xbc', b'\x00\xbc\x0b3', b'\x00\xbe\no', b'\x00\xc0\x07\x9c', b'\x00\xc4\x07?', b'\x00\xcc\x08G', b'\x00\xcc\x0b\xb0', b'\x00\xda\t\xd1', b'\x00\xe0\x07\xfd', b'\x00\xe6\x08\x83', b'\x00\xf0\n\xff', b'\x00\xf4\tM', b'\x00\xf6\r\x89', b'\x00\xf8\t\x92', b'\x01\x04\x0bY', b'\x01\x04\x0bY', b'\x01\x0e\n\xd5', b'\x01\x1a\x12\x10', b'\x01\x1e\x0e\x8f', b'\x01\x1e\x0f\xdd', b'\x01(\x10H', b'\x01*\x0f\xce', b'\x010\x10\x93', b'\x012\x0b\xd7', b'\x012\r\xb4', b'\x016\r\x91', b'\x01<\x0c\xf5', b'\x01Z\x12\xd1', b'\x01j\x10L', b'\x01~\x15t', b'\x01\x86\x0f\xd4', b'\x01\x86\x0f\xd4', b'\x01\x88\x11\xa5', b'\x01\x8c\x0f\xc6', b'\x01\x8c\x14s', b'\x01\xaa\x18\xe9', b'\x01\xb4\x18\r', b'\x01\xc8\x1a\x05', b'\x01\xce\x16\xe9', b'\x01\xda\x147', b'\x01\xe6\x1ax', b'\x01\xe8\x1c\xb8', b'\x02"\x1fC', b'\x02f\x19s', b'\x02\xbc)Y', b'\x02\xc8%\xaf', b'\x02\xca%\x8f', b'\x03h,\xcc', b'\x03\x801\xdf', b'\x03\x88.\x05', b'\x03\x90.\xe3', b'\x03\xc83\x07', b'\x03\xca1\xf9', b'\x04\x0e7\xfe', b'\x04t7D', b'\x04\xae@\xbc', b'\x04\xb2E\xef', b'\x04\xbcH\x83', b'\x04\xce<\xbb', b'\x06\xa4^1', b'\x06\xecZS', b'\x06\xf8`\x9a', b'\x07\x16\\\x08', b'\x07*h\xc9', b'\x07\x80h\x96', b'\x08\no\x92', b'\x08Rj\xad', b'\x08d|\xed', b'\x08~kj', b'\x08\xe0o\x83', b'\x08\xf2\x80\xa2', b'\tp\x87t', b'\tp\x87w', b'\t\xa6\x90\xc9', b'\t\xc0\x8a<', b'\n\x18\x8f\x0c', b'\n\xa8\x93L', b'\x0b\x08\x8b\xb0', b'\x0b"\x8bL', b'\x0b8\x8eZ', b'\x0bl\x9e\xfa', b'\x0c8\xa8\x92', b'\x0cT\xa8\xd5', b'\x0cb\xae\x9b']:
            text_encoding = "shift-jis" # Японский текст

        elif fd in [b'\x002\x02+', b'\x00\x88\x05l', b'\x00\xa8\x06#', b'\x00\xbc\t=', b'\x00\xbe\x08\xaa', b'\x00\xc0\x06\xcb', b'\x00\xc4\x066', b'\x00\xcc\x07^', b'\x00\xcc\t\x98', b'\x00\xda\x08\xc1', b'\x00\xe0\x07\x00', b'\x00\xe6\x07{', b'\x00\xf0\t\x86', b'\x00\xf4\x086', b'\x00\xf6\x0bT', b'\x00\xf8\x087', b'\x01\x04\t\xce', b'\x01\x04\t\xd8', b'\x01\x0e\te', b'\x01\x1a\x0e\x86', b'\x01\x1e\x0cO', b'\x01\x1e\x0c\xf8', b'\x01(\r\\', b'\x01*\x0c\xb4', b'\x010\r\x9a', b'\x012\nX', b'\x012\x0b\xb1', b'\x016\x0bs', b'\x01<\x0b\x12', b'\x01Z\x0f\x85', b'\x01j\r\xf5', b'\x01~\x11y', b'\x01\x86\rW', b'\x01\x86\r]', b'\x01\x88\x0f5', b'\x01\x8c\r\xd9', b'\x01\x8c\x11#', b'\x01\xaa\x14g', b'\x01\xb4\x14\x89', b'\x01\xc8\x15\xfa', b'\x01\xce\x12\xce', b'\x01\xda\x11\xdd', b'\x01\xe6\x16O', b'\x01\xe8\x17\x8a', b'\x02"\x1a\xe7', b'\x02f\x16\xc8', b'\x02\xbc$\x1a', b'\x02\xc8\x1f\xed', b'\x02\xca\x1fg', b'\x03j&\xda', b'\x03\x80(\x8c', b"\x03\x88'\xcc", b'\x03\x90(\xae', b'\x03\xc8)\xc3', b'\x03\xca+2', b'\x04\x0e/\xd1', b'\x04v0\xd4', b'\x04\xae4\xd8', b'\x04\xb28\xc9', b'\x04\xbc<\x02', b'\x04\xce5D', b'\x06\xa4L\xd8', b'\x06\xecK\xc8', b'\x06\xf8Q\t', b'\x07\x16K\xb5', b'\x07*V$', b'\x07\x80W\xb6', b'\x08\n\\L', b'\x08R[\xa9', b'\x08dj4', b'\x08|\\V', b'\x08\xde_\xde', b'\x08\xf2l\x9f', b'\tpq\x8e', b'\trq\xad', b'\t\xa6y"', b'\t\xc0s\xd3', b'\n\x18x^', b'\n\xa8x\x0c', b'\x0b\x08y\x12', b'\x0b"w\xf4', b'\x0b8z\x94', b'\x0bl\x83\x1b', b'\x0c:\x8d\x92', b'\x0cT\x8eQ', b'\x0cd\x92J']:
            text_encoding = "big5" # Китайский текст
        else:
            print("Ошибка непонятная кодировка файла")

        txt = io.StringIO() # Виртуальный файл для текста
        for i in data:
            f.seek(i)

            ss = 0 # Количество текста
            while True: # Расчёт количества букв
                if f.read(1) == b'\x00':
                    break
                else:
                    ss += 1
            f.seek(i)
            fd = f.read(ss)

            try: # Исключения
                text = fd.decode(text_encoding) # Декодинг текста по указанной кодировке
            except :
                #print(i,ss) # Оффсет ошибки текста и его длина
                fd = fd.replace(b'\x81', b'\x30').replace(b'\xFB', b'\x30').replace(b'\xFE', b'\x30') # Меняем байт 0400TBL.BIN 0401TBL.BIN китайский текст
                text = fd.decode(text_encoding)

            txt.write(text+"\n") # Запись в текстовый файл
        txt.seek(0)
        self.text = txt.read()
        txt.close()

    def Unpack_TXT2(self,f):
        self.text = f.read().decode("shift-jis")