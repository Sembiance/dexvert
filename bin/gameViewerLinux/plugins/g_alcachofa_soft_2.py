#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Mortadelo Y Filemon: Una Aventura de Cine. Dos Vaqueros Chapuceros
# Mortadelo Y Filemon: Una Aventura de Cine. Terror, Espanto y Pavor

import os, sys, io, struct
from PIL import Image

NAME = "Alcachofa Soft 2"
FORMATS_ARCHIVE = ['emc']
TYPES_ARCHIVE = [('Alcachofa Soft 2', ('*.emc'))]
GAMES = ["Mortadelo Y Filemon: Una Aventura de Cine. Dos Vaqueros Chapuceros", "Mortadelo Y Filemon: Una Aventura de Cine. Terror, Espanto y Pavor"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["ani",
                            "wav",
                            "txt"]

        self.sup_types = {"ani":2,
                          "wav":3,
                          "txt":4}

        self.images = []
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "emc":
            self.OpenArchiveEMC(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "ani":
            self.Unpack_ANI(io.BytesIO(self.file.read(size)))

        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))

        elif format == "txt":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))

    def OpenArchiveEMC(self, file):
        f = open(file,"rb")
        dataf = f.read() # Читаем весь файл и записываем его в dataf для поиска
        ##########################################################
        # Поиск звуков wav
        offset = 0 # Начало поиска оффсет
        while True:
            offset = dataf.find(b'RIFF',offset) # Поиск значения b'RIFF', по месту нахождения в файле offset Найденная позиция байта
            if offset == -1: # Если не нашли байты остановка
                break

            f.seek(offset+4) # Пропускаем первые 4 байта
            size = struct.unpack("<I",f.read(4))[0] + 8 # Размер
            check = f.read(4) # Проверочные данные
            if check == b'WAVE':
                #data.append((str(offset)+".wav",offset,size))

                # Расчёт длины имени файла
                end_name = offset-8 # 4 байта это ".WAV", 4 байта это размер файла
                length = 1 # Сейчас длина должна равнятся
                ss = 2
                for i in range(255):
                    f.seek(end_name-ss)
                    posf = f.tell()
                    #print("",posf)
                    length_name = f.read(1)[0] # Длина имени
                    if length_name == length:
                        f_path = f.read(length_name+4).replace(b'\x03',b'\x2E').decode("utf8")
                        #print("Длина имени",length_name,f_path)
                        self.data.append((f_path, offset, size, "wav"))
                        break
                    else:
                        ss += 1
                        length += 1 # Увеличиваем длину имени

            offset += 1 # Позиция дальше для поиска в файле


        ##########################################################
        # Поиск анимаций ani
        # Не использовать имена анимаций вних встречаются повторения имён
        offset = 0 # Начало поиска оффсет
        while True:
            offset = dataf.find(b'ANI\x00',offset)
            if offset == -1: # Если не нашли байты остановка
                break

            f.seek(offset-4)
            size = struct.unpack("<I",f.read(4))[0] # Размер
            f.seek(offset-8)
            check = f.read(4) # Проверочные данные
            if check == b'.ani':
                self.data.append((str(offset)+".ani",offset,size,"ani"))
                #print("Это анимация",offset,size)

                # Тут в длину имени входет тип файла .ani 4 байта
                # Расчёт длины имени файла
                end_name = offset-4 # 4 байта это размер файла
                length = 5 # Сейчас длина должна равнятся
                ss = 6
                for i in range(255):
                    f.seek(end_name-ss)
                    posf = f.tell()
                    length_name = f.read(1)[0] # Длина имени
                    if length_name == length:
                        f_path = f.read(length_name)
                        #print("Длина имени",length_name,f_path)
                        #self.data.append((f_path,offset,size))
                        break
                    else:
                        ss += 1
                        length += 1 # Увеличиваем длину имени
            else:
                print("Для теста непонятные строчка может содержать большие буквы",check)
            offset += 1 # Позиция дальше для поиска в файле

        ##########################################################
        # Поиск по имени текстового файла
        data2 = [b'\x4F\x42\x4A\x45\x54\x4F\x53\x03\x54\x58\x54',b'\x54\x45\x58\x54\x4F\x53\x03\x54\x58\x54'] # Список имён для поиска
        number_files = 0 # Количество файлов

        for i in data2:
            offset = dataf.find(i,0)
            if offset != -1:
                number_files += 1
                f.seek(offset)
                f_path = f.read(len(i)) # Читаем имя файла
                f_path = f_path.replace(b'\x03',b'\x2E').decode("utf8") # Меняем байт 03 на точку b'0577\x03WAV'
                size = struct.unpack("<I",f.read(4))[0] # Размер
                offset_f = f.tell() # Оффсет начало файла
                self.data.append((str(offset)+" "+f_path, offset_f,size, "txt"))

        self.file = f

    def Unpack_WAV(self, f): 
        self.sound = f

    def Unpack_TXT(self, f):
        fd = f.read()
        f.seek(33)
        check = f.read(6)

        if check == b'\xd3\xeb\xe8\xf6\xe0"' or check == b' \xf8\xe5\xf4, ': # Если текст русский
            self.text = fd.decode("cp1251")
        else:
            self.text = fd.decode("charmap")

    def Unpack_ANI(self, f):
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)
        type = f.read(4) # Тип
        if type != b'ANI\x00': # Проверка на картинку
            print("ЭТО НЕ КАРТИНКА",type)
            return(0)

        length = f.read(1)[0] # Длина внутренего имени
        fd = f.read(length)
        length_2 = struct.unpack("<I",f.read(4))[0] # Длина букв
        byte_18 = struct.unpack("<I",f.read(4))[0] # Количество строчек в конце файла по 18 байт
        f.read(25) # Непонятные данные

        end_pic = end_f-(byte_18*18) # Конец картинок

        frame = 0 # Номер кадра
        while True:
            while True: # Анимация 136281064.ani несколько раз подряд идут 10 непонятных байт
                posf = f.tell()
                if posf == end_pic:
                    break
                f.seek(posf+7)
                check = f.read(3) # Проверка
                if check == b'\xFF\xFF\xFF': # Заголовок с лишними 10 байтами
                    #print("    Ошибочный заголовок",posf)
                    f.seek(posf+10)

                else: # Нормальный заголовок
                    f.seek(posf)
                    break

            if f.tell() == end_pic:
                #print("Конец всех картинок",f.tell())
                break

            #######################
            # Ниже алгоритм идентичен Банда Корвино

            frame += 1
            #print("Начало картинки",f.tell())
            # 22 байта
            unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_2 = struct.unpack("<H",f.read(2))[0] # Непонятно
            Coordinates_w, Coordinates_h = struct.unpack("<HH",f.read(4)) # Координаты картинок ?
            w, h = struct.unpack("<HH",f.read(4)) # Ширина и высота картинки
            # Количество строчек в высоту Это обозначает высоту созданной картинки в нутри другой картинки

            size_color = struct.unpack("<I",f.read(4))[0] # Размер полотна с цветами, если картинка 24 бита надо на *3 (после таблицы кодов)
            #print("Размер полотна с цветами который надо прочетать",size_color)

            unclear_3 = f.read(1)[0] # Непонятно
            unclear_4 = f.read(1)[0] # Непонятно
            unclear_5 = f.read(1)[0] # Непонятно
            unclear_6 = f.read(1)[0] # Непонятно
            unclear_7 = f.read(1)[0] # Непонятно
            image_format = f.read(1)[0] # Формат картинки 0 это 24 бита, 1 это 8 бит

            list_command = [] # Список команд
            for i in range(h):
                pos = f.tell()
                col_command = struct.unpack("<H",f.read(2))[0] # Количество команд на строчку
                fd = f.read(col_command*8)
                list_command.append((col_command,fd))

            #print("Начало данных полотна цветов",f.tell())
            if image_format == 1: # 8 бит
                #print("8 бит")
                bit = 1
                byte = b'\xFF' # Байты

            elif image_format == 0: # 24 бита
                #print("24 бит")
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
                #print()
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

        posf = f.tell()
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        #if posf != end_f:
            #print("В конце файла остались ещё байты на",posf,"размером в",end_f-posf)
            # 18 байт на один кадр
        f.close()
