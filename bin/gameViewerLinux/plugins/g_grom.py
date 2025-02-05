#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Grom (ГРОМ)

import os, sys, io, struct
from PIL import Image
import numpy as np
import zlib

NAME = "Grom" 
FORMATS_ARCHIVE = ['pak', 'p01']
TYPES_ARCHIVE = [('Grom', ('*.pak', '*.p01'))]
GAMES = ["Grom"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["jpg",
                            "tga",
                            "actor",
                            "ai",
                            "anim",
                            "apd",
                            "dsc",
                            "food",
                            "gdlg",
                            "inventory",
                            "item",
                            "lua",
                            "mdl",
                            "medkit",
                            "mine",
                            "minedet",
                            "object3d",
                            "txt",
                            "vehicle",
                            "weapon",
                            "rds",
                            "dat"]
       
        self.sup_types = {"jpg":1,
                          "tga":1,
                          "actor":4,
                          "ai":4,
                          "anim":4,
                          "apd":4,
                          "dsc":4,
                          "food":4,
                          "gdlg":4,
                          "inventory":4,
                          "item":4,
                          "lua":4,
                          "mdl":4,
                          "medkit":4,
                          "mine":4,
                          "minedet":4,
                          "object3d":4,
                          "txt":4,
                          "vehicle":4,
                          "weapon":4,
                          "rds":2,
                          "dat":2}
        self.images = []  
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "pak" or format == "p01":
            self.OpenArchiveRES(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format in ["jpg", "tga"]:
            f2 = self.Decompression_z(io.BytesIO(self.file.read(size)),data_res[4],data_res[5],size)
            self.Unpack_TGA(f2)

        elif format in ["actor", "ai", "anim", "apd", "dsc", "food", "gdlg", "inventory", "item", "lua", "mdl", "medkit", "mine", "object3d", "txt", "vehicle", "weapon"]:
            f2 = self.Decompression_z(io.BytesIO(self.file.read(size)),data_res[4],data_res[5],size)
            self.Unpack_TXT(f2)  
            
        elif format == "rds":
            f2 = self.Decompression_z(io.BytesIO(self.file.read(size)),data_res[4],data_res[5],size)
            self.Unpack_RDS(f2)

        elif format == "dat":
            dirname, filename = os.path.split(name)
            check = filename.find('bkg') # Ищем имя файла текстуры bkg
            if check == -1: # Проверка на архив
                #print("Этот файл не является архивом с текстурами",filename)
                pass
            else:
                f2 = self.Decompression_z(io.BytesIO(self.file.read(size)),data_res[4],data_res[5],size)
                self.Unpack_DAT(f2)

    def OpenArchiveRES(self,file):
        self.data = []
        f = open(file,"rb")

        f.seek(-22,2) # С конца файла 22 байта
        PK = f.read(2) # PK
        unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно
        col = struct.unpack("<H",f.read(2))[0] # Количество файлов
        col_2 = struct.unpack("<H",f.read(2))[0] # Количество файлов
        size_tab = struct.unpack("<I",f.read(4))[0] # Размер таблицы файлов
        offset_tab = struct.unpack("<I",f.read(4))[0] # Оффсет таблицы файлов
        unclear = struct.unpack("<H",f.read(2))[0] # Непонятно
        f.seek(offset_tab)

        for i in range(col):
            posf0 = f.tell()
            PK = f.read(2) # PK
            unclear_1 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_2 = struct.unpack("<H",f.read(2))[0] # Непонятно
            comp = struct.unpack("<H",f.read(2))[0] # Непонятно 10 без сжатия 20 сжатие
            unclear_3 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_4 = struct.unpack("<H",f.read(2))[0] # Непонятно
            fd = f.read(8) # Непонятно
            size = struct.unpack("<I",f.read(4))[0] # Размер сжатого файла
            unclear_5 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_6 = struct.unpack("<H",f.read(2))[0] # Непонятно
            len_name = struct.unpack("<H",f.read(2))[0] # Длина имени
            unclear_7 = struct.unpack("<I",f.read(4))[0] # Непонятно
            unclear_8 = struct.unpack("<I",f.read(4))[0] # Непонятно
            unclear_9 = struct.unpack("<H",f.read(2))[0] # Непонятно
            unclear_10 = struct.unpack("<H",f.read(2))[0] # Непонятно
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            size_zag = 30 + len_name # Размер заголовка до сжатых данных

            posf = f.tell()
            f_path = bytearray(f.read(len_name)) # Имя файла зашифрованное
            for x in range(len(f_path)):
                f_path[x] = f_path[x] ^ 0x80

            try: # Исключения
                f_path = f_path.decode("utf8").replace("\\\\","\\")
            except: # Если не зашифрованные имена
                f.seek(posf)
                f_path = f.read(len_name).decode("utf8").replace("\\\\","\\")
            if size == 0: # Просто путь папки fx/
                pass
            else:
                format = f_path.split(".")[-1].lower()
                self.data.append((f_path,offset,size+size_zag,format,size_zag,comp))
        self.file = f
        
    def Decompression_z(self,f,size_zag,comp,size):
        f.read(size_zag)
        if size == 2648: # Исправление для maps.p01 файл railway/script.lua
            f.read(17) # Какието непонятные байты
        fd = f.read()

        if comp == 10: # Без сжатия
            fd_decomp = fd
        elif comp == 20: # Со сжатием
            decompress = zlib.decompressobj(zlib.MAX_WBITS|32)
            fd_decomp = decompress.decompress(b'\x78\xda'+fd)
        else:
            print("Непонятно Ошибка")
            return(0)
        f2 = io.BytesIO(fd_decomp)
        return(f2)

    def Unpack_TGA(self, f):
        try: # Исключения
            image = Image.open(f)
            self.images = [image]
        except :
            print("Не поддерживается")

    def Unpack_TXT(self, f): 
        try: # Исключения
            self.text = f.read().decode("utf8")
        except:
            f.seek(0)
            self.text = f.read().decode("cp1251")
            
    def Unpack_RDS(self, f):
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(64)
        w,h = struct.unpack("<II",f.read(8)) # Ширина и высота
        col = struct.unpack("<I",f.read(4))[0] # Количество
        #print(mult_file,"Ширина и высота",w,h,"Количество картинок",col)
        f.seek(112)
        for i in range(col):
            posf = f.tell()
            if posf+((w*h)*4) > end_f or posf == end_f:
                break
            rgb = np.frombuffer(f.read(w*h*4), dtype = np.uint8)
            rgb = np.array(rgb,np.uint8).reshape(h, w, 4)
            b,g,r,a = np.rollaxis(rgb, axis = -1)
            rgb = np.dstack([r,g,b,a])
            self.images.append(Image.fromarray(rgb,"RGBA"))
            w = w // 2
            h = h // 2
            #print("Позиция в файле новая ширина и высота",f.tell(),w,h)
        f.close()
        
    def Unpack_DAT(self, f):
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(8)
        # Заголовок 24 байт
        #unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно
        #unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно
        w,h = struct.unpack("<II",f.read(8)) # Ширина и высота
        #unclear_3 = struct.unpack("<I",f.read(4))[0] # Непонятно
        #unclear_4 = struct.unpack("<I",f.read(4))[0] # Непонятно
        f.seek(24)

        while True:
            if f.tell() == end_f:
                #print("Достигли конца файла)
                break
            # Заголовок 40 байт Непонятно
            f.seek(40,1)
            rgb = np.frombuffer(f.read(w*h*4), dtype = np.uint8)
            rgb = np.array(rgb,np.uint8).reshape(h, w, 4)
            b,g,r,a = np.rollaxis(rgb, axis = -1)
            rgb = np.dstack([r,g,b]) # Избавляемся от прозрачности а то картинку не видно
            self.images.append(Image.fromarray(rgb,"RGB"))