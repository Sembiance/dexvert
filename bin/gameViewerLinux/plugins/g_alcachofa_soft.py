#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Mortadelo y Filemón: La Sexta Secta. Operación Moscú              [ani]
# Mortadelo y Filemón: La Sexta Secta. El Escarabajo de Cleopatra   [ani]
# Mortadelo y Filemón: La Banda de Corvino. Balones Y Patadones     [ani, snd]
# Mortadelo y Filemón: La Banda de Corvino. Mamelucos a la romana   [ani, snd]
# Mortadelo y Filemón: Una Aventura de Cine. Edición Especial       [an0]
# Mortadelo y Filemón: El Sulfato Atómico                           [alg, svs, vhs]

import os, sys, io, struct
from PIL import Image, ImageSequence
import numpy as np
import io

NAME = "Alcachofa Soft"
TYPES_FILES = [('ani Images', ('*.ani')),('snd Sound', ('*.snd')),('an0 Images', ('*.an0')),('alg Images', ('*.alg')),('svs Images', ('*.svs')),('vhs Images', ('*.vhs'))]
FORMATS_FILES = ["ani","snd","an0", "alg", "svs", "vhs"]
GAMES = ["Mortadelo y Filemón: La Sexta Secta. Operación Moscú",
         "Mortadelo y Filemón: La Sexta Secta. El Escarabajo de Cleopatra",
         "Mortadelo y Filemón: La Banda de Corvino. Balones Y Patadones",
         "Mortadelo y Filemón: La Banda de Corvino. Mamelucos a la romana",
         "Mortadelo y Filemón: Una Aventura de Cine. Edición Especial",
         "Mortadelo y Filemón: El Sulfato Atómico"]

AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["ani",
                            "snd",
                            "an0",
                            "alg",
                            "svs",
                            "vhs"]
        self.sup_types = {"ani":2,
                          "snd":3,
                          "an0":2,
                          "alg":1,
                          "svs":1,
                          "vhs":2}
        self.images = []
        self.sound = None

    def open_files(self,files):
        self.data = files

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        size = data_res[2]
        format = data_res[3]
        f = open(name,"rb")
        f2 = io.BytesIO(f.read(size))
        f.close()

        if format == "ani":
            self.Unpack_ANI(f2)
        elif format == "snd":
            self.Unpack_SND(f2)
        elif format == "an0":
            self.Unpack_AN0(f2)
        elif format == "alg" or format == "svs":
            self.Unpack_ALG(f2)
        elif format == "vhs":
            self.Unpack_VHS(f2)

    def Unpack_ANI(self, f):
        type = f.read(4) # Тип
        if type != b'ANI\x00': # Проверка на картинку
            print("ЭТО НЕ КАРТИНКА",type)
            return(0) # Остановка скрипта

        size = struct.unpack("<I",f.read(4))[0] # Размер файла
        unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно
        unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно
        unclear_3 = struct.unpack("<I",f.read(4))[0] # Непонятно
        #print(mult_file,"Размер",size,unclear_1,unclear_2,unclear_3)
        unclear_4 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_5 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_6 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_7 = struct.unpack("<H",f.read(2))[0] # Непонятно
        #print("Непонятно",unclear_4,unclear_5,unclear_6,unclear_7)

        unclear_8 = struct.unpack("B",f.read(1))[0] # Непонятно
        number_pictures = struct.unpack("<I",f.read(4))[0] # Количество кадров
        unclear_9 = struct.unpack("B",f.read(1))[0] # Непонятно
        unclear_10 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_11 = struct.unpack("<H",f.read(2))[0] # Непонятно
        #print("Количество картинок",number_pictures)
        #print("Непонятно",unclear_8,unclear_9,unclear_10,unclear_11)

        for frame in range(number_pictures): # number_pictures
            unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_2 = struct.unpack("<H",f.read(2))[0] # Непонятно
            Coordinates_w, Coordinates_h = struct.unpack("<HH",f.read(4)) # Координаты картинок ?
            w, h = struct.unpack("<HH",f.read(4)) # Ширина и высота картинки
            #print("Непонятно",unclear_1,unclear_2)
            #print("Координаты картинок",Coordinates_w, Coordinates_h,"Ширина и высота",w, h,)

            size_color = struct.unpack("<I",f.read(4))[0] # Размер полотна с цветами, если картинка 24 бита надо на *3 (после таблицы кодов)
            #print("Размер полотна с цветами который надо прочетать",size_color)

            unclear_3 = struct.unpack("B",f.read(1))[0] # Непонятно
            unclear_4 = struct.unpack("B",f.read(1))[0] # Непонятно
            unclear_5 = struct.unpack("B",f.read(1))[0] # Непонятно
            unclear_6 = struct.unpack("B",f.read(1))[0] # Непонятно
            unclear_7 = struct.unpack("B",f.read(1))[0] # Непонятно
            image_format = struct.unpack("B",f.read(1))[0] # Формат картинки 0 это 24 бита, 1 это 8 бит
            #print("Формат картинки",image_format)
            #print("Непонятно",unclear_3,unclear_4,unclear_5,unclear_6,unclear_7)

            list_command = [] # Список команд
            for i in range(h):
                pos = f.tell()
                col_command = struct.unpack("<H",f.read(2))[0] # Количество команд на строчку
                fd = f.read(col_command*8)
                list_command.append((col_command,fd))

            #print("Начало данных полотна цветов",f.tell())
            if image_format == 1: # 8 бит
                bit = 1
                byte = b'\xFF' # Байты
            elif image_format == 0: # 24 бита
                bit = 3
                byte = b'\x00\xF8\x00' # Байты
            else:
                print("    Непонятный тип цвета",image_format_1,image_format_2)
                return(0)

            fd2 = f.read(size_color*bit) # Читаем полотно цветов
            f5 = io.BytesIO(fd2)

            if image_format == 1: # Палитра
                #print("Палитра",f.tell())
                Pal = b''
                for jj in range(256):
                    B = f.read(1)
                    G = f.read(1)
                    R = f.read(1)
                    Pal += R+G+B

                #print("  Прочитали палитру",f.tell())
            #print("Конец картинки",f.tell())

            f2 = io.BytesIO()
            fill = (w*h)*byte # Байты для заполнения фона картинки
            f2.write(fill)

            line_number = 0 # Номер строки картинки в высоту
            for i in list_command:
                #print("Количество команд на строчку",i[0])
                f3 = io.BytesIO(i[1]) # Данные команд 
                f2.seek(line_number*(w*bit)) # Переход на строчку

                for i in range(i[0]): # Выполняем команды
                    indentation = struct.unpack("<H",f3.read(2))[0] # Отступить от начало строчки картинки
                    col_colors = struct.unpack("<H",f3.read(2))[0] # Сколько прочетать цветов
                    offset = struct.unpack("<I",f3.read(4))[0] # Оффсет начало чтение байтов цветф
                    #print("Отступ на",indentation,"Сколько прочетать цветов",col_colors,"Оффсет",offset)

                    f5.seek(offset) # Переход на нужные цвета
                    Colour_byte = f5.read(col_colors*bit) # Читаем цвета
                    f2.seek(indentation*bit,1) # Отступить на байт
                    f2.write(Colour_byte)

                f3.close()
                line_number += 1 # Увеличиваем номер строки для перехода на новую строчку

            f2.seek(0)
            if image_format == 1: # 8 бит
                f_image = Image.frombuffer('P', (w,h), f2.read(w*h), 'raw', 'P', 0, 1)
                f_image.putpalette(Pal)

            elif image_format == 0: # 24 бита
                f_image = Image.frombuffer('RGB', (w,h), f2.read(w*h*3), 'raw', 'BGR', 0, 1)

            self.images.append(f_image)
            f2.close()
            f5.close() # Полотно с цветом
            #print()
        f.close()

    def Unpack_SND(self, f):
        type = f.read(4)
        if type != b'\x10\x00\x00\x00': # Проверка на звук
            print("ЭТО НЕ звук",type)
            return(0) # Остановка скрипта

        unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_2 = struct.unpack("<H",f.read(2))[0] # Непонятно
        frequency_1 = struct.unpack("<I",f.read(4))[0] # Частота звук
        frequency_2 = struct.unpack("<I",f.read(4))[0] # Частота звук
        unclear_3 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_4 = struct.unpack("<H",f.read(2))[0] # Непонятно
        size = struct.unpack("<I",f.read(4))[0] # Размер
        fd = f.read(size)
        #print("Частота",frequency_1,frequency_2,"Размер звука",size)
        #print("Непонятно",unclear_1,unclear_2,unclear_3,unclear_4)

        wav = b""
        wav += b"RIFF"
        wav += struct.pack("<I", size+44-8) # chunkSize размер файла-8
        wav += b"WAVE" # format WAVE
        wav += b"fmt " # subchunk1Id fmt 0x666d7420
        subchunk1Size = 16
        audioFormat = 1    # Формат звука 
        numChannels = 1    # Количество каналов
        sampleRate = frequency_1 # Частота файла
        byteRate = frequency_2   # Частота выхода звука, для расчёта длины звучания
        blockAlign = 2
        bitsPerSample = 8 # Битность звука 8 16 32
        wav += struct.pack("<IHHIIHH", subchunk1Size, audioFormat, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample)
        wav += b"data"
        wav += struct.pack("<I", size)
        wav += fd # Данные
        f2 = io.BytesIO(wav)
        self.sound = f2
        f.close()

    def Unpack_AN0(self, f):
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)
        type = f.read(4) # Тип архива
        if type in [b'\x01\x00\x00\x00', b'\x02\x00\x00\x00', b'\x03\x00\x00\x00', b'\x04\x00\x00\x00', b'\x05\x00\x00\x00', b'\x06\x00\x00\x00', b'\x07\x00\x00\x00', b'\x08\x00\x00\x00', b'\x09\x00\x00\x00']:
            pass
        else:
            print("ЭТО НЕ КАРТИНКИ",type,"Размер",end_f)
            return(0) # Остановка скрипта

        col = struct.unpack("<I",f.read(4))[0] # Количество файлов

        for i in range(col):
            f.seek(12,1) # Пропускаем 12 байта Заголовок
            w, h = struct.unpack("<HH",f.read(4)) # Ширина и высота
            b11 = struct.unpack("B",f.read(1))[0] # Битность картинки
            b12 = struct.unpack("B",f.read(1))[0] #
            #print("Ширина и высота",w, h, "Битность",b11, b12)

            if b11 == 8:
               col_byte = 1
               Pal = f.read(768) # Палитра
            elif b11 == 24:
               col_byte = 3
            elif b11 == 32:
                col_byte = 4
            else:
                print("Ошибка непонятная битность",b11)
                return(0) # Остановка скрипта

            f2 = io.BytesIO()
            while True:
                if f2.tell() == (w*h)*col_byte:
                    break

                bit = f.read(1)[0] # Управляющий байт
                if bit >> 7: # Тут будет бит 1 Это сжатые байты
                    f2.write(f.read(col_byte)*(bit - 127)) # Сколько раз повторить цвет

                else: # Тут будет бит 0 Это просто прочетать цветов
                    f2.write(f.read((bit+1)*col_byte)) # Прочетать цветов

            f2.seek(0)
            if b11 == 8:
                f_image = Image.frombuffer('P', (w,h), f2.read(w*h), 'raw', 'P', 0, 1) 
                f_image.putpalette(Pal)
            elif b11 == 24:
               f_image = Image.frombuffer('RGB', (w,h), f2.read(w*h*3), 'raw', 'BGR', 0, 1)
            elif b11 == 32:
                f_image = Image.frombuffer('RGBA', (w,h), f2.read(w*h*4), 'raw', 'BGRA', 0, 1)
            self.images.append(f_image)

            f2.close()
            f.seek(34,1) # Пропускаем 34 байта
        f.close()

    def Unpack_ALG(self, f):
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)

        type = f.read(4) # Тип
        unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно
        w, h = struct.unpack("<HH",f.read(4)) # Ширина и высота
        unclear_2 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_3 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_4 = f.read(112) # Непонятно
        w += 1
        h += 1

        f2 = io.BytesIO()
        while True:
            if f2.tell() == w*h:
                break

            byte = f.read(1)
            if byte[0] > 0xC0: # Сжатые данные
                f2.write(f.read(1)*(byte[0]-0xC0))

            else: # Просто записать байт
                f2.write(byte)

        #print("Конец распаковки",f.tell())

        check = f.read(1) # Проверка
        if check != b'\x0C':
            #print("Не равен байту 0C:",check)
            pass

        Pal = f.read(768) # Палитра

        f2.seek(0)
        f_image = Image.frombuffer('P', (w,h), f2.read(w*h), 'raw', 'P', 0, 1)
        f_image.putpalette(Pal)
        self.images.append(f_image)

        if f.tell() != end_f:
            print("Ошибка в конце файла есть ещё какието данные",f.tell())

        f.close()
        f2.close()

    def Unpack_VHS(self, f):
        f.seek(0)
        FLC_HEADER = [
            ["fsize",        1, "I", False],
            ["ftype",        1, "H", False],
            ["frames_num",   1, "H", True],
            ["width",        1, "H", True],
            ["height",       1, "H", True],
            ["depth",        1, "H", False],
            ["flags",        1, "H", True],
            ["speed",        1, "I", True],
            ["reserved1",    1, "H", False],
            ["created",      1, "I", True],
            ["creator",      1, "I", True],
            ["updated",      1, "I", True],
            ["updater",      1, "I", True],
            ["aspect_dx",    1, "H", True],
            ["aspect_dy",    1, "H", True],
            ["ext_flags",    1, "H", False],
            ["keyframes",    1, "H", False],
            ["totalframes",  1, "H", False],
            ["req_memory",   1, "I", False],
            ["max_regions",  1, "H", False],
            ["transp_num",   1, "H", False],
            ["reserved2",   24, "s", False],
            ["oframe1",      1, "I", False],
            ["oframe2",      1, "i", False],
            ["reserved3",   40, "s", False],]


        def parseflcchunks(f, offset, limit, level = 0, maxchunks = None,):
            def check_hdr(size, delta, name, offset):
                if delta < size:
                    raise EngineError("Incorrect FLC %s chunk at 0x{:08x}".format(
                        (name, offset)))

            chunks = []
            while True:
                if limit is not None:
                    if offset >= limit:
                        break
                if maxchunks is not None:
                    if len(chunks) >= maxchunks:
                        break
                chunk = {"offset": offset}
                temp = f.read(6)
                sz, tp = struct.unpack_from("<IH", temp)
                offset += 6

                chunk["size"] = sz
                chunk["type"] = tp
                delta = sz - 6
                if delta < 0:
                    raise EngineError("Incorrect FLC chunk at 0x{:08x}".format(
                        chunk["offset"]))

                raw_chunks = [
                    0x4, # COLOR_256
                    0x7, # DELTA_FLC
                    0xf, # BYTE_RUN
                    0xF100, # PREFIX_TYPE - mismaked, out destination ignore this
                ]
                #print("{}CHUNK 0x{:x}, size = {}".format("  "*level, tp, sz))
                # do not parse 3rd level 0x12 chunk
                if tp == 0x12 and level == 2:
                    tp = 0x4

                # parse chunks
                if tp in raw_chunks:
                    temp = f.read(delta)
                    offset += delta
                    chunk["data"] = temp
                elif tp == 0x12:
                    # PSTAMP
                    check_hdr(6, delta, "PSTAMP", offset)
                    temp = f.read(6)
                    delta -= 6
                    height, width, xlate = struct.unpack_from("<3H", temp)
                    offset += 6
                    offset, subchunks = parseflcchunks(f, offset, 
                        offset + delta, level + 1, 1)
                    chunk["chunks"] = subchunks
                    #print(subchunks)
                elif tp == 0xF1FA:
                    # FRAME_TYPE
                    check_hdr(10, delta, "FRAME_TYPE", offset)
                    temp = f.read(10)
                    delta -= 10
                    sub_num, delay, reserved, width, height = \
                        struct.unpack_from("<5H", temp)
                    offset += 10
                    chunk["delay"] = delay
                    chunk["width"] = width
                    chunk["height"] = height
                    offset, subchunks = parseflcchunks(f, offset,
                        offset + delta, level + 1, sub_num)
                    chunk["chunks"] = subchunks
                else:
                    raise Exception("Unknown FLC chunk type 0x{:04x} at 0x{:x08x}".\
                        format(tp, offset))

                chunks.append(chunk)

            return offset, chunks


        offset = 0
        hdr_keys = []
        hdr_struct = "<"
        for hnam, hsz, htp, hed in FLC_HEADER:
            hdr_keys.append(hnam)
            if hsz == 1:
                hdr_struct += htp
            else:
                hdr_struct += "%d" % hsz + htp

        header = {}
        temp = f.read(128)
        hdr = struct.unpack_from(hdr_struct, temp)

        offset += 128

        if len(hdr) != len(hdr_keys):
            raise EngineError("Incorrect FLC header {} != {}".format(
                len(hdr), len(hdr_keys)))
        for hid in range(len(hdr)):
            header[hdr_keys[hid]] = hdr[hid]

        if header["ftype"] != 0xAF12:
            raise EngineError("Unsupported FLC type (0x{:04x})".format(
                header["ftype"]))

        # check if not EGI ext
        if header["creator"] == 0x45474900:
            if header["ext_flags"] != 0:
                raise EngineError("Unsupported FLC EGI extension")

        # NOTE: we recreate FLC to avoid Pilllow bug
        #  1. remove 0xf100 chunk  (PREFIX, implementation specific)
        #  2. remobe 0x12 subchunk (PSTAMP) from 1st frame

        # read chunks
        _, chunks = parseflcchunks(f, offset, header["fsize"])

        f.seek(0)
        buf = io.BytesIO()
        buf.write(f.read(128)) # clone header
        for chunk in chunks:
            if chunk["type"] == 0xF100:
                continue
            elif chunk["type"] == 0xF1FA:
                rebuild = False
                nchunks = []
                nsz = 16 # I6H - type, size, sub_num, delay,
                         # reserved, width, height
                for schunk in chunk["chunks"]:
                    if schunk["type"] == 0x12: # detect mailformed PSTAMP
                        rebuild = True
                    elif rebuild:
                        nchunks.append(schunk)
                        nsz += schunk["size"]
                if rebuild:
                    buf.write(struct.pack("<I6H", nsz, 0xF1FA, len(nchunks),
                        chunk["delay"], 0, chunk["width"], chunk["height"]))
                    for schunk in nchunks:
                        f.seek(schunk["offset"])
                        buf.write(f.read(schunk["size"]))
                    continue
            # copy chunk
            buf.write(f.read(chunk["size"]))

        buf.seek(0)
        image = Image.open(buf)
        self.images = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(image)]
