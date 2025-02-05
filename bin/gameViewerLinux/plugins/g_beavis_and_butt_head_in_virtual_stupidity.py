#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Распаковка архивов .000 .vnm игры Beavis And Butt-Head Virtual Stupidity 

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Beavis and Butt-Head in Virtual Stupidity"
FORMATS_ARCHIVE = ['000','vnm']
TYPES_ARCHIVE = [('Beavis and Butt-Head in Virtual Stupidity', ('*.000', '*.vnm'))]
GAMES = ["Beavis and Butt-Head in Virtual Stupidity"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app
        
        self.sup_formats = ["anm"]

        self.sup_types = {"anm":1}
        self.images = []
        self.sound = None
        self.palitra = [] # Палитра для анимаций

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "vnm" or format == "000":
            self.OpenArchiveVNM(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        tip = data_res[4]
        w = data_res[5]
        h = data_res[6]
        
        self.file.seek(offset)
        if format == "anm":
            if tip == 0:
                self.Unpack_ANM_BEZ(io.BytesIO(self.file.read(size)),w,h)
            elif tip == 1:
                self.Unpack_ANM(io.BytesIO(self.file.read(size)),w,h)
            else:
                print("Непонятный тип",tip)

    def OpenArchiveVNM(self,file):
        f = open(file,"rb")
        data2 = [] # Настройки файлов высота ширина
        offs = []  # Оффсеты на таблицу по 24 байта с информацией
            
        type1 = f.read(4) # Тип архива VNM.  
        type2 = f.read(4) # Нули если внутри картинки    если 00 00 00 80 то скрипт
        if type1 == b'\x56\x4E\x4D\x1A' and type2 != b'\x00\x00\x00\x00': # Проверка на архив
            print("ЭТО НЕ АРХИВ это скрипт",type2)
            return(0) # Остановка скрипта
    
        size = struct.unpack("<I",f.read(4))[0] # Размер файла
        offset_pal = struct.unpack("<I",f.read(4))[0] # Начало палитры
        unclear2 = struct.unpack("<I",f.read(4))[0] # Непонятно 256 *4 всегда
        unclear3 = struct.unpack("<I",f.read(4))[0] # Непонятно 256 *4 всегда
        offset_tab = struct.unpack("<I",f.read(4))[0] # Оффсет таблицы оффсетов Таблица сылается на строчки по 24 байта с настройками картинок 
        unclear5 = struct.unpack("<I",f.read(4))[0] # Первый допустимый индекс в цветовой палитры.
        number_colors = struct.unpack("<I",f.read(4))[0] # Количество цветов*3
        col_f = struct.unpack("<I",f.read(4))[0] # Количество оффсетов(количество файлов) по 4 байта
        #print("Начало палитры",offset_pal,"Непонятные таблицы по 256 *4:",unclear2,unclear3)
        #print("Оффсет оффсетов",offset_tab,unclear5,"Количество цветов в палитре",number_colors)
        #print("Количество файлов",col_f)

        self.palitra.append((0, 0, 0, 0)) # Прозрачность
        for i in range(9): # Заполнение палитры 10 цветов по 3 
            r,g,b = struct.unpack("BBB",f.read(3))
            self.palitra.append((0, 0, 0, 255))
    
        f.seek(offset_pal) # Чтения палитры для переделки картинок
        for i in range(number_colors): # Палитра 
            r,g,b = struct.unpack("BBB",f.read(3))
            self.palitra.append((r << 2, g << 2, b << 2, 255)) # Битовый сдвиг в 2 в лево, чтоб правельная была палитра

        f.seek(offset_tab)
        for i in range(col_f): # Читаем место нахождение оффсетов
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет нахождения строчки по 24 байта
            if offset > 0: # Важно
                offs.append(offset)

        for i in offs: # Читаем таблицу по 24 байта с Настройками картинок
            f.seek(i)  # Оффсет настроек
            Offset2 = struct.unpack("<I",f.read(4))[0] # Оффсет сжатой картинки
            tip = struct.unpack("<I",f.read(4))[0] # 0 не сжат, 1 сжатый файл 
            w = struct.unpack("<I",f.read(4))[0]   # Ширина
            h = struct.unpack("<I",f.read(4))[0]   # Высота И сколько надо прочитать в начале по 4 байта
            xxx = struct.unpack("<I",f.read(4))[0] # X позиция
            yyy = struct.unpack("<I",f.read(4))[0] # Y позиция
            #print(Offset2,tip,w,h)
            data2.append((Offset2,tip,w,h))
        data2.append((size,None,None,None,None)) # Нужно для правельного расчёта размера

        data2.sort(key=lambda i: i[0]) # От сортировано Сортировка нужна чтоб правельно расчитать размеры

        ss2 = 0
        ds = len(data2) # Это сколько было файлов
        while True: # Удаляем одинаковые оффсеты картинок чтоб расчитать размер файла
            if data2[ss2+1][0] == size: # Когда достигли конца файла
                break
        
            #print(ss2,data2[ss2+1][0], data2[ss2][0])
            if data2[ss2+1][0] == data2[ss2][0]:
                #print("Удалил файл",ss2+1,data2[ss2+1])
                del data2[ss2+1]
            else: # Если не нашлось повторения оффсетов
                ss2 += 1
        #print("Было картинок",ds,"осталось",len(data2))
        col_f = len(data2)-1 # Новое количество файлов

        ss2 = -1
        for i in range(col_f):
            ss2 += 1
            size = data2[ss2+1][0] - data2[ss2][0] # Расчитываем размер файла 
            self.data.append((str(i+1)+".anm",data2[ss2][0],size,"anm",data2[ss2][1],data2[ss2][2],data2[ss2][3]))
                    
        self.file = f
        return 1
        
    def Unpack_ANM_BEZ(self,f,w,h):
        rgb = []
        for i in range(w*h): # Читаем картинку по палитре
            fd = struct.unpack("B",f.read(1))[0]
            rgb.extend(self.palitra[fd])
        rgb = np.array(rgb,np.uint8).reshape(h, w, 4)
        self.images =[Image.fromarray(rgb,"RGBA")]

    def Unpack_ANM(self,f,w,h):
        rgb = []
        for i in range(h): # Читаем количество оффсетов по высоте картинки h(Оффсет ссылается на строчку распаковки)
            offset = struct.unpack("<I",f.read(4))[0]

        size_f = 0 # Размер распакованных данных
        ss = 0 # Количество распакованных строчек
        while True:
            if size_f > w:
                posf0 = f.tell()
                #print("Позиция",posf0,"Насколько перполнился",size_f,size_f-w)
                print("Ошибка Слишком много байт ############### Строчка",ss)
                return(0)
                
            if size_f == w:
                #print("Конец распаковки строчки",f.tell())
                size_f -= w
                ss += 1
                if ss == h:
                    #print("Конец распакованно файла")
                    break

            check = struct.unpack("B",f.read(1))[0] #
            if check >= 128: # Повторение
                repeat = 256 - check # Повторить
                size_f += repeat
                for i in range(repeat):
                    rgb.extend(self.palitra[0])
                #print("Повторить байт",hex(check),repeat)

            else: # Чтение
                #print("Прочитать байт",hex(check),check+1)
                size_f += check+1
                fd = f.read(check+1) # Байты который надо прочетать
                for i in fd:
                    rgb.extend(self.palitra[i])

        rgb = np.array(rgb,np.uint8).reshape(h, w, 4)
        self.images =[Image.fromarray(rgb,"RGBA")]