#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Neighbours from Hell
# Как достать соседа

import io, struct
import zipfile
from PIL import Image
import numpy as np

NAME = "Neighbours from Hell"
FORMATS_ARCHIVE = ['bnd']
TYPES_ARCHIVE = [('Neighbours Pack', ('*.bnd'))]
AUTHOR = "Alex kalumb1@ya.ru"

GAMES = ["Neighbours from Hell",
         "Neighbours from Hell 2: On Vacation"
]

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] # (имя файла, оффсет, размер, формат, [имя в архиве])
        self.app = app
        self.sup_formats = ["tga",
                            "wav",
                            "mp3",
                            "xml"]
        self.sup_types = {"tga":1,
                          "wav":3,
                          "mp3":3,
                          "xml":4}
        self.images = []
        self.sound = None
            
    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "bnd":
            self.OpenArchiveBND(file)
            
    def OpenArchiveBND(self,file):
        self.data = []
        
        if not zipfile.is_zipfile(file):
            raise("Это не архив!")
        
        self.file = zipfile.ZipFile(file)
        for name in self.file.namelist():
            unicode_name = name.encode('cp437').decode('cp1251')
            format = unicode_name.split(".")[-1].lower()
            offset = 0
            size = self.file.getinfo(name).file_size
            if unicode_name[-1] != "/":
                self.data.append((unicode_name,offset,size,format,name))

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        name_size = data_res[4] # в EXE это индекс
        
        if format == "tga":
            self.Unpack_TGA(io.BytesIO(self.file.read(name_size)))
        elif format == "wav" or format == "mp3":
            self.Unpack_WAV_MP3(io.BytesIO(self.file.read(name_size)))
        elif format == "xml":
            self.Unpack_XML(io.BytesIO(self.file.read(name_size)))
        
    def Unpack_WAV_MP3(self, f):
        self.sound = f
        
    def Unpack_XML(self,f):
        text = f.read()
        if text[:2] == b"\xff\xfe":
            self.text = text[2:].decode("utf_16_le")
        elif text[:2] == b"\xfe\xff":
            self.text = text[2:].decode("utf_16_be")
        else:
            self.text = text.decode("cp1251")
        
    def Unpack_TGA(self, f):
        
        def Color(pixel):
            b = (pixel & 15) * 17
            g = ((pixel>>4) & 15) * 17
            r = ((pixel>>8) & 15) * 17
            a = ((pixel>>12) & 15) * 17
            return (r,g,b,a)
        
        f.seek(0xc)
        w,h = struct.unpack("HH",f.read(4))
        b,s = struct.unpack("BB",f.read(2))
        
        if s == 0 and b == 24:
            self.images = [Image.open(f)]
            return 1
        
        if s & 0b1111 == 0:
            if b == 16:
                im = Image.frombuffer('RGB', (w,h), f.read(w*h*2), 'raw', 'BGR;16', 0, 1)
            elif b == 24:
                im = Image.frombuffer('RGB', (w,h), f.read(w*h*3), 'raw', 'RGB', 0, 1)
        else:
            if b == 16:
                rgb = np.frombuffer(f.read(w*h*2), dtype=np.uint16)
                rgb = np.array(rgb, np.uint16).reshape(h, w)
                r,g,b,a = Color(rgb)
                rgb = np.dstack((r,g,b,a))
                rgb = np.uint8(rgb)
                
                im = Image.fromarray(rgb,"RGBA")
        self.images = [im]
        
        