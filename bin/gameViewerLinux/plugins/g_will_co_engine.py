#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Critical Point                   [ARC, WIP, MSK, WAV, SCR]
# Gibo                             [ARC, WIP, MSK, WAV, OGG, SCR]
# Little My Maid                   [ARC, WIP, MSK, WAV, OGG, MP3, SCR]
# Snow Drop                        [ARC, WIP, MSK, WAV, SCR]
# Enzai                            [ARC, WIP, MSK, WAV, OGG, SCR]
# Laughter Land                    [ARC, WIP, MSK, MOS, OGG]
# Under the Moon                   [ARC, WIP, MSK, MOS, OGG]
# Princess Waltz                   [ARC, WIP, MSK, WAP, OGG]
# Zettai Fukujuu Meirei            [ARC, WIP, MSK, OGG]
# Yume Miru Kusuri                 [ARC, WIP, MSK, OGG]
# Reijou Caster 2                  [ARC, WIP, MSK, WAV, OGG, SCR]
# Ijiwaru My Master                [ARC, WIP, MSK, MOS, OGG]
# I/O-revision II                  [ARC, WIP, MSK, OGG]
# Onna Kyoushi Chijoku no Senritsu [ARC, WIP, MSK, OGG, SCR]
# Onna Kyoushi -Nikutai Jugyou-    [ARC, WIP, MSK, WAV, OGG]
# Seido Maria                      [ARC, WIP, MSK, MOS, OGG]
# Toriko Hime                      [ARC, WIP, MSK, MOS, OGG]
# Folklore Jam                     [ARC, WIP, MSK, OGG]
# Mama Love                        [ARC, WIP, MSK, MOS, OGG]
# Nidozaki! Tartelette             [ARC, WIP ,WAP, MSK, MOS, OGG, PNG]
# Sekai de Ichiban Dame na Koi     [ARC, WIP, MSK, MOS, OGG]

# Версия движка 2
# Ojou-sama wa Gokigen Naname                       [ARC, PNG, MOS, PNA, OGG]
# Cocoro@Function!                                  [ARC, PNG, MOS, PNA, OGG]
# Cocoro@Function! NEO                              [ARC, PNG, MOS, PNA, OGG]
# Baka Moe Heart ni Ai wo Komete!                   [ARC, PNG, MOS, PNA, OGG]
# Kono Oozora ni Tsubasa wo Hirogete                [ARC, PNG, MOS, PNA, OGG]
# Kono Oozora ni Tsubasa wo Hirogete FLIGHT DIARY   [ARC, PNG, MOS, PNA, OGG]
# Omoi o Sasageru Otome no Melody                   [ARC, PNG, MOS, PNA, OGG]
# Tsukiakari ni Modaeru Harame                      [ARC, PNG, MOS, PNA, OGG]
# Koisuru Natsu no Last Resort                      [ARC, PNG, MOS, PNA, OGG]
# Yobai Suru Shichinin no Harame                    [ARC, PNG, MOS, PNA, OGG]
# Yobai Suru Shichinin no Harame 2                  [ARC, PNG, MOS, PNA, OGG]
# Kanojo to Ore to Koisuru Resort                   [ARC, PNG, MOS, PNA, OGG]
# Natsuiro Recipe                                   [ARC, PNG, MOS, PNA, OGG]
# Tegome ni Sareru Kyuunin no Otome                 [ARC, PNG, MOS, PNA, OGG]
# Tegome ni Sareru Kyuunin no Otome - The Motion    [ARC, PNG, MOS, PNA, OGG]
# Otome ga Kanaderu Koi no Aria                     [ARC, PNG, MOS, PNA, OGG]
# Otome ga Kanaderu Koi no Aria ~Kimi ni Sasageru Encore~ [ARC, PNG, MOS, PNA, OGG]
# Sakura Mau Otome no Rondo                         [ARC, PNG, MOS, PNA, OGG]
# Koi Suru Kimochi no Kasanekata                    [ARC, PNG, MOS, PNA, OGG]
# Koi Suru Kimochi no Kasanekata ~Kasaneta Omoi o Zutto~ [ARC, PNG, MOS, PNA, OGG]
# Ojou-sama wa Sunao ni Narenai                     [ARC, PNG, MOS, PNA, OGG]
# Midara ni Aegu Shichinin no Yobai Suru Harame     [ARC, PNG, MOS, PNA, OGG]
# Ane o Tasukeru Tame Nokosareta Shimai o Yogosu Haitoku no Hibi [ARC, PNG, MOS, PNA, OGG]
# Golden Marriage                                   [ARC, PNG, MOS, PNA, OGG]
# Golden Marriage -Jewel Days-                      [ARC, PNG, MOS, PNA, OGG]
# Pure Song Garden!                                 [ARC, PNG, MOS, PNA, OGG]
# Toriko no Shirabe Midara ni Aegu Otome Sextet     [ARC, PNG, MOS, PNA, OGG]
# Toriko no Shizuku Natsu no Gouka Kyakusen de Kegasareru Otome-tachi [ARC, PNG, MOS, PNA, OGG]
# Toriko no Kusari                                  [ARC, PNG, MOS, PNA, OGG]
# Mirai Kanojo                                      [ARC, PNG, MOS, PNA, OGG]
# Yakimochi Kanojo no Ichizu na Koi                 [ARC, PNG, MOS, PNA, OGG]
# Otome ga Irodoru Koi no Essence                   [ARC, PNG, MOS, PNA, OGG]
# Otome ga Irodoru Koi no Essence ~Egao de Orinasu Mirai~ [ARC, PNG, MOS, PNA, OGG]
# Houkago ni Midareru Ane Kyoushi to Tonari no Heya de Aegu Imouto [ARC, PNG, MOS, PNA, OGG]
# Miagete Goran Yozora no Hoshi o                   [ARC, PNG, MOS, PNA, OGG]
# Miagete Goran Yozora no Hoshi o Fine Days         [ARC, PNG, MOS, PNA, OGG]

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Will Co. Engine"
FORMATS_ARCHIVE = ['arc']
TYPES_ARCHIVE = [('Will Co. Engine', ('*.arc'))]
GAMES = ["Critical Point",
         "Enzai",
         "Gibo",
         "Little My Maid",
         "Laughter Land",
         "Snow Drop",
         "Under the Moon",
         "Princess Waltz",
         "Zettai Fukujuu Meirei",
         "Yume Miru Kusuri",
         "Ijiwaru My Master",
         "I/O-revision II",
         "Onna Kyoushi Chijoku no Senritsu",
         "Seido Maria",
         "Folklore Jam",
         "Mama Love",
         "Nidozaki! Tartelette",
         "Sekai de Ichiban Dame na Koi",
         "Reijou Caster 2",
         "Toriko Hime",
         "Onna Kyoushi -Nikutai Jugyou-",
         "Ojou-sama wa Gokigen Naname", # Версия движка 2
         "Cocoro@Function!",
         "Cocoro＠Function! NEO",
         "Baka Moe Heart ni Ai wo Komete!",
         "Kono Oozora ni Tsubasa wo Hirogete",
         "Kono Oozora ni Tsubasa wo Hirogete FLIGHT DIARY",
         "Koisuru Natsu no Last Resort",
         "Yobai Suru Shichinin no Harame",
         "Yobai Suru Shichinin no Harame 2",
         "Kanojo to Ore to Koisuru Resort",
         "Natsuiro Recipe",
         "Tegome ni Sareru Kyuunin no Otome",
         "Tegome ni Sareru Kyuunin no Otome - The Motion",
         "Otome ga Kanaderu Koi no Aria",
         "Otome ga Kanaderu Koi no Aria ~Kimi ni Sasageru Encore~",
         "Sakura Mau Otome no Rondo",
         "Koi Suru Kimochi no Kasanekata",
         "Koi Suru Kimochi no Kasanekata ~Kasaneta Omoi o Zutto~",
         "Ojou-sama wa Sunao ni Narenai",
         "Midara ni Aegu Shichinin no Yobai Suru Harame",
         "Ane o Tasukeru Tame Nokosareta Shimai o Yogosu Haitoku no Hibi",
         "Golden Marriage",
         "Golden Marriage -Jewel Days-",
         "Pure Song Garden!",
         "Toriko no Shirabe Midara ni Aegu Otome Sextet",
         "Toriko no Shizuku Natsu no Gouka Kyakusen de Kegasareru Otome-tachi",
         "Toriko no Kusari",
         "Mirai Kanojo",
         "Yakimochi Kanojo no Ichizu na Koi",
         "Otome ga Irodoru Koi no Essence",
         "Otome ga Irodoru Koi no Essence ~Egao de Orinasu Mirai~",
         "Tsukiakari ni Modaeru Harame",
         "Omoi o Sasageru Otome no Melody",
         "Houkago ni Midareru Ane Kyoushi to Tonari no Heya de Aegu Imouto",
         "Miagete Goran Yozora no Hoshi o",
         "Miagete Goran Yozora no Hoshi o Fine Days"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["wip",
                            "msk",
                            "mos",
                            "wap",
                            "png",
                            "pna",
                            "wav",
                            "ogg",
                            "mp3",
                            "scr"]

        self.sup_types = {"wip":2,
                          "msk":2,
                          "mos":2,
                          "wap":2,
                          "png":1,
                          "pna":2,
                          "wav":3,
                          "ogg":3,
                          "mp3":3,
                          "scr":4}
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
        if format in ["wip", "msk", "wap"]:
            self.Unpack_WIP(io.BytesIO(self.file.read(size)))
        elif format == "wav" or format == "ogg":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))
        elif format == "scr":
            self.Unpack_SCR(io.BytesIO(self.file.read(size)))
        elif format == "mp3":
            self.Unpack_MP3(io.BytesIO(self.file.read(size)))
        elif format == "mos":
            self.Unpack_MOS(io.BytesIO(self.file.read(size)))
        elif format == "pna":
            self.Unpack_PNA(io.BytesIO(self.file.read(size)))
        elif format == "png":
            self.Unpack_PNG(io.BytesIO(self.file.read(size)))
            
    def OpenArchive(self,file):
        f = open(file,"rb")
        f.seek(4)
        fd = f.read(4)
        if fd in [b'ANM\x00', b'MAT\x00', b'MOS\x00', b'MP3\x00', b'MSK\x00', b'OGG\x00', b'SCR\x00', b'TBL\x00', b'WAP\x00', b'WAV\x00', b'WIP\x00', b'WSC\x00',]:
            self.OpenArchiveARC(file)
        else:
            self.OpenArchiveARC_V2(file)
        f.close()
        
    def OpenArchiveARC(self,file):
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
                filename = f.read(9).split(b"\x00")[0].decode("cp1251").replace("\\\\","\\")+"."+i[0] # Имя файла
                size = struct.unpack("<I",f.read(4))[0] # Размер
                offset = struct.unpack("<I",f.read(4))[0] # Оффсет
                self.data.append((filename,offset,size,i[0]))
        self.file = f
        return 1

    def OpenArchiveARC_V2(self,file):
        f = open(file,"rb")
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        Start_files = struct.unpack("<I",f.read(4))[0]+8 # Начало файлов оффсет

        #print("Количество файлов",col,"Начало файлов",Start_files)
        for i in range(col):
            size = struct.unpack("<I",f.read(4))[0] # Размер
            offset = struct.unpack("<I",f.read(4))[0] + Start_files # Непонятно

            f_path = b'' # Читаем имя файла до байта 00 00  
            while True: 
                bait = f.read(2) # Байт строчки
                if bait == b'\x00\x00':
                    f_path = f_path.decode("utf-16-le").replace("\\\\","\\") # Имя файла 
                    break
                f_path += bait # Прибавляем байты
            format = f_path.split(".")[-1].lower() 
            self.data.append((f_path,offset,size,format))
        self.file = f
        return 1
        
    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_MP3(self, f):
        while True:
            posf0 = f.tell()
            bait = f.read(1) # Байт строчки
            if bait != b'\x00':
                break
        f.seek(posf0)
        fd = f.read()
        f2 = io.BytesIO(fd)
        self.sound = f2
        
    def Unpack_MOS(self, f):
        fd = f.read(4)
        f.seek(0)
        if fd == b'\x89PNG': # Если это просто картинка
            self.Unpack_PNG(f)
        else:
            self.Unpack_WIP(f)

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

    def Unpack_SCR(self, f):
        f2 = io.BytesIO()
        f3 = io.StringIO() # Виртуальный файл для текста
        f.seek(0,2)
        col = f.tell()
        f.seek(0)
        for i in range(col):
            fd = struct.unpack("B",f.read(1))[0] 
            fh = fd & 3 # Это 3 два бита 11
            fd = fd >> 2
            fd = fd | (fh<<6)
            fd = struct.pack("B", fd)
            f2.write(fd)
        f.close()

        f2.seek(0)
        text = b'' # Байты текста
        for i in range(col):
            bait = f2.read(1) # Байт 
            if bait in [b'\x00', b'\x80', b'\x81', b'\x82', b'\x83', b'\x84', b'\x85', b'\x86', b'\x87', b'\x88', b'\x89', b'\x8a', b'\x8b', b'\x8c', b'\x8d', b'\x8e', b'\x8f', b'\x90', b'\x91', b'\x92', b'\x93', b'\x94', b'\x95', b'\x96', b'\x97', b'\x98', b'\x99', b'\x9a', b'\x9b', b'\x9c', b'\x9d', b'\x9e', b'\x9f', b'\xa3', b'\xa5', b'\xa6', b'\xa7', b'\xa9', b'\xab', b'\xac', b'\xad', b'\xae', b'\xb1', b'\xb2', b'\xb3', b'\xb4', b'\xb5', b'\xb6', b'\xbb', b'\xbc', b'\xbd', b'\xbe',b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07', b'\x08', b'\t', b'\n', b'\x0b', b'\x0c', b'\r', b'\x0e', b'\x0f', b'\x10', b'\x11', b'\x12', b'\x13', b'\x14', b'\x15', b'\x16', b'\x17', b'\x18', b'\x19', b'\x1a', b'\x1b', b'\x1c', b'\x1d', b'\x1e', b'\x1f', b'\x7f', b'\xa0', b'\xa1', b'\xa2', b'\xa4', b'\xa8', b'\xaa', b'\xaf', b'\xb0', b'\xb7', b'\xb8', b'\xb9', b'\xba', b'\xbf']:
                if text != b'': # Если текст неравен пустой строчки то это текст
                    fd = text.decode("cp1251")
                    f3.write(fd+"\n")
                text = b''

            else:
                text += bait # Прибавляем байт
        f2.close()
        f3.seek(0)
        self.text = f3.read()
        f3.close()
        
    def Unpack_PNG(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_PNA(self, f):
        data2 = [] # Список файлов
        dataf = f.read() # Читаем весь файл и записываем его в dataf для поиска
        offset = 0 # чтоб начать с нуля

        while True:
            offset = self.Search_PNG(b"\x89PNG",dataf,offset) # HEX значение для поиска байт PNG
            offset_end = self.Search_PNG(b'\x00\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82',dataf,offset) # Ищем конец файла PNG  12 байтов
            size = (offset_end + 12)-offset # Получаем размер файла
            if offset == -1: # Если нечего не нашли
                break
            #print("Оффсет",offset,"Размер файла",size,"\n")
            data2.append((offset,size))
            offset += 1 # Чтоб искать картинку дальше
            
        for i in data2:
            f.seek(i[0])
            fd = f.read(i[1])

            f2 = io.BytesIO(fd) # Открываем картинку и копирвуем её
            image = Image.open(f2)
            self.images.append(image.copy())
            f2.close()

    def Search_PNG(self, Search_byte,dataf,yy):
        offset = dataf.find(Search_byte,yy) # Поиск значения Search_byte, по месту нахождения в файле yy
        if offset > -1: # Если нашли данные
            return(offset)
        else:
            return(offset) # Тут будет -1 Значит это конец файла