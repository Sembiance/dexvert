#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Распаковка архивов .dat игры Восьмое путешествие Синдбада. Проклятие Карамогула

import os, sys, io, struct
from PIL import Image, ImageSequence
import numpy as np

NAME = "Восьмое Путешествие Синдбада: Проклятие Карамогула"
FORMATS_ARCHIVE = ['dat'] 
TYPES_ARCHIVE = [('Восьмое Путешествие Синдбада: Проклятие Карамогула', ('*.dat'))]
GAMES = ["Восьмое Путешествие Синдбада: Проклятие Карамогула"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app

        self.sup_formats = ['are',
                            'bin',
                            'flc',
                            'gif',
                            'hsa',
                            'pcx',
                            'rol',
                            'scr',
                            'sda',
                            'sdr',
                            'sds',
                            'sla']

        self.sup_types = {"are":1,
                          "bin":2,
                          "flc":2,
                          "gif":2,
                          "hsa":2,
                          "pcx":1,
                          "rol":2,
                          "scr":2,
                          "sda":2,
                          "sdr":2,
                          "sds":1,
                          "sla":2}
        self.images = []
        self.sound = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "dat":
            self.OpenArchiveDAT(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "scr":
            self.Unpack_SCR(io.BytesIO(self.file.read(size)),name)

        elif format == "sla":
            self.Unpack_SLA(io.BytesIO(self.file.read(size)))

        elif format == "sds":
            self.Unpack_SDS(io.BytesIO(self.file.read(size)), name)

        elif format == "pcx" or format == "gif":
            self.Unpack_PNG(io.BytesIO(self.file.read(size)))

        elif format == "flc":
            self.Unpack_FLC(io.BytesIO(self.file.read(size)))

        elif format == "bin":
            self.Unpack_BIN(io.BytesIO(self.file.read(size)))

        elif format == "are":
            self.Unpack_ARE(io.BytesIO(self.file.read(size)))

        elif format == "sda" or format == "sdr":
            self.Unpack_SDA(io.BytesIO(self.file.read(size)), name)

        elif format == "rol":
            self.Unpack_ROL(io.BytesIO(self.file.read(size)))

        elif format == "hsa":
            self.Unpack_HSA(io.BytesIO(self.file.read(size)))

    def OpenArchiveDAT(self,file):
        f = open(file,"rb")
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)

        type = f.read(32)
        if type != b'Sindbad resource file v1.02\x00\x00\x00\x00\x00': # Проверка на архив
            print("ЭТО НЕ АРХИВ",type)
            return(0)

        offset_tab = struct.unpack("<I",f.read(4))[0] # Начало таблицы
        col = struct.unpack("<H",f.read(2))[0] # Число файлов
        f.seek(offset_tab)

        for i in range(col):
            filename = f.read(32).split(b"\x00")[0].decode("cp1251").replace("\\\\","\\") # Имя файла
            format = filename.split(".")[-1].lower()
            size = struct.unpack("<I",f.read(4))[0]   # Размер
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            self.data.append((filename,offset,size,format))

        if end_f == 27558069: # Архив из папки MOVIE
            self.data.append(("intr.hsa",3686782,20848368,"hsa")) # Добавляем файл для распаковки

        self.file = f
        return 1

    def Unpack_SCR(self, f, name):
        (dirname, filename) = os.path.split(name) # Поиск палитры по имени файла

        number_folders = dirname[-1:] # Номер папки
        dlina_n = len(filename) # Номер файла
        if dlina_n == 11: # Если имя номера файла НЕ больше 9
            number_f = filename[-5:-4]
        elif dlina_n == 12: # Если имя номера файла больше 10
            number_f = filename[-6:-4]

        line_search = "pal"+number_folders+"\screen"+number_f+".pal" # pal1\screen1.pal Строчка для поиска палитры

        for i in range(len(self.data)): # Поиск индекса i    получаем индекс
            if self.data[i][0] == line_search: # Сверяет первый элемент списка с line_search
                offset = self.data[i][1] # Открываем файл палитры
                size = self.data[i][2]
                self.file.seek(offset)
                f2 = io.BytesIO(self.file.read(size)) # Палитра
                #print("Нашлось",self.data[i])
                break

            elif i+1 == len(self.data): # Если ненашлось палитры для файла scr3\screen1.scr
                #print("Нет палитры для файла",name,"Искали",line_search)
                for i in range(len(self.data)): # Поиск индекса i получаем индекс
                    if self.data[i][0] == "pal3\screen0.pal": # Сверяет первый элемент списка
                        offset = self.data[i][1] # Открываем файл палитры
                        size = self.data[i][2]
                        self.file.seek(offset)
                        f2 = io.BytesIO(self.file.read(size)) # Палитра
                        break
                break

        # Палитра
        Pal = b'' # Палитра
        for i in range(256):
            r,g,b = struct.unpack("BBB",f2.read(3))
            r = (r << 2) | (r >> 4)
            g = (g << 2) | (g >> 4)
            b = (b << 2) | (b >> 4)
            Pal += struct.pack("BBB", r,g,b)
        f2.close()


        col_blocks = struct.unpack("<H",f.read(2))[0] # Количество непонятных блоков с данными
        for i in range(col_blocks):
            col_4 = struct.unpack("<H",f.read(2))[0] # Сколько надо прочитать по 4 байт раз
            unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_2 = struct.unpack("<H",f.read(2))[0] # Непонятно
            fd = f.read(col_4 * 4) # Читаем по четыре байта нужное число раз

        f_pos = f.tell()
        col_f = struct.unpack("<H",f.read(2))[0] # Количество файлов

        for i in range(col_f):
            unclear1 = struct.unpack("<I",f.read(4))[0] # Непонятно возможно это координаты картинки на экране или нет
            unclear2 = struct.unpack("<I",f.read(4))[0] # Непонятно
            unclear3 = f.read(1)[0]  # Непонятно
            w,h = struct.unpack("<HH",f.read(4)) # Ширина и высота

            if w == 0xFFFF and h == 0xFFFF: # Если количество файлов было неправельно
                #print("    Это не картинка, позиция", f.tell()-13)
                unclear = f.read(1) # Непонятный байт надо его прочетать чтобы можно было расчитать конец файла
                break
                # Встречаются в файлах screen11.scr, screen2.scr, screen4.scr

            f_image = Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1)
            f_image.putpalette(Pal) # Добавляем палитру в картинку
            self.images.append(f_image)

    def Unpack_SDS(self, f, name):
        if name == "sys\\panel\\panel3.sds": # Если этот файл
            f_pal_name = "pal3\screen0.pal" # То палитра такая
        elif name == "sys\\panel\\panel4.sds":
            f_pal_name = "pal4\screen0.pal"
        else:
            f_pal_name = "pal1\screen0.pal"

        for i in range(len(self.data)): # Поиск индекса i    получаем индекс
            if self.data[i][0] == f_pal_name: # Сверяет первый элемент списка
                offset = self.data[i][1] # Открываем файл палитры
                size = self.data[i][2]
                self.file.seek(offset)
                f2 = io.BytesIO(self.file.read(size)) # Палитра
                break

        # Палитра
        Pal = b'' # Палитра
        for i in range(256):
            r,g,b = struct.unpack("BBB",f2.read(3))
            r = (r << 2) | (r >> 4)
            g = (g << 2) | (g >> 4)
            b = (b << 2) | (b >> 4)
            Pal += struct.pack("BBB", r,g,b)
        f2.close()

        w,h = struct.unpack("<HH",f.read(4)) # Ширина и высота
        f_image = Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1)
        f_image.putpalette(Pal) # Добавляем палитру в картинку
        self.images.append(f_image)    

    def Unpack_PNG(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_FLC(self, f):
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
            ["reserved3",   40, "s", False],
        ]


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

    def Unpack_SLA(self,f):
        ss_sound = 0 # Номер звукового файла
        f_wav = io.BytesIO() # Буффер звука
        f_Pal = io.BytesIO(b'\x00' * 768) # Создаю палитру

        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)

        type = f.read(4) # Индефикатор
        if type != b'SLA\x00': # Проверка
            print("ЭТО НЕ ФАЙЛ АНИМАЦИИ")
            return(0)

        unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно
        w,h = struct.unpack("<HH",f.read(4)) # Читаем ширину и высоту
        number_8 = struct.unpack("<H",f.read(2))[0] # Тут всегда записанно число 8
        unclear_3 = struct.unpack("<H",f.read(2))[0] # Непонятно
        #print("Непонятные байты", unclear_1, unclear_2, unclear_3)

        while True:
            f_pos = f.tell() # Позиция в файле
            if f_pos == end_f or f_pos+6 == end_f: # Остановка если дошли до конца файла
                # Если в конце файла остаётся только 6 байт 53 4C 46 00 00 00 то тоже останавливаемся
                break

            # Заголовок файлов 10 байт
            check_1 = f.read(4) # Проверочные байты SLB или SLF
            size = struct.unpack("<I",f.read(4))[0] # Размер файла
            tip = f.read(2) # Индефикатор формата блока чанга
            #print("Позиция в файле",f_pos, "Тип чанга", tip)

            # 53 4C 46 00 = b'SLF\x00'
            if check_1 == b'SLF\x00': # SLF. размером в 6 байт
                # Внутри могут быть 2 байта которые записаны ниже
                # 00 00, 01 00, 02 00, 03 00, 04 00, 05 00, 06 00, 00 03
                f.seek(f_pos)
                fd = f.read(6) # 4 байта заголовок 2 байта непонятно возможно говорит что дальше какоето количество чегото
                #print(check_1,"Размер равен 6 байт",fd)

            elif check_1 != b'SLB\x00': # Если заголовок файла не равен b'SLB\x00'
                f.seek(f_pos)
                fd = f.read(12)
                print("    ############ НЕПОНЯТНЫЕ БАЙТЫ позиция",f_pos, fd)
                return(0)

            # У всех ниже файлов первые 4 байта будут 53 4C 42 00 = b'SLB\x00'

            elif tip == b'\x64\x00': # Перед звуком, размер 14 байт всегда
                f.seek(f_pos)
                fd = f.read(size+10) # Основной файл

            elif tip == b'\x65\x00': # Звук
                # Несколько звуковых файлов есть в dialog.sla
                f.seek(f_pos+12)
                check_RIFF = f.read(4) # Проверочные байты

                f.seek(f_pos)
                f.read(10) # Заголовок и размер и индефикатор
                unclear = struct.unpack("<H",f.read(2))[0] # Непонятно Нет это не количество блоков звуков
                fd = f.read(size-2) # +10 Основной файл без заголовка размера, и непонятных 2 байт

                if check_RIFF == b'RIFF' and f_wav.tell() > 0: # Если есть индефикатор звука и размер буффера больше 0 то записываем из буффера файл на диск
                    ss_sound += 1  # Сохранение звука если есть ещё звуковой файл в анимации
                    #print("Сохранение файла из буффера звука номер", ss_sound)
                    f_wav.close() # Закрываем файл чтобы удалить ненужные данные
                    f_wav = io.BytesIO() # Буффер звука очишен

                f_wav.write(fd) # Запись в буффер

                # Запись блока звука, это неполностью файл нехватает первых 12 байт
                #print("Часть Звука",f_pos, size-2, "непонятный байт", unclear)

            elif tip == b'\x66\x00': # Конец звука, всегда размер 12 байт
                f.seek(f_pos)
                fd = f.read(size+10)
                #print("После звука Конец звука",f_pos, "размер",size,"\n")

            elif tip == b'\x05\x00': # Обновление палитры
                f.seek(f_pos+10)
                #f.read(4) # Заголовок SLB.
                #f.read(4) # Размер файла
                #f.read(2) # Индефикатор чанга

                # Встречается много измений палиры в файле intro.sla
                col_packet = struct.unpack("<H",f.read(2))[0] # Сколько обновить данных
                f_Pal.seek(0) # Переходим в начало палитры

                for i in range(col_packet):
                    color_number_offset = f.read(1)[0] * 3 # Номер цвета на который надо записывать новую палитру
                    col_read = f.read(1)[0] * 3 # Сколько дальше прочетать цветов. Если надо прочетать все цвета то стоит байт 00
                    if col_read == 0: # Если число равно 0 то прочитать все цвета
                        col_read = 768

                    f_Pal.seek(color_number_offset, 1) # Пропускаем байты Перейти на нужный цвет записи
                    f_Pal.write(f.read(col_read)) # Читаем нужное число цветов Записываем байты поверх старых
                    #print("Записать палитру на",color_number_offset,"Сколько прочетать цветов",col_read)

                f_Pal.seek(0) # Перейти на начало
                Pal = f_Pal.read() # Читаем палитру

                f.seek(f_pos+(10+size)) # Пропускаю оставшиеся непонятные байты
                # Всёровно в конце файла может остатся байты возможно для выравнивания

            elif tip == b'\x02\x00': # Сжатая картинка основная
                f.seek(f_pos)
                fd = f.read(size+10) # Основной файл

                f3 = io.BytesIO(fd) # Сжатый первый кадр
                f4 = self.Unpack_comp(f3, w,h,Pal) # Распаковка Возвращять виртуальный файл с распакованной картинкой
                f3.close()

            elif tip == b'\x06\x00': # Кадры с наложением
                f.seek(f_pos)
                #f.read(10) # Заголовок и размер и Индефикатор чанга
                fd = f.read(size+10) # Основной файл

                f5 = io.BytesIO(fd) # Сжатый файл
                self.Unpack_anim(w,h, f4, f5, Pal) # f4 картинка в памяти, f5 сжатый файл с анимацией
                f5.close()

            elif tip == b'\xC8\x00': # Текст
                f.seek(f_pos)
                fd = f.read(size+10) # Основной файл

            elif tip == b'\x00\x00': # Размер 0 байт Весь файл размером в 10 байт
                f.seek(f_pos)
                fd = f.read(size+10) # Основной файл
                # Почти во всех файлах встречается на оффсетах 24,34,44,60 за редким исключением
                #print("Ноль байт",size,f_pos)

            else: # Непонятные файлы
                f.seek(f_pos)
                #f.read(4) # Заголовок
                #f.read(4) # Размер
                #f.read(2) # Индефикатор чанга
                fd = f.read(size+10) # Основной файл
                #print(tip,mult_file[:-4],f_pos,size+10) # Показывает тип файла
                #print("Байты размер",size,f.tell())

        if f_wav.tell() > 0: # Запись звука из буффера если в буффере есть файл
            ss_sound += 1
            #print("Запись буффера звука конец файла",ss_sound)
            f_wav.close()

        f4.close() # Распакованная картинка в памяти для кадров анимации
        f.close()
        f_Pal.close() # Файл палитры

    def Unpack_comp(self, f,w,h, Pal): # Распаковка сжатия картинки
        f2 = io.BytesIO()
        output = bytearray() # Распакованный файл

        f.read(4) # Заголовок SLB.
        size_comp = struct.unpack("<I",f.read(4))[0] + 10 # Размер +10
        f.read(2) # Индефикатор чанга

        for i in range(h):
            f.seek(1, 1) # Сделал так чтобы увеличить скорость распаковки.

            sr = 0 # Распаковано байт
            while sr != w: # Остановка когда распакуется количество байт равная ширине картинки w
                byte = f.read(1)[0]
                if byte >> 7: # Прочитать байтов
                    output.extend(f.read(0x100 - byte)) # Сколько прочитать байтов
                    sr += 0x100 - byte

                else: # Повторить байт
                    output.extend(f.read(1)*byte)
                    sr += byte

        # В конце может остатся 1 один лишний байт.
        f2.write(output) # Если использовать output

        f2.seek(0)
        # Создание картинки
        f_image = Image.frombuffer('P', (w,h), f2.read(w*h), 'raw', 'P', 0, 1)
        f_image.putpalette(Pal) # Добавляем палитру в картинку
        self.images.append(f_image)
        return(f2)

    def Unpack_anim(self,w,h, picture, f, Pal):
        # picture несжатая картинка в памяти для наложения
        f.seek(0, 2)
        end_f = f.tell() # Конец файла
        f.seek(0)

        f.read(4) # Заголовок SLB.
        f.read(4) # Размер файла +10
        f.read(2) # Индивикатор файла чанга b'\x06\x00'
        number_lines = struct.unpack("<H",f.read(2))[0] # Количество изменёных строчек w
        #print("Количество изменёных строчек",number_lines)

        line_number = 0 # Номер строчки куда будут записыватся байты

        #for i in range(number_lines):
        while f.tell() != end_f: # Остановка когда достигним конца файла.
            number = struct.unpack("<H",f.read(2))[0] # Читаем число
            # Проверяет два старших бита в number 1100 0000

            if number & 0xC000 == 0x0000:
                #print("Количество команд на строчку",number, "Позиция",f.tell()-2)
                # Умножить номер строчки на ширину 
                picture.seek(line_number * w) # Переходим на начало строчки для записи байтов

            elif number & 0xC000 == 0xC000:
            # Биты индефикации (11)00 0000
                # Сколько пропустить строчек
                line_number += 0x10000 - number
                continue
                # Что делает эта команда, пропускает строчки на начало новой строчки,
                # Минемальный переход на 1 строчку вперёд.

            elif number & 0xC000 == 0x8000:
            # Биты индефикации (10)00 0000
                # Переходим на последний байт на строчки и записываем 1 байт из числа number
                picture.seek((line_number * w) + (w-1)) # Последний байт на строчке
                picture.write(struct.pack("B", number - 0x8000)) # Запись первого байта из числа number
                continue

            else: # 0100 0000 Нет такой команды
                print("#################################")
                print("    Ошибка Непонятное значение",number,"Позиция",f.tell()-2,"Кадр",frame_number,"\n")
                return(0)

            for i in range(number):
                picture.seek(f.read(1)[0], 1) # На сколько байт отступить от текущей позиции
                check = f.read(1)[0] # Прочитать или повторить байты

                if check >> 7: # Если бит 1000 0000
                    #print("Повторить байты",256 - check, "Позиция",f.tell()-2,"позиция в файле картинки",picture.tell())
                    picture.write(f.read(2)*(256 - check)) # 2 байта повторения Сколько повторить

                else: # Просто прочитать байты
                    #print("Прочитать байтов",check * 2, "Позиция",f.tell()-2,"позиция в файле картинки",picture.tell())
                    picture.write(f.read(check * 2)) # Сколько прочитать байт дальше

            # Прибавлять надо именно после строчки иначе будет ошибочно записыватся
            line_number += 1 # Переход на новую строчку

        f.close()
        picture.seek(0) # Чтение картинки

        # Создание картинки
        f_image = Image.frombuffer('P', (w,h), picture.read(w*h), 'raw', 'P', 0, 1)
        f_image.putpalette(Pal) # Добавляем палитру в картинку
        self.images.append(f_image)

    def Unpack_BIN(self, f):
        data = [] # Список файлов
        type = f.read(8) # Тип архива
        if type == b'SCRF1.00': # Проверка на архив
            #print("ЭТО НЕ картинка а файл срипта игры",type)
            return(0) # Остановка скрипта

        for i in range(len(self.data)): # Поиск индекса i    получаем индекс
            if self.data[i][0] == "sys\\floor.pal": # Сверяет первый элемент списка
                offset = self.data[i][1] # Открываем файл палитры
                size = self.data[i][2]
                self.file.seek(offset)
                f2 = io.BytesIO(self.file.read(size)) # Палитра
                break

        Pal = b'' # Палитра
        for i in range(256):
            r,g,b = struct.unpack("BBB",f2.read(3))
            r = (r << 2) | (r >> 4)
            g = (g << 2) | (g >> 4)
            b = (b << 2) | (b >> 4)
            Pal += struct.pack("BBB", r,g,b)
        f2.close()

        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)
        size = struct.unpack("<I",f.read(4))[0] - 52 # Оффсет для расчёта блока с непонятными байтами
        f.seek(52)

        f.seek(0)
        for i in range(13):
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            data.append(offset)

        data.append(end_f) # Для расчёта размеров файлов

        col = struct.unpack("<H",f.read(2))[0] # Сколько раз прочетать по 52 байта
        w = struct.unpack("<H",f.read(2))[0] # Ширина картинки

        for i in range(col):
            fd = f.read(52) # 26 пар по 2 байта

        # Расчёт размеров файлов с картинками
        data2 = [] # Список файлов
        for i in range(len(data)-1):
            size = data[i+1] - data[i] # Получаем размер файла
            data2.append((data[i], size))
            #print("Оффсет",data[i],"размер",size)

        # Делим размер файла блока на ширину картинки и получаем высоту картинки
        h, rest = divmod(size, w) # Делит правельно сначало идёт целое число потом остаток
        if rest != 0:
            print("ОШИБКА ДАННЫЕ РАЗДЕЛИЛИСЬ НЕПРАВЕЛЬНО",rest)

        for i in data2:
            f.seek(i[0])
            f_image = Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1)
            f_image.putpalette(Pal) # Добавляем палитру в картинку
            self.images.append(f_image)

    def Unpack_ARE(self, f):
        f2 = io.BytesIO()
        f.read(1284) # Пропускаем байты

        for i in range(100):
            f.read(2) # Пропускаем байты 02 00
            for i in range(640):
                f2.write(f.read(1)) # Так получаем картинку шириной 640 высотой 100
                f.read(1) # Пропускаем байт 00
            f.read(2) # Пропускаем байты 02 00
        f.read(1284) # Пропускаем байты

        # Создание кратинки
        f2.seek(0)
        w = 640
        h = 100
        f_image = Image.frombuffer('P', (w,h), f2.read(w*h), 'raw', 'P', 0, 1)
        f_image.putpalette(b'\x00\x00\x00\xFF\xFF\xFF') # Добавляем палитру в картинку
        self.images.append(f_image)

        f.close()
        f2.close()

    def Unpack_SDA(self, f, name):
        (dirname, filename) = os.path.split(name) # Поиск палитры по имени файла

        dictionary = {"cursor1.sda":"pal1\\screen0.pal", # Всёровно стрелки неправельного цвета, цвет должен быть как в заглавном меню
                  "cursor3.sda":"pal3\\screen0.pal",
                  "cursor4.sda":"pal4\\screen0.pal",
                  "m2_3left.sda":"pal3\\screen0.pal",
                  "m2_3righ.sda":"pal3\\screen0.pal",
                  "m2_4left.sda":"pal3\\screen0.pal",
                  "m2_4righ.sda":"pal3\\screen0.pal",
                  "man1.sda":"pal1\\screen0.pal",
                  "man1_3.sda":"pal3\\screen0.pal",
                  "man1_4.sda":"pal4\\screen0.pal",
                  "man2left.sda":"pal1\\screen0.pal",
                  "man2righ.sda":"pal1\\screen0.pal",
                  "man3.sda":"pal1\\screen0.pal",
                  "man3_3.sda":"pal3\\screen0.pal",
                  "man3_4.sda":"pal3\\screen0.pal",
                  "sindbad.sdr":"pal1\\screen0.pal"} # Словарь

        f_pal_name = dictionary[filename] # Достаём по ключу имя палитры
        #print("Имя палитры",f_pal_name)

        for i in range(len(self.data)): # Поиск индекса i    получаем индекс
            if self.data[i][0] == f_pal_name: # Сверяет первый элемент списка 
                offset = self.data[i][1] # Открываем файл палитры
                size = self.data[i][2]
                self.file.seek(offset)
                f2 = io.BytesIO(self.file.read(size)) # Палитра
                break

        Pal = b'' # Палитра
        for i in range(256):
            r,g,b = struct.unpack("BBB",f2.read(3))
            r = (r << 2) | (r >> 4)
            g = (g << 2) | (g >> 4)
            b = (b << 2) | (b >> 4)
            Pal += struct.pack("BBB", r,g,b)
        f2.close()


        data = [] # Список файлов
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        for i in range(col):
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size = struct.unpack("<I",f.read(4))[0] # Размер
            f_path = f.read(16).split(b"\x00")[0].decode("utf8").replace("\\\\","\\") # Имя файла
            data.append((f_path, offset, size))
            #print(f_path, offset, size)

        for i in data:
            f.seek(i[1])
            fd = f.read(i[2])

            # Распаковка сжатых данных
            f3 = io.BytesIO(fd) # Сжатые данные
            w, h = struct.unpack("<HH",f3.read(4)) # Ширина и высота
            f2 = io.BytesIO() # Для распаковки

            while f3.tell() != i[2]: # Остановка когда достигним конца файла.
                byte = f3.read(1)[0] # Байт управления

                if byte & 0xC0 == 0b11000000: # Повторить байты
                    f2.write(f3.read(1) * (byte & 0x3F)) # Сколько раз надо повторить байт 0011 1111
                else:
                    f2.write(struct.pack("B", byte)) # Просто записываем 1 байт

            f2.seek(0)
            f_image = Image.frombuffer('P', (w,h), f2.read(w*h), 'raw', 'P', 0, 1)
            f_image.putpalette(Pal) # Добавляем палитру в картинку
            self.images.append(f_image)
            f2.close()
            f3.close()

        f.close()

    def Unpack_ROL(self, f):
        for i in range(len(self.data)): # Поиск индекса i получаем индекс
            if self.data[i][0] == "pal1\\screen0.pal": # Сверяет первый элемент списка
                offset = self.data[i][1] # Открываем файл палитры
                size = self.data[i][2]
                self.file.seek(offset)
                f2 = io.BytesIO(self.file.read(size)) # Палитра
                break

        Pal = b'' # Палитра
        for i in range(256):
            r,g,b = struct.unpack("BBB",f2.read(3))
            r = (r << 2) | (r >> 4)
            g = (g << 2) | (g >> 4)
            b = (b << 2) | (b >> 4)
            Pal += struct.pack("BBB", r,g,b)
        f2.close()

        data = [] # Список файлов
        col = struct.unpack("<I",f.read(4))[0] // 4 # Получим количество файлов в таблице

        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)

        for i in range(col):
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            data.append(offset)
        data.append(end_f) # Для правельного расчёта размер файла

        data2 = [] # Список файлов
        for i in range(len(data)-1):
            size = data[i+1] - data[i] # Получаем размер файла
            data2.append((data[i], size))
            #print("Оффсет",data[i],"размер",size)

        for i in data2:
            f.seek(i[0])
            fd = f.read(i[1])

            f2 = io.BytesIO(fd) # Сжатые данные
            f3 = io.BytesIO() # Распакованная картинка
            w, h = struct.unpack("<HH",f2.read(4)) # Ширина и высота
            unclear = f2.read(4) # Непонятно всегда нули

            while f2.tell() != i[1]: # Остановка когда достигним конца файла.
                byte = f2.read(1)[0] # Байт управления

                if byte & 0x80 == 0b10000000: # Пропустить байтов
                    f3.write(b'\x00' * (byte & 0x7F)) # Сколько надо пропустить байтов 0111 1111

                elif byte & 0x40 == 0b01000000: # Повторить следующий байт
                    f3.write(f2.read(1) * (byte & 0x3F))

                else:
                    print("Ошибка неопянтно что делать", byte, "позиция", f2.tell())
                    break

            if f3.tell() != w*h:
                print("Ошибка распаковалось неправельное количество байт", f3.tell(), w*h, "Нужно ещё байт",(w*h) - f3.tell())

            f3.seek(0)
            f_image = Image.frombuffer('P', (w,h), f3.read(w*h), 'raw', 'P', 0, 1)
            f_image.putpalette(Pal) # Добавляем палитру в картинку
            self.images.append(f_image)
            f3.close()
            f2.close()
        f.close()

    def Unpack_HSA(self, f):
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)

        w, h = struct.unpack("<II",f.read(8)) # Ширина и высота

        while True:
            size = struct.unpack("<I",f.read(4))[0] # Размер блока
            if size == 0xFFFFFFFF and f.tell() == end_f:
                break

            fd = f.read(size) # Сжатые данные

            # Конвертировать палитру
            f2 = io.BytesIO(f.read(768))
            Pal = b'' # Палитра
            for i in range(256):
                r,g,b = struct.unpack("BBB",f2.read(3))
                r = (r << 2) | (r >> 4)
                g = (g << 2) | (g >> 4)
                b = (b << 2) | (b >> 4)
                Pal += struct.pack("BBB", r,g,b)
            f2.close()

            fd_2 = self.Comp(fd) # Возвращяет распакованные данные
            f2 = io.BytesIO(fd_2)
            f_image = Image.frombuffer('P', (w,h), f2.read(w*h), 'raw', 'P', 0, 1)
            f_image.putpalette(Pal) # Добавляем палитру в картинку
            self.images.append(f_image)
            f2.close()

        f.close()

    def Comp(self, fd):
        src = iter(fd) # Сжатые данные Итерация
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

                        offset = len_output - ((len_output - 18 - offset_buffer) & 0xFFF) 
                        ###############################
                        # offset это оффсет начало чтения байтов, col сколько прочетать байт

                        len_byte = len_output - offset # Получаем количество байт доступное с конца файла

                        if len_byte >= col: # Если количество байт в конце файла больше чем нужно надо взять, просто читаем нужное число байт сразу
                            output.extend(output[offset:offset+col]) # Записываем в выходной файл последовательность байт

                        else:
                            # Время распаковки 0:00:03  3.484 sec
                            #for i in range(offset, offset+col):
                                #output.append(output[i]) # Записываем в выходной файл

                            # Время распаковки 3.266 sec
                            output.extend((output[offset:offset+len_byte]*((col//len_byte)+1))[:col])
                            # Притоком расчёте умножаем только на необходимое число раз

        except StopIteration: # Остановка так быстрей
            pass
            # Остановка если кончились байты в итерации, так значительно быстрей чем вести подсчёт каждого прочтенного байта в сжатом файле
        return(output[4096:])