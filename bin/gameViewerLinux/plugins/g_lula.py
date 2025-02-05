#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru

# Потдерживает распаковку игр
# Lula: The Sexy Empire (Жар: Империя секса)                   [TGP TAP DDF] TAF
# Ibiza Babewatch (Ибица. Пикантные приключения)               [TGP, TAP]
# Airline 69: Back To Casablanca (Касабланка: Объект 69)       [GFX, SFX]
# Airline 69 II: Krasser's Revenge (Объект 69. Месть Крассера) [GFX, SFX] 
# Patti Pain's Bondage Poker(Садисткий покер)                  [TAP, TGP]
# Ibiza Comic Poker(Ибица покер)                               [TAP, TGP]
# Caveman ZAC                                                  [GFX, SFX]
# Bondage Sudoku (Судоку Запретные Страсти)                    [GFX, SFX]
# Dick Sucks:Terror in Titfield (Многочлен в Сиська-Граде)     [GFX, SFX]
# Dark Secrets of Africa                                       [TAP, TGP] TAF
# Clif Danger                                                  [TGP, TAP]
# Chewy: ESC from F5                                           [TAP, TGP, SPEECH.TVP, DIAH.ADH, DETAILS.OLD] TAF(тоже TAF  CURSOR.BAK,CURSOR.TA1)
# Die Erben von St. Pauli                                      [GFX, SFX]

import os, sys, io, struct
from PIL import Image
import numpy as np
import zlib

NAME = "Lula"
FORMATS_ARCHIVE = ['tap', 'tgp', 'tvp', 'gfx', 'sfx', 'adh', 'ddf', 'old', 'taf', 'ta1', 'bak']
TYPES_ARCHIVE = [('Lula', ('*.tap', '*.tgp', '*.tvp', '*.gfx', '*.sfx', '*.adh', '*.ddf', '*.old', '*.taf', '*.ta1', '*.bak'))]

GAMES = ["Lula: The Sexy Empire", # (Жар: Империя секса)
         "Ibiza Babewatch", # (Ибица. Пикантные приключения)
         "Airline 69: Back To Casablanca", # (Касабланка: Объект 69)
         "Airline 69 II: Krasser's Revenge", # (Объект 69. Месть Крассера)
         "Patti Pain's Bondage Poker", # (Садисткий покер)
         "Ibiza Comic Poker", # (Ибица покер)
         "Caveman ZAC",
         "Bondage Sudoku", # (Судоку Запретные Страсти)
         "Dick Sucks:Terror in Titfield", # (Многочлен в Сиська-Граде)
         "Dark Secrets of Africa",
         "Clif Danger",
         "Chewy: ESC from F5",
         "Die Erben von St. Pauli"]
AUTHOR = "ZetpeR xax007@yandex.ru"
         
class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["tbf",
                            "anm",
                            "anm2",
                            "wav"]
        
        self.sup_types = {"tbf":1,
                          "anm":1,
                          "anm2":1,
                          "wav":3}
        self.images = []  
        self.sound = None 
        self.palitra = [] # Палитра для анимаций Chewy ESC from F5

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format in ['tap', 'tgp', 'tvp', 'gfx', 'sfx', 'adh', 'ddf', 'old']:
            self.OpenArchiveGFX(file)
        elif format == "taf" or format == "ta1" or format == "bak":
            self.OpenArchiveTAF(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "tbf":
            self.Unpack_TBF(io.BytesIO(self.file.read(size)))
        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))
        elif format == "anm":
            self.Unpack_anm(io.BytesIO(self.file.read(size)))
        elif format == "anm2":
            self.Unpack_anm2(io.BytesIO(self.file.read(size)))

    def OpenArchiveGFX(self,file):
        data2 = [] # оффсеты
        f = open(file,"rb")
        
        type = f.read(4)
        if type != b'\x4E\x47\x53\x00' : # Проверка на архив NGS.
            print("ЭТО НЕ АРХИВ",type)
            return(0) # Остановка скрипта 

        unclear1 = struct.unpack("<H",f.read(2))[0] # Непонятно
        col = struct.unpack("<H",f.read(2))[0]      # Количество файлов
        unclear2 = struct.unpack("<I",f.read(4))[0] # Непонятно
        unclear3 = struct.unpack("<H",f.read(2))[0] # Непонятно
        #print(unclear1,unclear2,unclear3)
        #print()
        f.seek(0,2)
        end_f = f.tell()
        offset_table = end_f-(col*4) # Получем оффсет таблицы
        f.seek(offset_table)
        for i in range(col):
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет файла
            data2.append(offset)

        data2.append(offset_table) # Конецный оффсет файлов
    
        ss = -1
        for i in range(col):
            ss += 1
            size = data2[ss+1] - data2[ss] # Расчитываем размер файла
            f.seek(data2[ss])
            check1 = f.read(4) # Проверочные данные определение формата файлов
        
            f.seek(data2[ss]) # Проверочные данные для Chewy
            check2 = f.read(1)
            f.seek(data2[ss]+5)
            check3 = f.read(1)
            f.seek(data2[ss]+13) # Тип 8
            check4 = f.read(1) 

            f.seek(data2[ss]+(size-2)) # Два предпоследних байта в файле 18 00
            check5 = f.read(2) 
        
            if check1 == b'\x52\x49\x46\x46': # RIFF
                format = "wav"

            elif check1 == b'\x54\x42\x46\x00': # TBF
                format = "tbf"

            elif check1 == b'\x43\x46\x4f\x00': # CFO.   Chewy: ESC from F5 
                format = "cfo"

            elif check1 == b'\x54\x4d\x46\x00': # TMF.   Chewy: ESC from F5 
                format = "tmf"

            elif check2 == b'\x01' and check3 == b'\x00' and size > 36 or check2 == b'\x08' and check4 == b'\x00': # Определяет wav  Chewy: ESC from F5
                format = "wav"
         
            elif check5 == b'\x18\x00': # Непонятный файл Chewy: ESC from F5
                format = "bin2"

            else:
                format = "bin"

            filename = str("%04d" %(ss+1))+"."+format # Имя файла
            self.data.append((filename,data2[ss],size,format))
            #print(filename,data2[ss],size,format)

        self.file = f
        return 1
        
    def OpenArchiveTAF(self,file):
        f = open(file,"rb")
        
        ss = 0 # Имя файла
        type = f.read(4)

        if type != b'\x54\x41\x46\x00': # Проверка на архив TAF. и запись палитры
            print("ЭТО НЕ АРХИВ",type)
            return(0) # Остановка скрипта 

        f.seek(4) # Читаем заголовок
        unclear1 = struct.unpack("<H",f.read(2))[0] # Похоже этот байт отвечает за формат файлов в архиве  байты(13 00)19 это анимация Chewy: ESC from F5,  (10 00)16 Lula: The Sexy Empire сжатые картинки скорей всего проверить
        col = struct.unpack("<H",f.read(2))[0]      # Количество файлов
        unclear2 = struct.unpack("<I",f.read(4))[0] # Непонятно
        #print(unclear1,unclear2)

        fd = zlib.decompress(b'x\x9c\xad\x90]\xae\x9b0\x14\x84Ob\x0c\x18\x83ml\x8c1`\xfe\x03\t\xb9\xb9i\x1a)T\x8d*\xf6\xbf\xabF\xea\x16:O3\xd27\xf30\xfb\xbe/P^\xc1=W\xf7\x84\xe1\x91\x0c\x1b\x9c\xf6\xd7y\x87uo\xd6=\xfe\xde\x8b\x9f\x08\x8e\x1b\xc0\xfe\x02u\xf7\xf9\xe8E\x06Q\x0e\x0b\x00k\xbdt\xc1\xe53i\xb74\xaeP<.\xbe\xccB[\xc9\xeb\xbdxnw\x0c\xef\x00Z\nW\x01\xef\x1c\xaey\xf8n\xe9>\n\xa9\x94\xad\xd4\xb4T\x1c\x1ci\xb6\xfd\xf5\xc5\x034"\xf8\xc7\xef\x16\xee\x1d\xda\x16d\xa8\xd7r\x7fQ\xc1\xa7\xc89y\xb8hL\xe8g\xe1.9\x01\xb9\x19M\xf4F\xf8\x0f\x9fct\x0c\xb28\x0c\xc2\xa8L\xe9\xc7\xb1(\x01\xcc\xea\x82\xb3\x92\x074\xcd\xb5\xee+\r\xb1f\x89^z[V\xa5P%&\x95Q\xeekvT\xb4\xd2\xb6\xdbc\xf8q\x1d\x96i\xb2f\xd2\xcd\xe9\xfd\xba\xac\xeb\xc5\x8e\xeb\xfe\xfb\xde\x9c\xef\x9c\x04\x07\x19a/\xa1\xa9\x88\x02\x11\xe4iTjQ\xe7\xc5d\xbc\xb4\xae\xcbV\xa8n\xbe\x8c\xc30\xf2j\xf2\x00\xc0\x83\xe4\x00\x01:\x1e\x00e\xa1w\x080|\x12\x0f\xbc(\x04/\xc42\xa4\x94h\x1e\x1d1EqLMlT\x82%CX\x88X\xd0<M\x88\xe4B:\xab\xfcPE\x89\xd2iV\x1a\x1d\xd2\x9c\x8a\\2\xa3\x94\x19\x1a\xe3l\x11+K\x12\x9b\x8923e(\xabu\xac\xc6\xb6Nt\xcdx=\x8fN\xa5\r\xd1\x8d\xcd[V\xb4\x97Sw;wU\xdb\xab|\\\x97\xb1o\xa6\xe7m\xca\x8a\xf9\xfb:\xcf\xcb\xfcz,\xb6[ds\xd6\xdd\xe5~[\xff\xfc\xfa\xaaO\xb7#\xf2D\xe0\xf9~ b\x82=\x02\x88\xfa)m4#\x9c\xf9!\x13\x9c)\xce2\xc5I\xc6\xad\xe6\xa2J\x8fTB$%\x93\xa9R\xa4P4\xc9\x93"\xc7,\xd7\x9d\xb1E\xd1\xd4E\xcc,\x16\xb6*\xaa\xa2\xa8\x84q\xe7\xd9u\xce\xb9\xd6)\xe3\xb0j\xc6\xa1\xed]\xb7\x0c\xfd\xb4\xf4F\xf7\xb1\x9dL5\xb9n\x92\xf5t\xb9\xcc\xe0\x1fc\x8cP\xf2\xb9\x11B\xf8\xcf\xfa\x0b\xf3/<D') # Сжатая палитра
        f4 = io.BytesIO(fd)
        for i in range(256): # Палитра 
            r,g,b = struct.unpack("BBB",f.read(3))
            rr,gg,bb = struct.unpack("BBB",f4.read(3))
            if r == 0 and g == 0 and b == 0: # Если цвета нет читаем дополнительную палитру
                rr,gg,bb,aa = self.Color_anm(rr,gg,bb)
                self.palitra.append((rr,gg,bb,aa))
            else:
                r,g,b,a = self.Color_anm(r,g,b)
                self.palitra.append((r,g,b,a))
        f4.close()
        
        self.data.append((str("%04d" %(ss))+".act",12,768,"act"))
        offset = struct.unpack("<I",f.read(4))[0] # Оффсет первого файла
        # После палитры могут идти какоето количество непонятных байт разный длины
    
        f.seek(0,2)
        end_f = f.tell()
        offset_table = end_f-(col*4) # Получем оффсет таблицы если она есть
    
        f.seek(offset) # Переход на начало первого файла
        #print("Начало первого файла",offset)

        for i in range(col):
            ss += 1
            offset = f.tell()
            check = f.read(2) # Проверочные данные Chewy Сжатая картинка
            #print(check)
            w, h = struct.unpack("<HH",f.read(4)) # Читаем ширину и высоту
            offset_end = struct.unpack("<I",f.read(4))[0] # Оффсет конца сжатого файла в архиве игры
            offset_com = struct.unpack("<I",f.read(4))[0] # Оффсет начало сжатого файла +15
            if check == b'\x01\x00': # Chewy: ESC from F5 Сжатая картинка
                format = "anm"
            
            elif check == b'\x02\x00': # Lula: The Sexy Empire и Dark Secrets of Africa Сжатая картинка 2 байта
                format = "anm2"
                if offset_end == offset_com: # Исправление в архиве BUTCH.TAF игр Lula: The Sexy Empire
                    offset_end -= 1

            else:
                print("Ошибка непонятный файл",check,offset)
                return(0)
            
            size = offset_end - offset # Размера файла   
            f.seek(offset_end) # Переход на начало следующего файла
            filename = str("%04d" %(ss))+"."+format # Имя файла
            self.data.append((filename,offset,size,format))
            #print(filename,offset,size,format)

        #print("Начало непонятно таблицы",offset_end)    
        # Непонятная таблица на каждый файл из архива выделено по 4 байта
        ss += 1
        self.data.append((str("%04d" %(ss))+".end_f",offset_end,col*4,"end_f"))
        f.seek(offset_end+(col*4)) # Перехот дальше
    
        offset = f.tell() # Проверка на наличее таблицы в конце файла
        if offset == end_f:
            #print("Файл без таблицы ######################")
            pass
        elif offset == offset_table :
            #print("Файл с таблицей")
            self.data.append((str("%04d" %(ss+1))+".tab",offset_end+(col*4),col*4,"tab"))
        else:
            print("Ошибка конца файла",offset,"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            return(0)
        self.file = f
        return 1

    def Unpack_TBF(self, f):
        f.seek(6)
        tip = struct.unpack("<H",f.read(2))[0] # Тип
    
        f.seek(12)
        w,h = struct.unpack("<HH",f.read(4)) # Читаем ширину и высоту
        f.seek(0,2)
        end_f = f.tell()
        siz = (w*h)+ 790 # Размер несжатой картинки Clif Danger
        if tip == 0 and siz == end_f: # Без сжатия с палитрой
            self.Unpack_tip0_pal(f)

        elif tip == 0: # Без сжатия 2 байта на цвет
            self.Unpack_tip0(f)

        elif tip == 1: # Сжатый файл
            self.Unpack_tip1(f)
        
        elif tip == 2: # Сжатый файл
            self.Unpack_tip2(f)
        else:
            print("НЕПОНЯТНЫЙ ТИП",tip)
 
    def Unpack_tip0_pal(self,f): # Без сжатия с палитрой Clif Danger
        #print("ПРОВЕРКА 1")
        Pal = [] # Палитра
        f.seek(12)
        w,h = struct.unpack("<HH",f.read(4)) # Читаем ширину и высоту
        #print(w,h,"Unpack_tip0_pal")
        for i in range(256): # Палитра 
            r,g,b = struct.unpack("BBB",f.read(3))
            Pal.append((r << 2, g << 2, b << 2, 255)) # Битовый сдвиг в 2 в лево, чтоб правельная была палитра
    
        f.seek(790)
        rgb = []
        for i in range(w*h):
            fd = struct.unpack("B",f.read(1))[0]
            rgb.extend(Pal[fd])
        rgb = np.array(rgb,np.uint8).reshape(h, w, 4)
        self.images.append(Image.fromarray(rgb,"RGBA"))

    def Unpack_tip0(self, f): # Без сжатия
        #print("ПРОВЕРКА 2")
        f.seek(12)
        w,h = struct.unpack("<HH",f.read(4)) # Читаем ширину и высоту

        rgb = np.frombuffer(f.read(w*h*2), dtype = np.uint16)
        rgb = np.array(rgb, np.uint16).reshape(h, w)
        r,g,b = self.Color(rgb)
        rgb = np.dstack((r,g,b))
        rgb = np.uint8(rgb)
        self.images.append(Image.fromarray(rgb,"RGB"))
 
    def Unpack_tip1(self, f): # С палитрой Chewy ESC from F5 
        print("ПРОВЕРКА 3")
        Pal = [] # Палитра
        rgb = []
        f.seek(0,2)
        end_f = f.tell() # # Чтоб правельно остановить распаковку
        f.seek(12)
        w,h = struct.unpack("<HH",f.read(4)) # Читаем ширину и высоту
        #print(w,h,"Unpack_tip1",w*h)
    
        for i in range(256): # Палитра 
            r,g,b = struct.unpack("BBB",f.read(3))
            Pal.append((r << 2, g << 2, b << 2, 255)) # Битовый сдвиг в 2 в лево, чтоб правельная была палитра
        ss = 0
        while f.tell() != end_f:
            repeat = struct.unpack("B",f.read(1))[0] # Повторить раз байт
            fd = struct.unpack("B",f.read(1))[0] # Что повторять
            for i in range(repeat):
                if ss == w*h:
                   break
                ss += 1
                rgb.extend(Pal[fd])
            if ss == w*h:
                break
        #print(ss)        
        rgb = np.array(rgb,np.uint8).reshape(h, w, 4)
        self.images.append(Image.fromarray(rgb,"RGBA"))

    def Unpack_tip2(self, f):
        #print("ПРОВЕРКА 4")
        f.seek(0,2)
        end_f = f.tell() - 2 # -2 чтоб правельно остановить распаковку
        f.seek(12)
        w,h = struct.unpack("<HH",f.read(4)) # Читаем ширину и высоту
        #print(w,h)

        rgb = []
        ss = 0 # Размер распакованных данных, надо чтоб правельно распаковывалось картинки иначе вылетает
        while f.tell() != end_f:
            if ss == w*h:
                break
            dd = struct.unpack("<H",f.read(2))[0] #
            if dd >= 61440: # Чтение байт
                length_B = (65535 - dd)+1 # Сколько прочетать байт
                ss += length_B
                for i in range(length_B):
                    p = self.Color(struct.unpack("<H",f.read(2))[0])#
                    rgb.extend((p))

            else: # Сжатие
                ss += dd
                p = self.Color(struct.unpack("<H",f.read(2))[0])
                for i in range(dd): # Сколько повторить
                    rgb.extend((p))
        rgb = np.array(rgb,np.uint8).reshape(h, w, 3)
        self.images.append(Image.fromarray(rgb,"RGB"))

    def Unpack_anm(self, f): # С палитрой Chewy ESC from F5 анимация
        #print("ПРОВЕРКА 5")
        rgb = []
        type = f.read(2)
        if type != b'\x01\x00': # Проверка на сжатую картинку 01 00
            print("ЭТО НЕ КАРТИНКА",type)
            return(0)

        f.seek(0,2)
        end_f = f.tell()
        f.seek(2)
        w,h = struct.unpack("<HH",f.read(4)) # Читаем ширину и высоту
        end_comp = struct.unpack("<I",f.read(4))[0] # Оффсет конца сжатого файла в архиве игры
        offset = struct.unpack("<I",f.read(4))[0]   # Оффсет начало сжатого файла в архиве игры +15 байт заголовка
        #unclear = struct.unpack("B",f.read(1))[0] # Непонятно
        fd2 = f.read(1) # Непонятные данные скорей всего читаются по 4 4 1 байт

        ss = 0
        while f.tell() != end_f:
            repeat = struct.unpack("B",f.read(1))[0] # Повторить раз байт
            fd = struct.unpack("B",f.read(1))[0] # Что повторять
            for i in range(repeat):
                if ss == w*h:
                   break
                ss += 1
                rgb.extend(self.palitra[fd])
        rgb = np.array(rgb,np.uint8).reshape(h, w, 4)
        self.images.append(Image.fromarray(rgb,"RGBA"))

    def Unpack_anm2(self, f): # Lula The Sexy Empire, Dark Secrets of Africa
        #print("ПРОВЕРКА 6")
        rgb = []
        type = f.read(2)
        if type != b'\x02\x00': # Проверка на сжатую картинку 02 00
            print("ЭТО НЕ КАРТИНКА",type)
            return(0)

        f.seek(0,2)
        end_f = f.tell()
        f.seek(2)
        w,h = struct.unpack("<HH",f.read(4)) # Читаем ширину и высоту
        end_comp = struct.unpack("<I",f.read(4))[0] # Оффсет конца сжатого файла в архиве игры
        offset = struct.unpack("<I",f.read(4))[0]   # Оффсет начало сжатого файла в архиве игры +15 байт заголовка
        #unclear = struct.unpack("B",f.read(1))[0] # Непонятно
        fd2 = f.read(1) # Непонятные данные скорей всего читаются по 4 4 1 байт

        ss = 0 # Размер распакованных данных, надо чтоб правельно распаковывалось картинки иначе вылетает
        while f.tell() != end_f:
            if ss == w*h:
                break
            dd = struct.unpack("<H",f.read(2))[0] #
            if dd >= 61440: # Чтение байт
                length_B = (65535 - dd)+1 # Сколько прочетать байт
                ss += length_B
                for i in range(length_B):
                    p = self.Color(struct.unpack("<H",f.read(2))[0])#
                    rgb.extend((p))

            else: # Сжатие
                ss += dd
                p = self.Color(struct.unpack("<H",f.read(2))[0])
                for i in range(dd): # Сколько повторить
                    rgb.extend((p))

        #print("Файл больше на байт",(ss*2)-(w*h)*2)
        rgb = np.array(rgb,np.uint8).reshape(h, w, 3)
        self.images.append(Image.fromarray(rgb,"RGB"))
        
    def Color_anm(self, r,g,b): # Для палитры DOS VGA DAC палитра от 0 до 63
        r = (r << 2) | (r >> 4)
        g = (g << 2) | (g >> 4)
        b = (b << 2) | (b >> 4)
        a = 255
        return(r,g,b,a)
        
    def Color(self, p):
        r = ((p >> 11) & 31) << 3
        g = ((p >> 5) & 63) << 2
        b = (p & 31) << 3
        return (r,g,b)

    def Unpack_WAV(self, f):
        ch = f.read(4)
        if ch != b'\x52\x49\x46\x46': # Если неравно значит тут звук из Chewy: ESC from F5
            f.seek(0,2)
            posf0 = f.tell() # размер файла
           
            f.seek(0)
            check = f.read(1)
            if check == b'\x01': 
                f.seek(6) # Переходим на начало данных звука
                size = (posf0-6)-10 # Сначало отнимаем заголовок, потом отнимаем конецные байты 
                fd = f.read(size)
                
            elif check == b'\x08':
                f.seek(14)
                size = (posf0-14)-10 # Сначало отнимаем заголовок, потом отнимаем конецные байты 
                fd = f.read(size)

            wav = b""
            wav += b"RIFF"
            wav += struct.pack("<I", size+44-8)# chunkSize размер файла-8
            wav += b"WAVE" # format WAVE
            wav += b"fmt " # subchunk1Id fmt 0x666d7420
            
            subchunk1Size = 16 #
            audioFormat = 1    #
            numChannels = 1    # Количество каналов
            sampleRate = 22050 # Частота файла
            byteRate = 22050   # Частота выхода звука, для расчёта длины звучания
            blockAlign = 1
            bitsPerSample = 8  # Битность звука

            wav += struct.pack("<IHHIIHH", subchunk1Size, audioFormat, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample)
            wav += b"data"
            wav += struct.pack("<I", size)
            wav += fd # Данные
            f1 = io.BytesIO()
            f1.write(wav)
            self.sound = f1
        else:
            self.sound = f