#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Распаковка архивов .kid игры Voodoo Kid (Корабль похищенных душ) жанр квест

import os, sys, io, struct
from PIL import Image
import numpy as np
import zlib

NAME = "Voodoo Kid" 
FORMATS_ARCHIVE = ['kid'] 
TYPES_ARCHIVE = [('Voodoo Kid', ('*.kid'))]
GAMES = ["Voodoo Kid"]
AUTHOR = "ZetpeR xax007@yandex.ru" 

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app
        
        self.sup_formats = ["x_w",
                            "vsc",
                            "xlf",
                            "wav"]
 
        self.sup_types = {"x_w":1,
                          "vsc":2,
                          "xlf":3,
                          "wav":3}
        self.images = [] 
        self.sound = None 

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "kid":
            self.OpenArchiveKID(file)
    
    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        tip = data_res[4]
        self.file.seek(offset)
        if format == "x_w":
            f = io.BytesIO(self.file.read(size))
            f2 = self.Unpack_decompression(f, tip)
            
            name_act = name[:-4]+".PAL" # Поиск палитры 
            for i in range(len(self.data)): # Поиск индекса i    получаем индекс
                if self.data[i][0] == name_act: # Сверяет первый элемент списка с name_act
                    offset = self.data[i][1] # Открываем файл палитры
                    size = self.data[i][2]
                    tip = data_res[4]
                    self.file.seek(offset)
                    f = io.BytesIO(self.file.read(size))
                    f3 = self.Unpack_decompression(f, tip)
                    self.Unpack_X_W(f2, f3)
                    break

                elif i+1 == len(self.data):
                    #print("Нет палитры для файла",name)
                    for i in range(len(self.data)): # Поиск индекса i    получаем индекс
                        if self.data[i][0] == "052GA001.PAL": # Сверяет первый элемент списка с name_act
                            offset = self.data[i][1] # Открываем файл палитры
                            size = self.data[i][2]
                            tip = data_res[4]
                            self.file.seek(offset)
                            f = io.BytesIO(self.file.read(size))
                            f3 = self.Unpack_decompression(f, tip)
                            self.Unpack_X_W(f2, f3)
                            break
                    break
                else:
                    pass
                    #print("Не нашлось",i,self.data[i])

        elif format == "vsc":
            f = io.BytesIO(self.file.read(size))
            f2 = self.Unpack_decompression(f, tip)
            self.Unpack_VSC(f2)
            
        elif format == "wav" or format == "xlf":
            f = io.BytesIO(self.file.read(size))
            f2 = self.Unpack_decompression(f, tip)
            self.Unpack_WAV(f2)
            
    def Unpack_decompression(self, f, tip): # Распаковка сжатия
        if tip == 0: # Без сжатия
            return(f)
        elif tip == 4: # Сжатие
            fd = f.read()
            decompress = zlib.decompressobj(zlib.MAX_WBITS|32)
            fd2 = decompress.decompress(b'\x78\xda'+fd)
            f2 = io.BytesIO(fd2)
            return(f2)
        else:
            print("НЕПОНЯТНЫЙ ТИП ФАЙЛА",tip)
            return(0)

    def OpenArchiveKID(self,file):
        f = open(file,"rb")
        
        type = f.read(4) # Тип архива Burp 
        if type != b'\x42\x75\x72\x70': # Проверка на архив
            print("ЭТО НЕ АРХИВ",type)
            return(0) # Остановка скрипта 
     
        col_f = struct.unpack("<I",f.read(4))[0] # Количество файлов

        for i in range(col_f):
            size_unpacked = struct.unpack("<I",f.read(4))[0] # Размер распакованных данных
            size = struct.unpack("<I",f.read(4))[0]          # Размер
            offset_Name = struct.unpack("<I",f.read(4))[0]   # Оффсет имени файла в конце файла
            offset = struct.unpack("<I",f.read(4))[0]        # Оффсет
            tip = struct.unpack("<I",f.read(4))[0] # Тип данных сжатых данных 0 не сжат, 4 сжат. 

            posf = f.tell()
            f.seek(offset_Name) # Переход для чтения имени в конце файла
            b49 = struct.unpack("B",f.read(1))[0]         # Всегда 49
            length_name = struct.unpack("B",f.read(1))[0] # Длина имени
            filename = f.read(length_name).split(b"\x00")[0].decode("cp1251").replace("\\\\","\\") # Имя файла
            format = filename.split(".")[-1].lower()
            self.data.append((filename,offset,size,format,tip))
            #print(filename,size_unpacked,offset_Name,tip,"Оффсет и размер",offset,size)
            f.seek(posf) # Возврат в таблицу
        self.file = f
        return 1

    def Unpack_X_W(self, f2, f3):
        Pal = [] # Палитра
        f3.seek(0,2)
        posf0 = f3.tell()
        f3.seek(0)
        col_cbet = posf0//3
    
        for i in range(col_cbet): # Палитра  256
            r,g,b = struct.unpack("BBB",f3.read(3))
            Pal.append((r, g, b, 255)) 
        f3.close()
        
        rgb = []
        w,h = struct.unpack("<HH",f2.read(4)) # Читаем ширину и высоту
    
        for i in range(w*h):
            fd = struct.unpack("B",f2.read(1))[0]
            rgb.extend(Pal[fd])
        rgb = np.array(rgb,np.uint8).reshape(h, w, 4)
        self.images.append(Image.fromarray(rgb,"RGBA"))

    def Unpack_WAV(self, f):
        ch = f.read(4)
        if ch != b'\x52\x49\x46\x46':
            f.seek(24)
            fd = f.read()
            f2 = io.BytesIO(fd)
            self.sound = f2
        else:
            self.sound = f

    def Unpack_VSC(self,f):
        offset_tab_1 = struct.unpack("<I",f.read(4))[0] # Оффсет таблицы 1
        offset_tab_2 = struct.unpack("<I",f.read(4))[0] # Оффсет таблицы 2
        offset_tab_3 = struct.unpack("<I",f.read(4))[0] # Оффсет таблицы 3  ещё обозначает конец сжатого файла
        zeros = f.read(4)
        offset_pal = struct.unpack("<I",f.read(4))[0] # Оффсет палитры
        end_f = struct.unpack("<I",f.read(4))[0]   # Размер файла целиком
        #print(offset_tab_1,offset_tab_2,offset_tab_3,zeros,offset_pal,end_f)

        f.seek(offset_tab_2)     
        size_tab_2 = struct.unpack("<I",f.read(4))[0] -2 # Размер  -2 это уже сжатие 
        col_tab_2 = size_tab_2//4  # Количество сжатых файлов анимации +1
        #print("Количество сжатых файлов",col_tab_2,"col_tab_2 размер",size_tab_2+6)
        for i in range(col_tab_2-1): # Читаем таблицу 2
            unclear = struct.unpack("<I",f.read(4))[0]+offset_tab_2 # Оффсет начало сжатой графики 
        
        # Начало сжатых данных
        posf0 = f.tell()
        if offset_tab_3 > 0: # Размер сжатых данных      # Записываем сжатый файл
            size_comp = offset_tab_3 - posf0 # расчёт от таблицы 3 если она есть
        
        elif offset_pal > 0:
            size_comp = offset_pal - posf0 # Если есть палитра

        else:
            size_comp = end_f - posf0 # Если нет палитры

        f.seek(posf0)
        fd = f.read(size_comp)
        f3 = io.BytesIO(fd) # сжатый файл
    
        Pal = []
        if offset_pal > 0: # Палитра
            f.seek(offset_pal)
            for i in range(256): 
                r,g,b = struct.unpack("3B",f.read(3))
                Pal.append((r,g,b,255))
        else: # Нет палитры
            print("БЕЗ ПАЛИТРЫ")
            fd = zlib.decompress(b'x\x9c\xad\x92!\x92c1\x0cDu\x0f\x1dA\x07\xd0\x01\x1a\xea\x00\x82\x82>\x80\xa0\x81\xa1\xa1\xa1a\xe0\x07\x81\x81\x01\x03\x03\x02\x07,\\\xb00 p\xe0\x8e\xfe\x01v\xd0V\xb9\\vI\xf5\xdc\xdd2\xfd%\xfa\xf7\xba\xcd\xb88\xef\xd0\xd1\xdb\xeb\xe8Dl\x90\xc7TstP\x874\x10\\\xae\x89\x04M\xd0\xe3p\x07]V\xbf=\xef\x06|tq\xf0\xfb\xd7j\x99\t\xee&\xcb\xb5\x85\xf59\xdc4]\x0c\xda\xdcF\xa29\x94\x90B-|\x07_\x12\x9f\x0b\x0b\x14\xc2\xc3YT\xf6J\x80\xdc\xed\xe3\xbe\x1d\xe8B\t9\x82\xb7s*50D\x8ec\x0f/\xa9q\xed\xdc \xa1|\xefZ`\x85\xdc\xa6\xa4\x931\x89\xe8\xb0R\xce\xef+\xa7I\xa6EYPy=\xf7rn%\xc0\xe4~[{z\x80\xa7swQ\x98\n]:?\x16\x1c2\xc1#4\x1c\x97\xa6\xc6\x92a"\xd2\x94X\xa8\x1b\xcdnV\xd6\x8c\x03\x92\xc2.\x1c\x95O\xb75\xbb\x1bi\xf95\xf6\x12v\xcc\x10z\xdfg\x06\xd2h\x07\xae;U\x04rJ\x1c\x10+\xe3\xc1f\xd2J\xed\x19\x1e\t\x91\x0bA\xc8\x94Ciwo\x057U\xadfZ\x01hI\x80{e\xc6\x1d\xd8{\x81\xf9\xb3F\xa2\x94\xf5\x18\xf3\xe8[\x99\xbc\xd0\xccr\xf2-+\x9c\x82\x88X\xa5_\x16\x8al\xf4Z\xda\xce\x0b\x95\x16\xadN-\x17u\xac\xd1\x0cU\xfa\xdd\xf9\xac0\x19\xcay\xb1*]}F}\x8d\x8a\xc1\x89\xe8\x8a\xdad\tE\xf5\x10}\xfd\xb9\xb6\xc0\xd7\xc3\x07H\xcfJ\x11\xf9\x8cL0\xc0;\xf9\xa7\xff\xf7_\xd6\x8f\xc5oR\xc9\xedF') # Сжатая палитра для 010D1001.VSC, 173D0101.VSC
            f5 = io.BytesIO(fd) # Для 010D1001.VSC, 173D0101.VSC
            for i in range(256): 
                r,g,b = struct.unpack("3B",f5.read(3))
                Pal.append((r,g,b,255))
            f5.close()
        
        while True:
            if f3.tell() == size_comp:
                #print("Достигли конца файла ###\n")
                break
            rgb = []
            und2 = struct.unpack("<H",f3.read(2))[0] # Непонятный байт
            w,h = struct.unpack("<HH",f3.read(4))    # Ширина и высота
            und = struct.unpack("B",f3.read(1))[0]   # Непонятный байт
            #print("Высота и ширена",w,h,"Не понятный первый байт",und,"\n")
            ss = 0 # Счётчик распакованных байт
            number_lines = 0 # Нужно чтоб прервать распаковку
    
            while True:
                bait1 = struct.unpack("B",f3.read(1))[0] # Повторить прозрачныйц байт
                for i in range(bait1):
                    #rgb.extend(Pal[0]) # Оригинал
                    rgb.extend((0,0,0,0)) # Прозрачность
                ss += bait1
        
                if ss == w:
                    ss -= w
                    number_lines += 1
                    if number_lines == h:
                        #print("Конец распаковки",f3.tell())
                        break
                    bait4 = struct.unpack("B",f3.read(1))[0] # НЕПОНЯТНЫЙ БАЙТ
                    continue

                elif ss > w:
                    print("ОШИБКА значение распакованной строчки слишком большое",ss,f3.tell())
                    return(0)
        
                bait2 = struct.unpack("B",f3.read(1))[0] # * 4 Сколько прочетать не сжатых байт
                bait3 = struct.unpack("B",f3.read(1))[0] # + bait2
                size = int((bait2*4)+ bait3) # Сколько прочетать байт
                fd = f3.read(size)
                for ij in fd:
                    rgb.extend(Pal[ij])      

                ss += size
            rgb = np.array(rgb,np.uint8).reshape(h, w, 4)
            self.images.append(Image.fromarray(rgb,"RGBA"))