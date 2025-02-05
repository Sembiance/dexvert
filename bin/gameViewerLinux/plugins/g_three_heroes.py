#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Три богатыря или очень страшная сказка
# kalumb1@ya.ru

import os, sys
import struct
import io
from PIL import Image

NAME = "Три богатыря или очень страшная сказка"
FORMATS_ARCHIVE = ['dat']
TYPES_ARCHIVE = [('DAT Game Pack', ('*.dat'))]
AUTHOR = "Alex kalumb1@ya.ru"
GAMES = ["Три богатыря или очень страшная сказка"]

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] # (имя файла, оффсет, размер, формат)
        self.app = app

        self.sup_formats = ["jpg",
                            "tga",
                            "mp3",
                            "raw",
                            "amb",
                            "ani",
                            "obj",
                            "spr",
                            "lst",
                            "hom"]
        self.sup_types = {"jpg":1,
                          "tga":1,
                          "mp3":3,
                          "raw":3,
                          "amb":4,
                          "ani":4,
                          "obj":4,
                          "spr":4,
                          "lst":4,
                          "hom":4}
                      
        self.images = []
        self.sound = None
        self.text = None
        
    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "dat":
           self.OpenArchiveDAT(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        self.text = None
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        code = data_res[4]
        self.file.seek(offset)
        if format == "jpg" or format == "tga":
            self.Unpack_JPG_TGA(self.decode_res(self.file.read(size),name,code))
        if format == "mp3":
            self.Unpack_MP3(self.decode_res(self.file.read(size),name,code))
        if format == "raw":
            self.Unpack_RAW(self.decode_res(self.file.read(size),name,code))
        if format in ["amb","hom"]:
            self.Unpack_AMB(self.decode_res(self.file.read(size),name,code))
        if format in ["ani","obj","spr","lst"]:
            self.Unpack_ANI_OBJ(self.decode_res(self.file.read(size),name,code))
            
    def decode_res(self, bytes_res, name, code):
        if code == 1:
            decode = bytearray(bytes_res)
            v1 = ord(name[0])
            for i in range(len(bytes_res)):
                decode[i] ^= v1
                v1 = (v1 + 27) & 0xff
            return io.BytesIO(decode)
        else:
            return io.BytesIO(bytes_res)
        
    
    def OpenArchiveDAT(self,file):
        self.data = [] # Список файлов
        
        f = open(file,"rb")
        
        if f.read(4) != b"FPAK":
            raise Exception("Это не архив!")
        
        col_files = struct.unpack("<I",f.read(4))[0] # Количество файлов
        code = f.read(4)
        
        for k in range(col_files):
            decode = bytearray(f.read(22))
            
            v9 = 85
            v11 = 22
            n = 0

            while True:
                decode[n] ^= v9
                n = n+1
                
                v9 = (v9 + 33) & 0xff
                v11 -= 1
                if v11 == 0:
                    break
            
            filename = decode[:14].split(b"\x00")[0].decode("cp1251")
            format = filename.split(".")[-1].lower()
            offset = struct.unpack("<I",decode[14:18])[0]
            size = struct.unpack("<I",decode[18:])[0]
            if code == b"code":
                self.data.append((filename,offset,size,format,1))
            else:
                self.data.append((filename,offset,size,format,0))
        self.file = f
        
    def Unpack_MP3(self, f): 
        self.sound = f
        
    def Unpack_JPG_TGA(self, f):
        self.images = [Image.open(f)]
        
        
        
    def Unpack_RAW(self,f):
        wav = b""
        size = f.getbuffer().nbytes
        try:
            wav += b"RIFF"
            wav += struct.pack("<I", size+44-8)# chunkSize размер файла-8
            wav += b"WAVE" # format WAVE
            wav += b"fmt " # subchunk1Id fmt 0x666d7420
            
            subchunk1Size = 16 #p
            audioFormat = 1 #p
            numChannels = 1
            sampleRate = 22050
            byteRate = 44100
            blockAlign = 2
            bitsPerSample = 16

            wav += struct.pack("<IHHIIHH", subchunk1Size, audioFormat, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample)
            wav += b"data"
            wav += struct.pack("<I", size)
            wav += f.read() # Данные
        finally:
            self.sound = io.BytesIO(wav)
            
    def Unpack_AMB(self, f): 
        self.text = f.read().decode("utf8")
            
    def Unpack_ANI_OBJ(self, f): 
        self.text = f.read().decode("cp1251")
            
            