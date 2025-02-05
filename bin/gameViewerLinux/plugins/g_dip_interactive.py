#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Братья Пилоты Догонялки
# Кот Леопольд. Догонялки
# Ну, погоди! Выпуск 4. Догонялки

import os, sys, io, struct
from PIL import Image

NAME = "DIP Interactive" 
FORMATS_ARCHIVE = ['res']
TYPES_ARCHIVE = [('DIP Interactive', ('*.res'))]
GAMES = ["Братья Пилоты Догонялки",
         "Кот Леопольд. Догонялки",
         "Ну, погоди! Выпуск 4. Догонялки"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["png",
                            "ogg",
                            "txt"]

        self.sup_types = {"png":1,
                          "ogg":3,
                          "txt":4}

        self.images = []  
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "res":
            self.OpenArchiveRES(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "png":
            self.Unpack_PNG(io.BytesIO(self.file.read(size)))
        elif format == "ogg":
            self.Unpack_OGG(io.BytesIO(self.file.read(size)))
        elif format == "txt":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))

    def OpenArchiveRES(self,file):
        self.data = []
        f = open(file,"rb")
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)
        type = f.read(4) # Тип архива
        if type != b'PaR6': # Проверка на архив
            print("ЭТО НЕ АРХИВ",type)
            return(0) # Остановка скрипта 
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов

        for i in range(col):
            tip = struct.unpack("B",f.read(1))[0] # Непонятно возможно это тип файла
            size = struct.unpack("<I",f.read(4))[0] # Размер
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет

            #print("Тип",tip,"Оффсет размер файла",offset,size)
            posf0 = f.tell() # Для возврата
            f.seek(offset)
            fd = f.read(4) # Проверочные байты
            f.seek(posf0) # Возврат назад

            if tip == 8 and fd == b'\x89PNG': # png
                f_path = "\\Png\\"+str("%010d" %offset)+" "+str(tip)+".png"

            elif tip == 9 and fd == b'OggS': # ogg Звуки
                f_path = "\\Звуки ogg\\"+str("%010d" %offset)+" "+str(tip)+".ogg"

            elif tip == 10: # Это не файл скорей данные записанные в таблицу файлов
                pass

            elif tip == 11 and fd == b'OggS': # Видео формата ogg
                f.seek(offset+58)
                fd = f.read(4) # Проверочные байты
                f.seek(posf0) # Возврат назад
                if fd == b'OggS': # Это для Братьев пилотов просто голоса персонажей
                    f_path = "\\Звуки ogg\\"+str("%010d" %offset)+" "+str(tip)+".ogg"
                else:
                    f_path = "\\Видео ogg\\"+str("%010d" %offset)+" "+str(tip)+".avi"

            elif tip == 12 and fd == b'OggS': # ogg Музыка
                f_path = "\\Музыка ogg\\"+str("%010d" %offset)+" "+str(tip)+".ogg"

            elif tip == 1: # Текст
                f_path = "\\Txt\\"+str("%010d" %offset)+" "+str(tip)+".txt"

            else:
                f_path = str("%010d" %offset)+"."+str(tip)

            if tip != 10: # Пропускаем мибо данные с типом 10
                format = f_path.split(".")[-1].lower()
                self.data.append((f_path, offset, size, format))

            else:
                #print("   Ошибки Тип",tip,"Оффсет размер",offset,size)
                pass
        self.file = f

    def Unpack_OGG(self, f):
        self.sound = f

    def Unpack_PNG(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_TXT(self, f): 
        self.text = f.read().split(b"\x00")[0].decode("cp1251")