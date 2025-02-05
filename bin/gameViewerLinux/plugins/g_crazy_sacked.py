#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Sacked (Оторва) Gefeuert! Dein letzter Tag... 
# Crazy School: Schulverweis! (Оторва в Школе) Sacked in School 

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Crazy Sacked" 
FORMATS_ARCHIVE = ['ogd']
TYPES_ARCHIVE = [('Crazy Sacked', ('*.ogd'))]
GAMES = ["Sacked",
         "Crazy School: Schulverweis!"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app
        
        self.sup_formats = ["sprite"]
        self.sup_types = {"sprite":1}
        self.images = []   
        self.sound = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "ogd":
            self.OpenArchiveOGD(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        file2 = data_res[4]
        self.file.seek(offset)
        if format == "sprite":
            self.Unpack_SPRITE(io.BytesIO(self.file.read(size)),file2)

    def OpenArchiveOGD(self,file):
        self.data = [] 
        f = open(file,"rb")

        type = f.read(16) # Тип архива
        if type != b'#ODIN_ENGINECF10': # Проверка на архив
            print("ЭТО НЕ АРХИВ",type)
            return(0)
        f.seek(0,2)
        end_f = f.tell()

        f.seek(20)
        offset_block = struct.unpack("<I",f.read(4))[0] # Оффсет таблицы файлов
        f.seek(offset_block)

        col = struct.unpack("<I",f.read(4))[0] # Количество файлов

        for i in range(col):
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            posf = f.tell() # Запомнить позицию
            if f.tell() == end_f: # Если достигнут конец файла
                size = end_f - offset # Расчёт размера файла по концу файла
            else:
                size = struct.unpack("<I",f.read(4))[0]
                size -= offset # Расчёт размера файла по второму оффсету

            f.seek(offset+14) # Переходим на начало внутреннего имени
            filename = f.read(50).split(b"\x00")[0].decode("utf8").replace("\\\\","\\")
            if filename == "SPRITE": # Информация о картинки ширина и высота в файле
                f.seek(posf)
                offset_2 = struct.unpack("<I",f.read(4))[0] # Оффсет картинки SPRITECB8 или палиты
                posf2 = f.tell()
                f.seek(offset_2+14)
                filename2 = f.read(50).split(b"\x00")[0].decode("utf8").replace("\\\\","\\")
                if filename2 == "SPRITEPAL":
                    size += 1048 # Размер файла палитры если он есть
                    f.seek(posf2)
                    offset_2 = struct.unpack("<I",f.read(4))[0] # Читаем следущий оффсет чтоб правельно расчитать
                    posf2 = f.tell()

                f.seek(posf2)
                offset_3 = struct.unpack("<I",f.read(4))[0] #
                size += offset_3 - offset_2 # Получаем размер картинки и прибавляем его к файлу
                self.data.append((str("%05d" %(i+1))+"."+str(filename), offset, size, filename.lower(),file))
                
            else:
                self.data.append((str("%05d" %(i+1))+"."+str(filename), offset, size, filename.lower()))
            f.seek(posf)
        self.file = f

    def Unpack_SPRITE(self, f, file):
        f.seek(541)
        w,h = struct.unpack("HH",f.read(4)) # Читаем ширину и высоту картинки
        f.seek(565+14)
        filename = f.read(50).split(b"\x00")[0].decode("utf8").replace("\\\\","\\")
        if filename == "SPRITEPAL":
            f.seek(565+24)
            
            f5 = io.BytesIO() # Чтение внешний палитры 
            for j in range(256): # Палитра 768 байта
                fd = f.read(3) # RGB
                f5.write(fd)
                a = f.read(1)
            f5.seek(0)
            Pal = np.frombuffer(f5.read(256*3), dtype=np.uint8)
            Pal = np.array(Pal, np.uint8).reshape(256, 3)
            f5.close()
            
            f.seek(565+1048+24) # Первый файл с высотой и шириной, второй файл палитра, третий файл картинка переходим на чтение картинки 
            
            rgb_pal = np.frombuffer(f.read(w*h), dtype=np.uint8)
            rgb = Pal[rgb_pal]
            rgb = rgb.reshape(h, w, 3)
            self.images.append(Image.fromarray(rgb,"RGB"))
            
        elif filename == "SPRITECB8":
            (dirname, filen) = os.path.split(file)

            if filen == "CS_OBJECTS.OGD" or filen == "CS_CHARS.OGD" or filen == "CS_FX.OGD" or filen == "CS_GAMEGUI.OGD" or filen == "CS_MAPTILES.OGD": # Палитра для файлов
                if os.path.exists(dirname+"\\"+"CS_INGAME.PAL") == False:
                    print("Ошибка нет в папки файла CS_INGAME.PAL")
                    return(0)
                else:
                    f2 = open(dirname+"\\"+"CS_INGAME.PAL","rb") # Читаем палитру в память
            elif filen == "CS_GUI.OGD":
                if os.path.exists(dirname+"\\"+"CS_MENUE.PAL") == False:
                    print("Ошибка нет в папки файла CS_MENUE.PAL")
                    return(0)
                else:
                    f2 = open(dirname+"\\"+"CS_MENUE.PAL","rb")
            elif filen == "CS_MINIGAME.OGD":
                if os.path.exists(dirname+"\\"+"CS_MINIGAME.PAL") == False:
                    print("Ошибка нет в папки файла CS_MINIGAME.PAL")
                    return(0)
                else:
                    f2 = open(dirname+"\\"+"CS_MINIGAME.PAL","rb")
            else:
                print("ОШИБКА НЕПОНЯТНО КАКАЯ НУЖНА ПАЛИТРА")
                return(0)

            f5 = io.BytesIO() # Чтение внешний палитры 
            for j in range(256): # Палитра 768 байта
                b = f2.read(1)
                g = f2.read(1)
                r = f2.read(1)
                f5.write(r)
                f5.write(g)
                f5.write(b)
            f5.seek(0)
            Pal = np.frombuffer(f5.read(256*3), dtype=np.uint8)
            Pal = np.array(Pal, np.uint8).reshape(256, 3)
            f5.close()
            f2.close()

            f.seek(565+24) # Переходим на чтение картинки
            
            rgb_pal = np.frombuffer(f.read(w*h), dtype=np.uint8)
            rgb = Pal[rgb_pal]
            rgb = rgb.reshape(h, w, 3)
            self.images.append(Image.fromarray(rgb,"RGB"))
            
        elif filename == "SPRITECB":
            f.seek(565+23) # Переходим на чтение картинки
            rgb = np.frombuffer(f.read(w*h*4), dtype = np.uint8)
            rgb = np.array(rgb,np.uint8).reshape(h, w, 4)
            b,g,r,a = np.rollaxis(rgb, axis = -1)
            rgb = np.dstack([r,g,b,a])
            self.images.append(Image.fromarray(rgb,"RGBA"))
            
        else:
            print("ОШИБКА НЕПОНЯТНО внутрение имя файла",filename)
            return(0)