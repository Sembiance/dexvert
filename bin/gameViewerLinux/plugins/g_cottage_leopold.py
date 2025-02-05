#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Дача кота Леопольда, или Особенности мышиной охоты

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Дача кота Леопольда, или Особенности мышиной охоты" 
FORMATS_ARCHIVE = ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','bas', 'flm']
TYPES_ARCHIVE = [('Дача кота Леопольда, или Особенности мышиной охоты', ('00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','*.bas','*.flm'))]
GAMES = ["Дача кота Леопольда, или Особенности мышиной охоты"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app
        
        self.sup_formats = ["bmp",
                            "anm",
                            "wav"]
        self.sup_types = {"bmp":1,
                          "anm":2,
                          "wav":3}
        self.images = []   
        self.sound = None
        self.fwav = io.BytesIO() # Соединенные звуки
        self.f_img = "" # Пуская картинка что бы создать картинку с нужными параметрами ширины и высоты

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        (dirname, filename) = os.path.split(file)
        if filename in ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17']:
            self.OpenArchive00(file)
        elif format == "bas":
            self.OpenArchiveBAS(file)
        elif format == "flm":
            self.OpenArchiveFIM(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "bmp":
            self.Unpack_BMP(io.BytesIO(self.file.read(size)))
        elif format == "anm":
            self.Unpack_ANM(io.BytesIO(self.file.read(size)))
        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))

    def OpenArchive00(self,file):
        self.data = [] 
        f = open(file,"rb")
        data = [] # Список размеров
    
        size = struct.unpack("<I",f.read(4))[0] # Первый размер файла
        data.append(size)
        f.seek(12)
        col_f = struct.unpack("<I",f.read(4))[0] # Сколько прочитать размеров дальше
        for i in range(col_f): 
            size = struct.unpack("<I",f.read(4))[0] # Размеры файлов
            data.append(size)
        f.seek(232) # Начало файлов
        ss = 0
        for i in data:
            ss += 1
            offset = f.tell()
            tip1 = f.read(2) # Проверка на тип bmp

            f.seek(offset+583)
            tip2 = f.read(1) # Проверка на тип anm

            if tip1 == b'\x42\x4D': # bmp
                self.data.append((str(ss)+".bmp",offset,i,"bmp"))

            elif tip2 == b'\x03': # Анимация
                self.data.append((str(ss)+".anm",offset,i,"anm"))

            else: # Непонятно
                self.data.append((str(ss)+".bin",offset,i,"bin"))
                
            f.seek(offset+i) # Переход на начало следующего файла
        self.file = f
        
    def OpenArchiveBAS(self,file):
        f = open(file,"rb")
        data = [] # Список размеров
        col_f = struct.unpack("<I",f.read(4))[0] # Сколько прочитать файлов
        for i in range(col_f):
            size = struct.unpack("<I",f.read(4))[0]
            data.append((size))
        offset = f.tell() # Cделано чтоб правельно начинались звук wav
        f.seek(offset-4)
        ss = 0 # Номер файла
        for i in data:
            ss += 1
            offset = f.tell()
            tip1 = f.read(1) # Проверка на тип anm
            f.seek(offset)
            tip2 = f.read(2) # Проверка на тип bmp, wav

            if tip2 == b'\x42\x4D': # bmp
                self.data.append((str(ss)+".bmp",offset,i,"bmp"))
            
            elif tip2 == b'\x52\x49' or tip2 == b'\x54\xF8': # wav    tip2 это для первого звука в архиве GAME.BAS
                self.data.append((str(ss)+".wav",offset,i,"wav"))

            elif tip1 == b'\x03': # Анимация
                self.data.append((str(ss)+".anm",offset,i,"anm"))
            
            else: # Непонятно
                self.data.append((str(ss)+".bin",offset,i,"bin"))
                
            f.seek(offset+i) # Переход на начало следующего файла
        self.file = f
        return 1

    def OpenArchiveFIM(self,file):
        f = open(file,"rb")
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        self.data.append(("0.anm",0, end_f, "anm"))
        self.file = f

    def Unpack_BMP(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_WAV(self, f):
        tip2 = f.read(4)
        if tip2 == b'\x54\xF8\x32\x00': # Для первого звука в архиве GAME.BAS
            f.seek(0)
            f.write(b'\x52\x49\x46\x46')
            self.sound = f
        else:    
            self.sound = f
            
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
            
    def Unpack_ANM(self, f):
        f.seek(0,2)  
        end_f = f.tell()
        f.seek(0)
    
        check_1 = f.read(1) # Проверка
        f.seek(1025)
        check_2 = f.read(2) # Проверка 2
        if check_1 == b'\x03' and check_2 == b'\x05\x01': # Это Просто картинка
            List_sizes = [(0,end_f)]
            f.seek(1) # Переходим к началу палитры
        else:   
            # Размер заголовка с таблице файлов 583 байта
            #print("Это анимация")
            List_sizes = self.Size_Anm(f, end_f) # Ищем размеры файлов анимации
            # Находимся на 584 байте, тут уже палитра

        #print("Нашлось анимаций",len(List_sizes), List_sizes)
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

    def Size_Anm(self, f, end_f): # Ищем размеры файлов анимации
        offset = 583 # Размер заголовка с таблице файлов 583 байта
        f.seek(205) # Раньше этой позиции оффсеты не начинаются проверил все таблицы
        List_sizes = [] # Список оффсетов и размеров файлов анимации

        while True:
            if f.tell() >= 583:
                break

            f_pos = f.tell()
            size = struct.unpack("<I",f.read(4))[0] # Возможный размер анимации
            #print("Позиция чтения размера",f_pos,size)

            if offset+size <= end_f: # Это чтоб невызывало ошибок если значение получится больше файла
                f.seek(offset+size)
                posboz = f.tell() # Возможная позиция начало новой анимации
                #print("Зашли сюда 2 позиция",posboz)
                if posboz == end_f: # Дошли до конца файла
                    List_sizes.append((offset, size)) # Сохранение данных последней анимации
                    #print("    Это анимация Оффсет и размер", offset, size)
                    #print("    Расчёт таблицы размеров файлов закончен правельно")
                    #print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                    break

                # Это проверка следующего за файлом анимации другова файла анимации
                check_1 = f.read(1) # Проверка первого байта палитры 03
                #print("Проверка",check_1,posboz,"Размер",size)
                if check_1 == b'\x03' and size > 0: # Это возможно анимация
                    f.seek(posboz+1025) # Пропуск палитры
                    check_2 = f.read(2) # Проверка 2
                    if check_2 == b'\x05\x01': # Это анимация
                        List_sizes.append((offset, size))
                        #print("    Это анимация Оффсет и размер", offset, size)
                        offset += size # Новое начало анимации
                        # Тут можно пропустить сразу 4 байта
                        f_pos += 3 # Почему прибавляю 3 потому что дальше ирибавляется +1 и в сумме получается прибавить +4 байта прочитанного размера файла

            f.seek(f_pos+1)
        return(List_sizes)
 
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

                #"""
                # Время 0.328 sec
                # Проблема в алгоритме это слишком много проверок

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
                        #""" 

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
