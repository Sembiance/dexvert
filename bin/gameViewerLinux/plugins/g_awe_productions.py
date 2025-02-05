#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Антон Горев

# Agatha Christie And Then There Were None (Агата Кристи: И никого не стало) [BMP, ICO, TGA, ACA, BAK, ACG, PSD, ACV, MP3, ACT]
# Spongebob Squarepants Lights, Camera, PANTS! (Губка Боб "Свет, камера, штаны") [BMP, TGA, ICO, GIF, JPG, SBA, SBG, SBV, CSS, TXT]
# SpongeBob SquarePants: The Movie [BMP, ICO, SBA, SBG, SBV]
# Bratz: Rock Angelz [ICO, RAA, RAG, RAV]

import os, sys, io, struct
from PIL import Image
import numpy as np
import io

NAME = "AWE Productions"
TYPES_FILES = [('bmp Images', ('*.bmp')),('ico Images', ('*.ico')),('tga Images', ('*.tga')),('aca Images', ('*.aca')),('bak Images', ('*.bak')),('acg Images', ('*.acg')),('psd Images', ('*.psd')),('acv Sound', ('*.acv')),('mp3 Sound', ('*.mp3')),('gif Images', ('*.gif')),('jpg Images', ('*.jpg')),('sbg Images', ('*.sbg')),('sbv Sound', ('*.sbv')),('css Text', ('*.css')),('txt Text', ('*.txt')),('raa Images', ('*.raa')),('rag Images', ('*.rag')),('rav Sound', ('*.rav')),('act Text', ('*.act'))]
FORMATS_FILES = ["bmp","ico","tga","aca","bak","acg","psd","acv","mp3","gif","jpg","sba","sbg","sbv","css","txt","raa","rag","rav","act"]
GAMES = ["Agatha Christie: And Then There Were None",
         "Spongebob Squarepants Lights, Camera, PANTS!",
         "SpongeBob SquarePants: The Movie",
         "Bratz: Rock Angelz"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res:
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        self.sup_formats = ["bmp",
                            "ico",
                            "tga",
                            "aca",
                            "bak",
                            "acg",
                            "psd",
                            "acv",
                            "mp3",
                            "gif",
                            "jpg",
                            "sba",
                            "sbg",
                            "sbv",
                            "css",
                            "txt",
                            "raa",
                            "rag",
                            "rav",
                            "act"]

        self.sup_types = {"bmp":1,
                          "ico":1,
                          "tga":1,
                          "aca":1,
                          "bak":1,
                          "acg":1,
                          "psd":1,
                          "acv":3,
                          "mp3":3,
                          "gif":1,
                          "jpg":1,
                          "sba":1,
                          "sbg":1,
                          "sbv":3,
                          "css":4,
                          "txt":4,
                          "raa":1,
                          "rag":1,
                          "rav":3,
                          "act":4}
        self.images = []
        self.sound = None
        self.text = None

    def open_files(self,files):
        self.data = files

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        size = data_res[2]
        format = data_res[3]
        self.text = None
        f = open(name,"rb")
        f2 = io.BytesIO(f.read(size))
        f.close()

        if format in ["bmp", "ico", "tga", "aca", "bak", "acg", "psd", "gif", "jpg","sba","sbg","raa","rag"]:
            self.Unpack_BMP(f2)
        elif format in ["acv","mp3","sbv","rav"]:
            self.Unpack_WAV(f2)
        elif format in ["css", "txt"]:
            self.Unpack_TXT(f2)
        elif format in ["act"]:
            self.Unpack_act(f2)

    def Unpack_BMP(self, f):
        try: # Исключения
            image = Image.open(f)
            self.images = [image]
        except :
            print("Не поддерживается")

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_TXT(self, f): 
        self.text = f.read().decode("cp1251")

    def Unpack_act(self, f):
        f3 = io.BytesIO()
        strings = struct.unpack("<H",f.read(2))[0]

        for i in range(strings):
            stringlen = struct.unpack("<H",f.read(2))[0]
            for j in range(stringlen):
                fd = struct.unpack("B",f.read(1))[0]
                if (fd % 0x40) <= 0xF:
                    decoded = struct.pack("B",fd + 0x30)
                elif (fd % 0x40) <= 0x1F:
                    decoded = struct.pack("B",fd + 0x10)
                elif (fd % 0x40) <= 0x2F:
                    decoded = struct.pack("B",fd - 0x10)
                elif (fd % 0x40) <= 0x3F:
                    decoded = struct.pack("B",fd - 0x30)
                f3.write(decoded)

        f3.seek(0)
        self.text = f3.read().decode("cp1251")
        f3.close()
