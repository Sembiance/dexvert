#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Десять негритят
# Стрелки и Разводы(Train Empire)
# Кто самый умный ?
# В гостях у розовой зебры
# Розовая Зебра Приключения начинаются

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Comulti Multimedia" 
FORMATS_ARCHIVE = ['vfs', 'pak', 'txt']
TYPES_ARCHIVE = [('Comulti Multimedia', ('*.vfs', '*.pak', '*.txt'))]
GAMES = ["Десять негритят",
         "Стрелки и Разводы",
         "Кто самый умный ?",
         "В гостях у розовой зебры",
         "Розовая Зебра Приключения начинаются"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["bmp",
                            "psd",
                            "gif",
                            "jpg",
                            "tga",
                            "ogg",
                            "wav",
                            "txt",
                            "log",
                            "ini",
                            "ion",
                            "css",
                            "htm",
                            "html",
                            "sha",
                            "def",
                            "isc",
                            "sfd",
                            "tok"]

        self.sup_types = {"bmp":1,
                          "psd":1,
                          "gif":1,
                          "jpg":1,
                          "tga":1,
                          "ogg":3,
                          "wav":3,
                          "txt":4,
                          "log":4,
                          "ini":4,
                          "ion":4,
                          "css":4,
                          "htm":4,
                          "html":4,
                          "sha":4,
                          "def":4,
                          "isc":4,
                          "sfd":4,
                          "tok":4}

        self.images = []  
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "vfs" or format == "pak":
            self.OpenArchiveVFS(file)
        elif format == "txt":
           self.OpenArchiveTXT(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format in ["bmp","psd","gif","jpg","tga"]:
            self.Unpack_BMP(io.BytesIO(self.file.read(size)),data_res[4])
        elif format == "wav" or format == "ogg":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)),data_res[4])
        elif format in ["txt","log","ini","ion","css","htm","html","sha","def","isc","sfd","tok"]:
            self.Unpack_TXT(io.BytesIO(self.file.read(size)),data_res[4])

    def OpenArchiveVFS(self,file):
        self.data = []

        f = open(file,"rb")
        data3 = [] # Оффсеты размер файлов
        type = f.read(4) # Тип архива
        if type != b'pack': # Проверка на архив
            print("ЭТО НЕ АРХИВ",type)
            return(0)

        unclear_1 = struct.unpack("<I",f.read(4))[0] # Непонятно
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        size_tab = struct.unpack("<I",f.read(4))[0] # Размер таблицы с именами
        size_bin_1 = struct.unpack("<I",f.read(4))[0] # Длина архива без таблицы файлов
        unclear_2 = struct.unpack("<I",f.read(4))[0]  # Непонятно
        size_bin_2 = struct.unpack("<I",f.read(4))[0] # Длина заголовока до таблицы имён файлов
        size_bin_3 = struct.unpack("<I",f.read(4))[0] # Начало файлов в архиве

        for i in range(col):
            unclear_3 = struct.unpack("<I",f.read(4))[0] # Непонятно
            size = struct.unpack("<I",f.read(4))[0]   # Размер
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет
            data3.append((offset,size,unclear_3))
            #print(unclear_3,size,offset)

        data3.sort(key=lambda i: i[2]) # Чтоб правельно расчитать имена файлов

        for i in range(col):
            f_path = b'' # Читаем имя файла до байта 00
            while True: 
                bait = f.read(1) # Байт строчки
                if bait == b'\x00':
                    f_path = f_path.decode("cp1251").replace("\\\\","\\") # Переделаваем байты в строчку
                    format = f_path.split(".")[-1].lower()
                    self.data.append((f_path,data3[i][0],data3[i][1],format,0))
                    break
                f_path += bait # Прибавляем байт
        self.file = f

    def OpenArchiveTXT(self,file):
        data = [] # Список путей
        f = open(file,"rb")
        size_tab = struct.unpack("<I",f.read(4))[0] # Размер таблицы
        fd = f.read(size_tab-4)
        f2 = io.BytesIO(fd)

        while True:
            if f2.tell() == size_tab-4:
                break
            length = struct.unpack("B",f2.read(1))[0] # Длина дальше данных
            byte = f2.read(length) # Имя файла зашифровано
            fd = bytearray(byte)
            for i in range(len(fd)):
                if fd[i] >= 27: # Байт 1b
                    fd[i] = fd[i] - 0x1b

                elif fd[i] <= 26: # Байт
                    fd[i] = (256+fd[i]) - 0x1b
            f_path = fd.decode("utf8")

            offset = struct.unpack("<I",f2.read(4))[0]+size_tab # Оффсет
            size = struct.unpack("<I",f2.read(4))[0] # Размер

            if f_path[-1:] == "\\": # Путь
                #print("    Это путь к файлу",f_path,offset-size_tab,"Внутри файлов",size)
                data.append((f_path,offset,size))
                # Тут offset обозначает сколько в папке папок, size обозначает сколько в папке файлов
            else: # Файл
                #print(f_path,"   ",offset,size)

                #################################### Создания пути
                path_folder = ""
                for i in data:
                    path_folder += i[0]
                #print(path_folder+f_path,offset,size)
                format = f_path.split(".")[-1].lower()
                self.data.append((path_folder+"\\"+f_path,offset,size,format,1))
                #####################################

                path_folder, col_folder, col_file = data[len(data)-1] # Последняя папка
                #print("Входим для проверки",path_folder, col_folder, col_file)
                #print("Все пути",data,len(data),len(data)-1)
                del data[len(data)-1] # Удаляем последнию папку
                col_file -= 1
                if col_file == 0: # Удаляем последнию папку
                    #print("    Удалили",path_folder, col_folder, col_file)
                    pass
                else:
                    data.append((path_folder, col_folder, col_file))
                    #print("Добавили путь  ",path_folder, col_folder, col_file)
        self.file = f

    def Unpack_WAV(self, f, tip):
        if tip == 0:
            pass
        elif tip == 1:
            f = self.Explanation(f)
        self.sound = f

    def Unpack_BMP(self, f, tip):
        if tip == 0:
            pass
        elif tip == 1: # 1 Значит зашифрован
            f = self.Explanation(f)
        self.images = [Image.open(f)]

    def Unpack_TXT(self, f, tip):
        if tip == 0:
            pass
        elif tip == 1:
            f = self.Explanation(f)
        try: # Исключения если не текстовый файл попадётся а архив txt
            self.text = f.read().decode("cp1251")
        except :
            pass

    def Explanation(self, f): # Расшифровка
        fd = f.read()
        fd = bytearray(fd)
        for i2 in range(len(fd)):
            if fd[i2] >= 27: # Байт 1b
                fd[i2] = fd[i2] - 0x1b

            elif fd[i2] <= 26: # Байт
                fd[i2] = (256+fd[i2]) - 0x1b
        f2 = io.BytesIO(fd)
        return(f2)
