#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# The Simpsons Virtual Springfield

import os, sys, io, struct
from PIL import Image
import numpy as np
import zlib

NAME = "The Simpsons Virtual Springfield"
TYPES_FILES = [('vsa Images', ('*.vsa')),('vsb Images', ('*.vsb')),('vs3 Images', ('*.vs3'))]
FORMATS_FILES = ["vsa","vsb","vs3"]
GAMES = ["The Simpsons Virtual Springfield"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["vsa",
                            "vsb",
                            "vs3"]

        self.sup_types = {"vsa":2,
                          "vsb":1,
                          "vs3":2}
        self.images = []
        self.sound = None
        self.fwav = io.BytesIO() # Соединенные звуки
        self.f2 = io.BytesIO() # Распакованная картинка VS3 для наложения кадра
        self.Pal = "" # Палитра для наложения VS3

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

        if format == "vsa":
            self.Unpack_VSA(f2,name)
        elif format == "vsb":
            self.Unpack_VSB(f2)
        elif format == "vs3":
            self.Unpack_VS3(f2)

    def Unpack_VSA(self, f,name):
        dirname, filename = os.path.split(name)
        ss = 0 # Номера картинки Нужно чтоб исправить ошибку в файле 109_11F.VSA
        f.seek(0,2)
        end_f = f.tell()
        f.seek(0)

        type = f.read(4)
        if type != b'VSA_': # Проверка
            print("ЭТО НЕ КАРТИНКИ",type)
            return(0)

        PalA = bytearray(f.read(1024))
        for i in range(3, 4*256, 4):
            if i == 63: # Номер цвета прозрачности 15   59
                PalA[i] = 0

            else: # Специально записано FF чтоб было видно картинку
                PalA[i] = 255

        PalA = tuple(tuple(PalA[i*4:i*4+4]) for i in range(256)) # Получаем список в виде чисел

        while f.tell() != end_f: # Остановка когда достигним конца файла.
            tip = struct.unpack("<H",f.read(2))[0] # Тип файлов
            if tip == 64 or tip == 256: # Сжатая картинка
                ss += 1
                unclear = struct.unpack("<I",f.read(4))[0] # Непонятно может тут 2 числа по 2 байта
                w,h = struct.unpack("HH",f.read(4)) # Ширина высота
                size = struct.unpack("<I",f.read(4))[0] # Размер сжатых данных
                #print(w,h,"Шир Выс,Размер сжатых данных",size)
                #print("Позиция",f.tell()-2,"Тип",tip,"Непонятно",unclear)
                f.read(18) # Всегда нули

                if size == 0: # Если размер сжатых данных равен нулю то начать сначало
                    continue

                if filename == "109_11F.VSA": # Сделано чтоб исправить ошибку в файле 109_11F.VSA
                    if ss == 4: 
                        w = 320
                        h = 155

                    elif ss == 5:
                        w = 208
                        h = 126

                    elif ss == 6:
                        w = 88
                        h = 142

                    elif ss == 7:
                        w = 64
                        h = 112

                    elif ss == 8:
                        w = 72
                        h = 70

                    elif ss == 9:
                        w = 48
                        h = 45

                    elif ss == 10:
                        w = 48
                        h = 19

                    elif ss == 11:
                        w = 8
                        h = 1

                size_comp = f.tell()+size # Узнаем конец сжатых данных

                f2 = io.BytesIO()
                while True:
                    if f.tell() == size_comp: # Конец файла
                        break

                    compr = f.read(1)[0] # Байт управления

                    #if compr & 0x80 == 0x80:
                    if compr >= 0x80: # Если левый бит 1
                        f2.write(f.read(1) * (257 - (compr))) # Читаем байт который надо повторить

                    else: # Байт не сжат
                        f2.write(f.read(compr+1)) # Читаем байты

                f2.seek(0)
                f_image = Image.new("RGBA", (w, h))
                f_image.putdata(tuple(PalA[number] for number in f2.read(w*h)))
                self.images.append(f_image) # Список в виде чисел
                f2.close()

            elif tip == 128: # Звук
                f.read(8) # Всегда нули
                size = struct.unpack("<I",f.read(4))[0] # Размер файла
                f.read(18) # Всегда нули
                self.fwav.write(f.read(size))

            else:
                print("Не понятно какой тип ",tip,"позиция",f.tell()-2)
                break

        self.Unpack_NEW_WAV()
        f.close()

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
            byteRate = 22050   # Частота выхода звука, для расчёта длины звучания
            blockAlign = 2
            bitsPerSample = 8 # Битность звука
            wav += struct.pack("<IHHIIHH", subchunk1Size, audioFormat, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample)
            wav += b"data"
            wav += struct.pack("<I", size)
            wav += fd # Данные
            f3 = io.BytesIO(wav)
            self.sound = f3
            self.fwav = io.BytesIO() # Чистим память

    def pal_data(self): # Палитра
        pal_data = b'x\x9cc``\xd8\xcf\x00\xc2\xfb\xc1\xd4~0\xeb\x00\x10\xdc9\xb0\xec\xd4\x07\x06Tp\xee\xce\xe3\xd5\xabWs\xef2`\x90V^\xba\xf4\xff\x94\xaeg\xcd\xf9g\x8bB\xb6$Z\xcc\x0e\x90m\xb2g\xca\xfc\xdd\x7f88\xfa\xff\x8f\xf3\xcc\xcf\x9f\xff\xdf\x18\xe3\xf1\x1f\xac\x8b\x87\x81\x81\x9f\x8bUTTTXQHA\x86WNNNYH\xceL\\\xdcXI\xc6V\x8b\xd5\xcdZ\xdc\xc7X&\xcaP8DR\xc0_D\xc4G@>[F\xa6H\x92/\x8f\x83/]\x84\xa1S\x9d\xa1\xceE\xb2\xdeU\xad\xd3Rm\xb2\xa7\xe1R/\xe5\xb9\x91\n\x8bb\xf4\xb6\xa5*\xaf,f\xdb\xe5\xc7p\xc6\x95\xfd\xa45\xc3zk\xe3\x95bFG\x99\xd4\xef\xb1j>\xe3\xe0}\xc7\xc2\xb2\x99A\xa8\x9aA=\xcb\xd44\xdb\xc4\xaa\xd0C/\xd5E1\xdaK\xae*Cuz\x93Na\xbfC\xd0\x820\x9fR\x1b\xe5bC\xe9&U\x86`}\x86\x08WA\x17\x1b\x0e\x0bG>S\x1f\tCO\x0e}S\x06##\x06k#\x06\x139\x06\x19\x19fI\x19.e]\x06y\x0b&\xee\x08\x19\xceP\x13\x06+~\x069>\x06)\r\x06\x069K9ccc777C\x970M\xafd\x93\x80\x02\xdd\xf0"\xe5\xa4\x99\xea&\xab\x18\xccN\xb2f\xdfbH}\xc5\x19\xf7\x8d\xd5\xeb\xbfh\xcf\x19\x86\xfa\xb5\x12\x8b\x9b\x04\xebs\xa2&\xf7\x94L\x9c\xd9\xd9\xbf\xa2\xafj\xd5\x84\t\x13f\xcf\x9e\xbdh\xd1\xa2\x15+V\xac\x9d\xbe{{\xcf\xdee\x99\xfb**\x1eE\xc5^\xf6\xafX_\x94\xd6\\PP\x10\x1d\x1d]\xe0\xef_\xe3\xee\xde\xea\xef69)\xa9\xaf bW\x9e\xd7\x9e\xba\xa4\xed\xd3\xb2/\xcf*z\xd7^\xf9iF\xf7\xef\xe5\xb5\xff\x17\xc7\xfe\xdf\x9b\xf8\xe1\xa2\xff\xff\x87N\x7f\x1f\xe6\xfc\xbf\xdc\xf1\xff\xd0\xdc\xaf\xdb\x16\xfc_\xb5\xe3\xfd\x8c\xad\xff{\xd6\xfdoZ\xf0\xbf~\xfe\xff\x8a\xdeO\x99]\xff\xc3\xbb\xfeGU}\xf6\xa9\xf9bS\xf7\xdf \xe2\xbfP\xc5q\xb1\xac\xa5\xe6\xd3\xda]\xfb\x92\xddz\xca,\xd3\x02m\x93\x9c\xd43\xfc\xd4\x9d\xd3\xb9\xb3\x03\x18\x9a\x19D\xaa\nO\xac\x9drt\xe7\xdc3;\x96\x9c\xd8\xbdv\xff\x05`\x1a\xb9~\xfd\xfa\x91KON\x9f\xf9pz\xeb\x8b\xf5\x9b^\xf5\xce\xf8\xefw\xe6\xbf\xd6\xde\xff\xb5_\xfe\xbf|\xf9\xeb\xff\xff\xffO\xff\xdc|\xf0\xe7\xfc\xe7\xbbG>\xdd\xde\xf8\xff\xdb\x96\xff\xe7\xae\xff?\xf5\xe1E\xe7\xdd\x8b[\xfav\xcd\xefY~ \xb3\xe9t\xc6\x81\x03\xa6\x0f7I?\x9e\xca\xf1p:\xcb\xff^\x96\xffej?\x92\xc4\xff\x87\xb1\xfc\xf7\xe1z\x15\xac{7)\xe4F}\xd8\xff\xda\x88\x97\x8b\\\xce\xbdr^xO\xbat/\xc3\xff\x13L\xff\x9f1\x10\t\xfe\xff\xfe\xb0`\xc1\x92\x86\x86\x06Pj\xfc\xcf\xf0\x1fL\xfd\x07\xb3\x80\x00\x00P\xf8D\xaf'
        return(zlib.decompress(pal_data))

    def Unpack_VSB(self, f):
        Pal = self.pal_data() # Если понадобится внешняя палитра
        f.seek(0,2)
        end_f = f.tell() # Узнаёт конец файла
        f.seek(0)

        type = f.read(4)
        if type != b'VSB_': # Проверка
            print("ЭТО НЕ ЗАДНИЙ ФОН",type)
            return(0)

        f.seek(16)
        w,h = struct.unpack("HH",f.read(4)) # Ширина и Высота
        #print("Ширина и высота",w,h)
        f.seek(132) # Начало сжатых данных 132

        f2 = io.BytesIO()
        while True:
            if f2.tell() == w*h: # Остановить распаковку
                break

            byte = f.read(1) # Байт управеления

            #if byte[0] & 0xC0 == 0xC0: # Проверяет два бита в байте слева
            if byte[0] >= 0xC0: # Повторяет байты
                f2.write(f.read(1)*(byte[0] - 0xC0)) # Повторить байт Количество повторений

            else: # Если байт не сжат прочто запись
                f2.write(byte)

        #print("Конец распаковки",f.tell())

        posf = f.tell()
        ostatok = end_f - posf # Проверяем если в конце файла остались ещё байты 768 то это палитра
        unclear = f.read(1)[0] # Непонятный байт всегда 0C В одной картинки 705_04.VSB нет этого байта

        f.seek(posf)
        check = f.read(4) # Байты проверки
        #print(posf,"Осталось в конце файла байт",ostatok,"Непонятный байт 0x"+hex(unclear)[2:].rjust(2, '0').upper())

        if ostatok == 768 or ostatok == 769: # Есть палитра внутри файла
            if ostatok == 769: # Пропускаем непонятный байт 0C
                posf += 1

            f.seek(posf)
            Pal = b'' # Палитра
            for i in range(256):
                Pal += f.read(3)

        elif check == b'VSB_':
            #print("Тут есть ещё файл VSB Осталось в конце файла байт",ostatok)
            # Непонятная палитра ?
            # Для кратинки используется внешняя палитра MASTER.VSP
            # Используется внешняя палитра pal_data
            pass

        else:
            print("НЕПОНЯТНО №№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№")

        f2.seek(0)
        f_image = Image.frombuffer('P', (w,h), f2.read(w*h), 'raw', 'P', 0, 1) 
        f_image.putpalette(Pal)
        self.images.append(f_image)
        f2.close()
        f.close()

    def Unpack_VS3(self, f):
        self.Pal = self.pal_data() # Если понадобится внешняя палитра

        f.seek(0,2) # Перейти на конец файла
        end_f = f.tell() # Узнаёт длину файла
        f.seek(0)

        unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно Размер файла неправельный
        type = f.read(2) # Индефикатор 12 AF
        if type != b'\x12\xAF':
            print("ЭТО НЕ ФАЙЛ анимации",type)
            return(0)

        Frames = struct.unpack("<H",f.read(2))[0] #	Число фреймов, максимум 4000. Не включая кольцевой фрейм.
        w,h = struct.unpack("HH",f.read(4)) # Ширина и высота
        #print("Ширина и высота картинки",w,h,"Непонятные байты",unclear_1)

        # Заголовок занимает 128 байт
        f.seek(128)

        while f.tell() != end_f: # Читаем до конца файла
            pos = f.tell()
            size = struct.unpack("<I",f.read(4))[0] # Размер Неправельный размер для типа чангов FA F1
            tip = f.read(2) # Тип файла FA F1 или 22 56 (Звук)

            #print("Позиция",pos,"Размер",size, "Тип блока", " ".join("{:02x}".format(x) for x in tip).upper())

            if tip == b'\xFA\xF1': # Это начало чанга размером в 16 байт его надо пропустить 
                f.seek(pos)
                f.read(16)
                #print("Начало чанга FA F1 позиция",pos,HEX)
                #print(HEX)
                #f.seek(pos+16) # Пропускаем байты

                # Чанг читается так 
                # 4 байта должен быть размер со всеми файлами но почемуто размер неправельный 
                # 2 байта индефикатор FA F1
                # 2 байта количество файлов 01 00
                # 8 байт нули 00 00 00 00 00 00 00 00
                # Пример DA 3D 00 00 FA F1 01 00 00 00 00 00 00 00 00 00
                # b'\x10\x00\x00\x00\xFA\xF1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' Это пустой заголовок файла
                continue

            elif tip == b'\x0F\x00': # Сжатая картинка Находится в чанге FA F1
                #print("Распаковка картинки")

                while self.f2.tell() != w*h: # Остановка когда вся картинка распаковалась
                    col = f.read(1)[0] # Количество команд для распаковки одной строчки по ширине картинки
                    for i in range(col):
                        byte = f.read(1)[0] # Байт управления

                        if byte >= 0x80: # Просто чтение байт
                            self.f2.write(f.read(0x100 - byte))

                        else: # Повторение следующего байта
                            self.f2.write(f.read(1) * byte)
                self.f2.seek(0)
                f_image = Image.frombuffer('P', (w,h), self.f2.read(w*h), 'raw', 'P', 0, 1)
                f_image.putpalette(self.Pal) # Добавляем палитру в картинку
                self.images.append(f_image)

                #if f.tell() != pos+size:
                    #print("Позиция сейчас и позиция после пропуска сжатия", f.tell(), pos+size, "разница между ними в байт",(pos+size)-f.tell())
                    # Разница в 1 байт

                f.seek(pos+size) # Пропускаем сжатые файлы так как в файле FOX.VS3 и CREDITP.VS3 после сжатия стоит 1 ненужный байт он портит алгоритм чтения файлов
                #print("Позиция после распаковки картинки",f.tell())

            elif tip == b'\x22\x56': # Это файл звука
                f.seek(10, 1) # Пропускаем байты от текущей позиции Байты нули
                self.fwav.write(f.read(size-16)) # Записываем данные звука, минус заголовок
                #print("Звук начало",pos, "позиция после звука",f.tell(),"размер",size)

            elif tip == b'\x20\x00': # Анимация наложения
                f.seek(pos)
                fd = f.read(size)
                self.overlay(fd, size) # Наложение на картинку

            else:
                print("    Ошибка непонятный тип блока позиция",pos,":0x"," ".join("{:02x}".format(x) for x in tip).upper())
                break

        # Звук
        if self.fwav.tell() > 0: # Записать звука если размер файла больше 0
            self.Unpack_NEW_WAV()
        f.close()
        self.f2 = io.BytesIO() # Очиска картинки

    def overlay(self, fd, end_f):
        f = io.BytesIO(fd)
        self.f2.seek(0)

        w = 640 # Тут всегда
        h = 480
        line_number = 0 # Номер строчки где сейчас находимся в файле, куда будут записыватся байты

        size = struct.unpack("<I",f.read(4))[0] # Размер файла целиком
        tip = f.read(2) # Тип блока чанга 20 00

        col_h = struct.unpack("<H",f.read(2))[0] # Количество изменёных строчек по высоте картинки
        #print("Количество изменёных строчек по высоте картинки", col_h,"\n")
        #print("###################")

        old_byte_1 = b'\x00' # Предпоследний байт.
        old_byte_2 = b'\x00' # Последний байт.

        # Надо читать файл до конца так как команды типа elif number & 0xFE00 == 0xFE00: идёт возврат к началу for но это неправельтно так как мы ещё неизменили строчку по высоте картинки
        while f.tell() != end_f: # Остановка когда достигним конца файла.
            #print("\nПозиция",f.tell())
            number = struct.unpack("<H",f.read(2))[0] # Читаем число
            # Количество команд которое надо выполнить чтобы изменить данные на одной строчки по ширине картинки.

            # Проверяет два старших бита в number 1100 0000
            #if number & 0xC000 == 0x0000:
            # Биты индефикации (00)00 0000
            if number <= 255: # Cколько команд надо выполнить
                #print("Количество команд на строчку",number, "Позиция",f.tell()-2)
                # Получаем оффсет нужной строчки w, Умножить номер строчки на ширину
                # Умножить номер строчки на ширину 
                self.f2.seek(line_number * w) # Переходим на начало строчки для записи байтов
                #print("Начать со строчки",line_number ,"на оффсете",line_number * w)
                # Максимальное количество команд 16383(3FFF)

            # Команда выполняется
            #elif number & 0xC000 == 0xC000:
            # Биты индефикации (11)00 0000
            elif number & 0xFE00 == 0xFE00: # Сколько пропустить строчек
                line_number += 0x10000 - number
                #print("Сколько пропустить строчек", 0x10000 - number, "Позиция",f.tell()-2)
                continue
                # Что делает эта команда, пропускает строчки на начало новой строчки,
                # Минемальный переход на 1 строчку вперёд.

            # Проверить выполняетсяли это команда Из РОЗОВОЙ ПАНТЕРЫ
            #elif number & 0xC000 == 0x8000:
            # Биты индефикации (10)00 0000
            elif number & 0xFF00 == 0x8000: # Переходим на последний байт на строчки и записываем 1 байт из числа number
                # Это каманда некогда недолжна сработать так как картинки всегда разрешением 640
                print("    ПРОВЕРИТЬ КОМАНДУ записи в последний байт строчки")
                self.f2.seek((line_number * w) + (w-1)) # Последний байт на строчке
                self.f2.write(struct.pack("B", number - 0x8000)) # Запись первого байта из числа number
                continue

            else: # 0100 0000 Нет такой команды
                print("#################################")
                print("    Ошибка Непонятное значение", number, "Позиция", f.tell()-2, "\n")
                return(0)

            #print("Количество команд на одну строчку W по ширине картинки", number)

            for i in range(number): # Выполнение команд
                number = f.read(1)[0] # Байт команд
                #print("Позиция", f.tell()-1, "байт", hex(number))

                version = number >> 4
                #print("Сколько раз повторить", version)

                flag_skip_byte = (number >> 3) & 1 # Проверка на бит 0000 1000
                #print("Пропускаем байты или нет", flag_skip_byte)

                if flag_skip_byte: # Если флаг равен 1 заходим
                    skip = f.read(1)[0] * 4 # Сколько пропустить байт
                    self.f2.seek(skip, 1) # Пропускаем байты от текущей позиции

                team_number = number & 0b00000111 # Номер команды
                #print("Номер команды", team_number)

                if team_number == 0:
                    if version == 0:
                        old_byte_1 = f.read(1) # Записываем байт в старые байты

                    elif version <= 15:
                        byte = f.read(1) # Читаем байт
                        self.f2.write(byte * (version * 4))
                        old_byte_1 = byte # Предпоследний байт

                elif team_number == 1:
                    if version == 0:
                        pass

                    elif version <= 15:
                        self.f2.write(old_byte_1 * (version * 4))

                elif team_number == 2: # Команда нечего не делает
                    pass

                elif team_number == 3:
                    if version == 0:
                        self.f2.write((old_byte_1 + old_byte_2) * 2)

                    elif version == 1:
                        self.f2.write(old_byte_1)
                        self.f2.write(old_byte_2)
                        self.f2.write(old_byte_1 * 2)

                    elif version == 2:
                        self.f2.write(old_byte_1+old_byte_2+old_byte_2+old_byte_1)

                    elif version == 3:
                        self.f2.write(old_byte_1)
                        self.f2.write(old_byte_2 * 3)

                    elif version == 4:
                        self.f2.write(old_byte_1 * 2)
                        self.f2.write(old_byte_2 * 2)

                    elif version == 5:
                        self.f2.write(old_byte_1 * 3)
                        self.f2.write(old_byte_2)

                    elif version == 6:
                        self.f2.write(old_byte_1 * 2)
                        self.f2.write(old_byte_2)
                        self.f2.write(old_byte_1)

                    # Команду 7 перенёс ниже, скорей всего она не используется.

                    elif version == 8:
                        self.f2.write((old_byte_2+old_byte_1) * 2)
     
                    elif version == 9:
                        self.f2.write(old_byte_2+old_byte_1+old_byte_2+old_byte_2)

                    elif version == 10:
                        self.f2.write(old_byte_2+old_byte_1+old_byte_1+old_byte_2)

                    elif version == 11:
                        self.f2.write(old_byte_2)
                        self.f2.write(old_byte_1 * 3)

                    elif version == 12:
                        self.f2.write(old_byte_2 * 2)
                        self.f2.write(old_byte_1 * 2)

                    elif version == 13:
                        self.f2.write(old_byte_2 * 3)
                        self.f2.write(old_byte_1)

                    elif version == 14:
                        self.f2.write(old_byte_2+old_byte_2+old_byte_1+old_byte_2)

                    elif version in [7, 15]: # Скорей всего это команда не используется.
                        self.f2.write(b'\x00\x00\x00\x00')

                elif team_number == 4:
                    if version == 0:
                        byte = f.read(1)
                        self.f2.write((old_byte_1 + byte) * 2)
                        old_byte_2 = byte

                    elif version == 1:
                        byte = f.read(1)
                        self.f2.write(old_byte_1)
                        self.f2.write(byte)
                        self.f2.write(old_byte_1 * 2)
                        old_byte_2 = byte

                    elif version == 2:
                        byte = f.read(1)
                        self.f2.write(old_byte_1)
                        self.f2.write(byte * 2)
                        self.f2.write(old_byte_1)
                        old_byte_2 = byte

                    elif version == 3:
                        byte = f.read(1)
                        self.f2.write(old_byte_1)
                        self.f2.write(byte * 3)
                        old_byte_2 = byte

                    elif version == 4:
                        byte = f.read(1)
                        self.f2.write(old_byte_1 * 2)
                        self.f2.write(byte * 2)
                        old_byte_2 = byte

                    elif version == 5:
                        byte = f.read(1)
                        self.f2.write(old_byte_1 * 3)
                        self.f2.write(byte)
                        old_byte_2 = byte

                    elif version == 6:
                        byte = f.read(1)
                        self.f2.write(old_byte_1 * 2)
                        self.f2.write(byte)
                        self.f2.write(old_byte_1)
                        old_byte_2 = byte

                    # Команду 7 перенёс ниже, скорей всего она не используется.

                    elif version == 8:
                        byte = f.read(1)
                        self.f2.write((byte+old_byte_1) * 2)
                        old_byte_2 = byte

                    elif version == 9:
                        byte = f.read(1)
                        self.f2.write(byte+old_byte_1)
                        self.f2.write(byte * 2)
                        old_byte_2 = byte

                    elif version == 10:
                        byte = f.read(1)
                        self.f2.write(byte)
                        self.f2.write(old_byte_1 * 2)
                        self.f2.write(byte)
                        old_byte_2 = byte

                    elif version == 11:
                        byte = f.read(1)
                        self.f2.write(byte)
                        self.f2.write(old_byte_1 * 3)
                        old_byte_2 = byte

                    elif version == 12:
                        byte = f.read(1)
                        self.f2.write(byte * 2)
                        self.f2.write(old_byte_1 * 2)
                        old_byte_2 = byte

                    elif version == 13:
                        byte = f.read(1)
                        self.f2.write(byte * 3)
                        self.f2.write(old_byte_1)
                        old_byte_2 = byte

                    elif version == 14:
                        byte = f.read(1)
                        self.f2.write(byte * 2)
                        self.f2.write(old_byte_1)
                        self.f2.write(byte)
                        old_byte_2 = byte

                    elif version in [7, 15]: # Скорей всего это команда не используется.
                        byte = f.read(1)
                        self.f2.write(b'\x00\x00\x00\x00')
                        old_byte_2 = byte

                elif team_number == 5:
                    if version == 0:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write((byte_1 + byte_2) * 2)
                        old_byte_1 = byte_1
                        old_byte_2 = byte_2

                    elif version == 1:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(byte_1)
                        self.f2.write(byte_2)
                        self.f2.write(byte_1 * 2)
                        old_byte_1 = byte_1
                        old_byte_2 = byte_2

                    elif version == 2:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(byte_1+byte_2+byte_2+byte_1)
                        old_byte_1 = byte_1
                        old_byte_2 = byte_2

                    elif version == 3:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(byte_1)
                        self.f2.write(byte_2 * 3)
                        old_byte_1 = byte_1
                        old_byte_2 = byte_2

                    elif version == 4:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(byte_1 * 2)
                        self.f2.write(byte_2 * 2)
                        old_byte_1 = byte_1
                        old_byte_2 = byte_2

                    elif version == 5:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(byte_1 * 3)
                        self.f2.write(byte_2)
                        old_byte_1 = byte_1
                        old_byte_2 = byte_2

                    elif version == 6:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(byte_1*2)
                        self.f2.write(byte_2)
                        self.f2.write(byte_1)
                        old_byte_1 = byte_1
                        old_byte_2 = byte_2

                    # Команду 7 перенёс ниже, скорей всего она не используется.

                    elif version == 8:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write((byte_2+byte_1) * 2)
                        old_byte_1 = byte_1
                        old_byte_2 = byte_2

                    elif version == 9:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(byte_2+byte_1+byte_2+byte_2)
                        old_byte_1 = byte_1
                        old_byte_2 = byte_2

                    elif version == 10:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(byte_2+byte_1+byte_1+byte_2)
                        old_byte_1 = byte_1
                        old_byte_2 = byte_2

                    elif version == 11:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(byte_2)
                        self.f2.write(byte_1 * 3)
                        old_byte_1 = byte_1
                        old_byte_2 = byte_2

                    elif version == 12:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(byte_2 * 2)
                        self.f2.write(byte_1 * 2)
                        old_byte_1 = byte_1
                        old_byte_2 = byte_2

                    elif version == 13:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(byte_2 * 3)
                        self.f2.write(byte_1)
                        old_byte_1 = byte_1
                        old_byte_2 = byte_2

                    elif version == 14:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(byte_2 * 2)
                        self.f2.write(byte_1+byte_2)
                        old_byte_1 = byte_1
                        old_byte_2 = byte_2

                    elif version in [7, 15]: # Скорей всего это команда не используется.
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(b'\x00\x00\x00\x00')
                        old_byte_1 = byte_1
                        old_byte_2 = byte_2

                elif team_number == 6:
                    if version == 0:
                        f.seek(f.tell()-2)
                        old_byte_1 = f.read(1) # Это байт преведущего чего то
                        old_byte_2 = f.read(1) # Это байт number

                    elif version <= 15:
                        self.f2.write(f.read(version * 4))
                        f.seek(f.tell()-2)
                        old_byte_1 = f.read(1)
                        old_byte_2 = f.read(1)

                elif team_number == 7:
                    if version == 0:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(old_byte_1)
                        self.f2.write(byte_1+byte_2)
                        self.f2.write(old_byte_1)

                    elif version == 1:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(old_byte_1 * 2)
                        self.f2.write(byte_1+byte_2)

                    elif version == 2:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(byte_1+byte_2)
                        self.f2.write(old_byte_1 * 2)

                    elif version == 3:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(byte_1+old_byte_1+old_byte_1+byte_2)

                    # Команды 4,5,6,7 перенёс ниже, скорей всего она не используется.

                    elif version == 8:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(old_byte_2)
                        self.f2.write(byte_1+byte_2)
                        self.f2.write(old_byte_2)

                    elif version == 9:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(old_byte_2 * 2)
                        self.f2.write(byte_1+byte_2)

                    elif version == 10:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(byte_1+byte_2)
                        self.f2.write(old_byte_2 * 2)

                    elif version == 11:
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(byte_1)
                        self.f2.write(old_byte_2 * 2)
                        self.f2.write(byte_2)

                    # Этих вариаций нет, заместо них записываеются пустые байты 
                    elif version in [4, 5, 6, 7,  12, 13, 14, 15]: # Скорей всего это команда не используется.
                        byte_1 = f.read(1)
                        byte_2 = f.read(1)
                        self.f2.write(b'\x00\x00\x00\x00')

            line_number += 1 # Увеличиваем номер строчки по высоте картинки

        self.f2.seek(0)
        f_image = Image.frombuffer('P', (w,h), self.f2.read(w*h), 'raw', 'P', 0, 1)
        f_image.putpalette(self.Pal) # Добавляем палитру в картинку
        self.images.append(f_image)
        f.close()