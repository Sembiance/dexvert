#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Pink Panther: Passport to Peril (Розовая Пантера: Право на Риск)
# Pink Panther: Hocus-Pocus       (Розовая Пантера: Фокус-Покус)

import os, sys, io, struct
from PIL import Image

NAME = "Pink Panther" 
FORMATS_ARCHIVE = ['orb']
TYPES_ARCHIVE = [('Pink Panther', ('*.orb'))]
GAMES = ["Pink Panther: Passport to Peril",
         "Pink Panther: Hocus-Pocus"]

AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["cel",
                            "vox",
                            "wav",
                            "mus",
                            "txt"]

        self.sup_types = {"cel":2,
                          "vox":3,
                          "wav":3,
                          "mus":3,
                          "txt":4}
        self.images = [] 
        self.sound = None 
        self.dirname = None # Место положение архива нужно для архива PPTP.BRO
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "orb":
            self.OpenArchiveORB(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        tip = data_res[4]
        self.file.seek(offset)
        if format == "cel":
            if tip == 0: 
                self.Unpack_CEL(io.BytesIO(self.file.read(size)))

            elif tip == 1: # Файлы в другом а архиве Passport to Peril для русской версии
                if os.path.exists(self.dirname+"\\INSTALL\\PPTP.BRO") == True:
                    file2 = open(self.dirname+"\\INSTALL\\PPTP.BRO","rb")
                    file2.seek(offset)
                    self.Unpack_CEL(io.BytesIO(file2.read(size)))
                    file2.close()

                elif os.path.exists(self.dirname+"\\PPTP.BRO") == True: # Если лежит в папке с архивом
                    file2 = open(self.dirname+"\\PPTP.BRO","rb")
                    file2.seek(offset)
                    self.Unpack_CEL(io.BytesIO(file2.read(size)))
                    file2.close()

                else:
                    print("Ошибка, нет папки с файлом INSTALL\\PPTP.BRO")

        elif format in ["mus", "vox", "wav"]:
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))

        elif format == "txt":
            self.Unpack_TXT(io.BytesIO(self.file.read(size))) 

    def OpenArchiveORB(self,file):
        (self.dirname, filename) = os.path.split(file)

        f = open(file,"rb")
        type = f.read(4) # Тип архива ORB.
        if type != b'ORB\x00':
            print("ЭТО НЕ АРХИВ",type)
            return(0)

        unclear_1 = f.read(2) # Непонятно Всегда нули 00 00
        type = f.read(2) # Проверка на наличие таблицы файлов в архиве
        if type != b'\x02\x00':
            print("Архив без таблицы",type)
            return(0)

        unclear_3 = f.read(4) # Непонятно

        offset_tab = struct.unpack("<I",f.read(4))[0] # Оффсет на таблицы в конце файла
        col_tab = struct.unpack("<I",f.read(4))[0] # Количество таблиц в конце файла
        f.seek(offset_tab)

        for i in range(col_tab):
            folder = f.read(16).split(b"\x00")[0].decode("utf8") # Имя локаци или папки
            # Возможно ниже две строчки это скрипт игры, что отображается на локации.
            offset2 = struct.unpack("<I",f.read(4))[0] # Непонятный оффсет тоже ссылается на таблицу файлов но других
            size2 = struct.unpack("<I",f.read(4))[0] # Размер для выше таблице или файла
            self.data.append((folder+"\\"+folder+" "+str(offset2)+".script", offset2, size2, "script", 0))

            offset_tab_f = struct.unpack("<I",f.read(4))[0] # Место нахождения таблиц файлов
            col_f = struct.unpack("<I",f.read(4))[0] # Количество файлов

            f_pos = f.tell() # Запоминаем позицию в таблице
            f.seek(offset_tab_f) # Переходим на таблицу файлов

            for j in range(col_f): # Прочитать файлы
                f_path = f.read(16).split(b"\x00")[0].decode("utf8") # Имя файла
                offset = struct.unpack("<I",f.read(4))[0] # Оффсет файла
                size = struct.unpack("<I",f.read(4))[0] # Размер файла
                tip = struct.unpack("<H",f.read(2))[0] # В каком архиве находится файл
                format = f_path.split(".")[-1].lower()
                self.data.append((folder+"\\"+f_path, offset, size, format, tip))

            f.seek(f_pos) # Возврат в таблицу локаци или папки
        self.file = f
        return 1

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_TXT(self, f): 
        self.text = f.read().decode("cp1251")

    def Unpack_CEL(self,f):
        f.seek(0,2)
        end_f = f.tell() # Конец файла, нужно для распаковки анимаций
        f.seek(0)

        size_f = struct.unpack("<I",f.read(4))[0] # Размер файла
        type = f.read(2)
        if type != b'\x12\xAF':
            print("ЭТО НЕ ФАЙЛ анимации",type)
            return(0)

        framen = struct.unpack("<H",f.read(2))[0] # Количество кадров анимаций
        w,h = struct.unpack("<HH",f.read(4)) # Ширина и высота основной картинки

        f.seek(68, 1) # Пропускаем байты
        #unclear_fd_1 = f.read(68) # Непонятные байты С 12-80 непонятно 68 байта
        # 8 байт непонятно потом идут два раза по 8 байт данные которые если выстовить шириной в 8 то видна закономерность

        #f.seek(80)
        offset_mini = struct.unpack("<I",f.read(4))[0] # Оффсет начало файлов
        offset_animal = struct.unpack("<I",f.read(4))[0] # Оффсет первого кадра наложения анимации
        #print("Количество кадров",framen,"Оффсет начало файлов",offset_mini,"Оффсет наложений анимаций",offset_animal)

        f.seek(offset_mini-88, 1) # Пропускаем байты
        #unclear_fd_2 = f.read(offset_mini-88) # Непонятные байты, количество байт может отличатся у разных файлов

        frame_number = 0 # Количество найденых анимаций наложения
        Pal = b'\x00' *768 # Создаю палитру

        f.seek(offset_mini) # Переходим на начало чтения файлов
        while f.tell() != end_f: # Остановка когда достигним конца файла.
            size_block = struct.unpack("<I",f.read(4))[0] # Размер блока данных
            unclear = f.read(2) # Непонятно FA F1 Тип файла
            col = struct.unpack("<H",f.read(2))[0] # Количество файлов 0,1,2,3
            zeros = f.read(8) # Непонятно 8 байт нулей
            #print("Начало блока позиция",posf,"Размер блока",size_block,"Количество файлов",col)

            if col == 0: # Пустой кадр всегда 10 00 00 00 FA F1 00 00 00 00 00 00 00 00 00 00
                frame_number += 1 # Номер кадра

            for ii in range(col): # Прочитать нужное количество файлов
                posf = f.tell()
                size = struct.unpack("<I",f.read(4))[0] # Размер файла
                tip = struct.unpack("<H",f.read(2))[0] # Тип данных
                f.seek(posf) # Переход на начало файла
                #print("Позиция",posf,"Размер",size,"Тип данных",tip,"Номер файла",ii+1)

                if tip == 4: # Тут файл обновления палитры 04 00
                    # Тип 4 это палитра но может быть не полной 768 а меньше например 710
                    # Заголовок Палитры 10 байт CE 02 00 00  04 00  01 00  0A  EC
                    #size = struct.unpack("<I",f.read(4))[0] # Размер файла
                    #tip = struct.unpack("<H",f.read(2))[0] # Тип данных 04 00
                    #unclear = struct.unpack("<H",f.read(2))[0] # Непонятно 01 00

                    f.seek(8, 1) # Пропускаем байты
                    color_number_offset = f.read(1)[0] *3 # Номер цвета на который надо записывать новую палитру
                    col_read = f.read(1)[0] *3 # Сколько дальше прочетать цветов. Если надо прочетать все цвета то стоит байт 00
                    if col_read == 0: # Если число равно 0 то прочитать все цвета
                        col_read = 768
                        
                    #print("Палитра Непонятно",unclear,"Записать палитру на",color_number_offset,"Сколько прочетать цветов",col_read)

                    f_Pal = io.BytesIO(Pal) # Кладём старую палитру
                    f_Pal.seek(color_number_offset) # Перейти на нужный цвет записи
                    f_Pal.write(f.read(col_read)) # Читаем нужное число цветов Записываем байты поверх старых
                    f_Pal.seek(0) # Перейти на начало
                    Pal = f_Pal.read() # Читаем обновленную палитру
                    f_Pal.close()

                    f.read(size-(10+col_read)) # Читаем оставшиеся ненужные байты

                elif tip == 7: # Тип 7 наложение анимаций 07 00
                    # Заголовок анимации 8 байт
                    frame_number += 1 # Номер кадра
                    #print("Номер анимации",frame_number,"Позиция",posf,"размер",size)
                    self.Unpack_anim(w,h, f2, f, Pal, f.tell()+size) # f2 картинка в памяти, f файл анимаций

                elif tip == 15: # Распаковка сжатой картинки 0F 00
                    f_temp = io.BytesIO(f.read(size))
                    f2 = self.Unpack_comp(f_temp, w,h, Pal) # f2 Буффер картинки в памяти для наложения анимаций
                    f_temp.close()

                elif tip == 16: # Не сжатая картинка 10 00
                    # Картинки без сжатия
                    # Право на риск APBG0016.CEL, FVSPB004.CEL, IMVS0002.CEL, OPBG0016.CEL
                    # Фокус-Покус Нету
                    size = struct.unpack("<I",f.read(4))[0] - 4 # Размер файла +2 байта к размеру файла
                    tip = struct.unpack("<H",f.read(2))[0] # Тип данных
                    f2 = io.BytesIO(f.read(size))
                    #print("Картинка без сжатия позиция",posf,"размер",size,"уже прибавели 2")

                    if size == 1024 and w == 33 and h == 31: # Право на риск FVSPB004.CEL
                        # FVSPB004.CEL картинка не сжата, размер почему то неправильный указан не хватает одного байта. Если посмотреть на файл то один пиксель стоит не на своём месте и один пиксель не понятный в начале картинки, но всего надо прочетать ещё 2 байта.
                        # Делаем картинку правельной перемещяя сконца файла 1 пиксель в начало заместо непонятного
                        f2.seek(1023, 1) # Пропускаем байты картинки
                        fd1 = f2.read(1) # Первый пиксель
                        f2.seek(0)
                        f2.write(fd1) # В ставляем в нужное место пиксель
                        f2.seek(0)

                    frame_number += 1 # Номер кадра

                    f_image = Image.frombuffer('P', (w,h), f2.read(w*h), 'raw', 'P', 0, 1)
                    f_image.putpalette(Pal)    
                    self.images.append(f_image)

                elif tip == 18: # Заголовок перед мини картинкой 12 00
                    # FA 05 00 00  12 00 (высота и ширина) 3F 00 56 00  01 00
                    #size = struct.unpack("<I",f.read(4))[0] # Размер файла
                    #tip = struct.unpack("<H",f.read(2))[0] # Тип данных
                    f.seek(6, 1) # Пропускаем байты
                    h2, w2 = struct.unpack("<HH",f.read(4)) # Ширина и высота Мини картинки
                    unclear = struct.unpack("<H",f.read(2))[0] # Непонятно
                    #print("Позиция",posf,"Перед Мини картинкой Ширина и высота",h2, w2,"Непонятно",unclear)

                    posf3 = f.tell()
                    size_2 = struct.unpack("<I",f.read(4))[0] # Размер файла
                    tip_2 = struct.unpack("<H",f.read(2))[0] # Тип данных
                    f.seek(posf3) # Переход на начало файла
                    fd = f.read(size_2)

                    if tip_2 == 15: # Распаковка Мини картинки 0F 00
                        # Заголовок мини картинки 6 байт  EE 05 00 00 (тип)0F 00

                        # Генерация палитры
                        Pal_2 = b'' 
                        for i in range(255):
                            Pal_2 += struct.pack("BBB", i, i, i)

                        f_temp = io.BytesIO(fd)
                        # Непоказываем мини картинку
                        #f6 = self.Unpack_comp(f_temp, w2,h2, Pal_2)
                        f_temp.close()
                        #f6.close()

                    elif tip_2 == 18: # 12 00
                        # Сейчас в fd записанно 262 байт # Просто набор байт
                        # Размер всегда 262 байт при любой ширине и высоте картинки. Последнии 10 байт всегда D7 81 81 B4 1E D2 05 B9 23 D7
                        # Если брать чисто размер файла то он равен 256 байт
                        #print("    Непонятный файл размером в 262 байта позиция",posf3)
                        pass

                    else:
                        print("    Ошибка непонятный тип в мини картинки",tip_2)
                        return(0) # Остановка скрипта

                else:
                    print("    Ошибка неизвестный тип файла",tip,"Позиция",posf)
                    print("Размер файла",size)
                    fd = f.read(size)
                    print("Позиция после файла",f.tell())
        f.close()
        f2.close() # Буффер картинки

    def Unpack_comp(self, f, w,h, Pal): # Распаковка сжатия картинки Тип 15
        f2 = io.BytesIO() # Буффер картинки в памяти для наложения

        size_comp = struct.unpack("<I",f.read(4))[0] # Размер сжатых данных
        tip_comp = struct.unpack("<H",f.read(2))[0] # Тип сжатия
        #print("Ширина и высота",w,h,"Размер сжатых данных",size_comp,"Тип сжатия",tip_comp)

        for i in range(h):
            f.seek(1, 1) # Сделал так чтобы увеличить скорость распаковки.
            # number_komand = f.read(1)[0] # Количество команд для распаковки одной строчки по ширине картинки. Команд может быть больше чем число в этом байте.
            #print("Количество команд",number_komand)

            # OHBG0001.CEL Команд значительно больше чем записанно, записанно 63 команд а должно прочитается 319 чтобы правельно распаковалось

            sr = 0 # Распаковано байт
            while sr != w: # Остановка когда распакуется количество байт равная ширине картинки w
                byte = f.read(1)[0]
                if byte >> 7: # Прочитать байтов
                    byt2 = 256-byte # Сколько прочитать байтов
                    f2.write(f.read(byt2))
                    sr += byt2
                    #print(byte,"Прочитать байтов",byt2)

                else: # Повторить байт
                    f2.write(f.read(1)*byte)
                    sr += byte
                    #print(byte,"Повторить байт2",byt1)

        f_pos = f.tell()
        #print("Позиция после распаковки",f_pos)
        if size_comp == f_pos: # Если не осталось байтов после распаковки
            pass

        else: # Если остались ещё байты
            fd_check = f.read() # Оставшиеся байты
            if fd_check == b'\x00': # Остался один байт 00
                pass # Это нормально но не во всех файлах он есть

            else:
                #print("    Ошибка сжатых данных в конце ещё остались байты",size_comp-f_pos,fd_check)
                pass
                # Если в конце останется один байт это вполне нормально, в некоторых файлов в конце не остаётся 1 байт.

        f2.seek(0)
        f_image = Image.frombuffer('P', (w,h), f2.read(w*h), 'raw', 'P', 0, 1)
        f_image.putpalette(Pal)    
        self.images.append(f_image)
        return f2

    def Unpack_anim(self, w,h, picture, f, Pal, end_f):
        """
        size2 = struct.unpack("<I",f.read(4))[0] # Размер файла наложений анимаций
        tip = struct.unpack("<H",f.read(2))[0] # Тип данных 7 наложение анимаций
        number_lines = struct.unpack("<H",f.read(2))[0] # Количество изменёных строчек
        #print("Размер файла",size2, "Тип данных",tip, "Количество изменёных строчек",number_lines)
        """
        f.seek(8,1) # Пропускаем байты для увелечения скорости
        line_number = 0 # Номер строчки куда будут записыватся байты

        while f.tell() != end_f: # Остановка когда достигним конца файла.
            number = struct.unpack("<H",f.read(2))[0] # Читаем число

            if number <= 255: # Cколько команд надо выполнить
                #print("Количество команд на строчку",number,"Позиция",f.tell()-2)
                # Получаем оффсет нужной строчки w, Умножить номер строчки на ширину 
                picture.seek(line_number * w) # Переходим на начало строчки для записи байтов
                #print("Начать со строчки",line_number ,"на оффсете",line_number * w)

            elif number & 0xFE00 == 0xFE00: # Сколько пропустить строчек
                line_number += (0xFFFF - number)+1
                #print("Сколько пропустить строчек", (0xFFFF - number)+1,"Позиция",f.tell()-2)
                continue
                # Что делает эта команда, пропускает строчки на начало новой строчки, 
                # минемальный переход на 1 строчку вперёд.

            elif number & 0xFF00 == 0x8000: # Переходим на последний байт на строчки и записываем 1 байт
                picture.seek((line_number * w) + (w-1)) # Последний байт на строчке
                picture.write(struct.pack("B", number - 0x8000)) # Запись первого байта
                continue

            else:
                print("#################################")
                print("    Ошибка Непонятное значение",tip,"Позиция",f.tell()-2,"Кадр",frame_number,"Размер файла",size2,"\n")
                return(0)

            for i in range(number):
                picture.seek(f.read(1)[0], 1) # На сколько байт от ступить от начало строчки
                check = f.read(1)[0] # Прочитать или повторить байты

                if check >> 7: # Если бит 1000 0000
                    picture.write(f.read(2)*(256 - check)) # 2 байта повторения Сколько повторить

                else: # Просто прочитать байты
                    picture.write(f.read(check * 2)) # Сколько прочитать байт дальше

            line_number += 1 # Переход на новую строчку

        picture.seek(0)
        f_image = Image.frombuffer('P', (w,h), picture.read(w*h), 'raw', 'P', 0, 1)
        f_image.putpalette(Pal)    
        self.images.append(f_image)