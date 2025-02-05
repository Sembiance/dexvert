#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Tonny
# Alex kalumb1@ya.ru

# https://github.com/scummvm/scummvm-tools/blob/master/engines/tony/


import os, sys, io, struct
from PIL import Image
import numpy as np
import lzo

NAME = "Tonny"
FORMATS_ARCHIVE = ['mpr','vdb']
TYPES_ARCHIVE = [('Tonny Pack', ('*.mpr','*.vdb'))]
GAMES = ["Tony Tough and the Night of Roasted Moths"]
AUTHOR = "Alex kalumb1@ya.ru"

class Game_Res:
    def __init__(self,api):
        self.file = None
        self.data = []
        self.api = api
        
        self.sup_formats = ["loc","wav"]
        self.sup_types = {"loc":1,
                          "wav":3
        }
        self.images = []
        self.sound = None


    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "vdb":
            self.OpenArchiveVDB(file)
        elif format == "mpr":
            self.OpenArchiveMPR(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None
        
        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        
        head = self.file.read(4)
        if head != b"RESD":
            raise Exception("Неверный заголовок!")
        nSizeDecomp, nSizeComp = struct.unpack("<II",self.file.read(8))
        buff = self.file.read(nSizeComp)
        buff = lzo.decompress(buff, False, nSizeDecomp)
        
        if format == "wav":
            self.Unpack_WAV(io.BytesIO(buff))
        elif format == "loc":
            self.Unpack_LOC(io.BytesIO(buff))
            
    
    def OpenArchiveVDB(self,file):

        f = open(file,"rb")
        f.seek(-8, 2)
        num, head = struct.unpack("<II",f.read(8))
        f.seek(-8 - 12 * num, 2)
        
        for i in range(num):
            offset, code, parts = struct.unpack("3I",f.read(12))
            offset_old = f.tell()
            f.seek(offset)
            for j in range(parts):
                offset = f.tell()
                size, rate = struct.unpack("<II",f.read(8))
                filename = "Sound_{}_{}.wav".format(i+1, j+1)
                self.data.append((filename,offset,size+8,"wav"))
                f.seek(size,1)
            f.seek(offset_old)
        
        self.file = f
        
    def OpenArchiveMPR(self,file):
        # MPC
        
        p,f = os.path.split(file)
        a = p+"\\"+f[:-3]+"MPC"
        if not os.path.exists(a):
            raise Exception("Файл {} не найден".format(a))
            
        f = open(a,"rb")

        head = f.read(5)
        if head[:-1] != b"MPC\x20":
            raise Exception("Неверный заголовок")

        dwSizeDecomp = struct.unpack("<I",f.read(4))[0]
        
        if head[4]:
            dwSizeComp = struct.unpack("<I",f.read(4))[0]
            buff = f.read(dwSizeComp)
            buff = lzo.decompress(buff, False, dwSizeDecomp)
        else:
            buff = f.read(dwSizeComp)
        f.close()
        
        n = buff.find(b"\x08Location")
        buff = buff[n-2:]
        
        f = io.BytesIO(buff)
        n_res = []
        num = struct.unpack("<H",f.read(2))[0]
        for i in range(num):
            l = struct.unpack("B",f.read(1))[0]
            f.seek(l, 1)
            f.seek(8, 1)
            r = struct.unpack("I",f.read(4))[0]
            n_res.append(r)
    
        
        # MPR

        f = open(file,"rb")
        f.seek(-12, 2)
        dwSizeComp, nResources = struct.unpack("<II",f.read(8))
        head = f.read(4)
        if head != b"END0":
            raise Exception("Это не архив!")
        
        f.seek(-(12 + dwSizeComp), 2)
        
        buff = f.read(dwSizeComp)
        buff = lzo.decompress(buff, False, nResources*8)
        table = struct.unpack("<{}I".format(nResources*2), buff)
        
        for i in range(nResources):
            format = "dat"
            
            code = table[i * 2]
            offset = table[i * 2 + 1]
            f.seek(offset)
            head = f.read(4)
            if head != b"RESD":
                raise Exception("Неверный заголовок!")
            nSizeDecomp, size = struct.unpack("<II",f.read(8))
            if code in n_res:
                format = "loc"
            
            filename = "File_{}.{}".format(i+1, format)
            self.data.append((filename,offset,size,format))
        self.file = f

    def Unpack_WAV(self, f):
    
        def SaveWAV(outBuffer, rate):
            size = len(outBuffer)*2
            wav = b""
            try:
                wav += b"RIFF"
                wav += struct.pack("<I", size+44-8)# chunkSize размер файла-8
                wav += b"WAVE" # format WAVE
                wav += b"fmt " # subchunk1Id fmt 0x666d7420
                
                subchunk1Size = 16
                audioFormat = 1
                numChannels = 1
                sampleRate = rate #22050
                byteRate = 44100
                blockAlign = 2
                bitsPerSample = 16

                wav += struct.pack("<IHHIIHH", subchunk1Size, audioFormat, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample)
                wav += b"data"
                wav += struct.pack("<I", size)
                f1 = io.BytesIO()
                f1.write(wav)
                for b in outBuffer:
                    f1.write(struct.pack("h",b))
            finally:
                return f1

        class Struct:
            def __init__ (self, *argv, **argd):
                if len(argd):
                    # Update by dictionary
                    self.__dict__.update (argd)
                else:
                    # Update by position
                    attrs = filter (lambda x: x[0:2] != "__", dir(self))
                    for n in range(len(argv)):
                        setattr(self, attrs[n], argv[n])
            
        class imach (Struct):
            last = 0
            stepIndex = 0

        class ADPCMStatus (Struct):
            ima_ch = [imach(), imach()]
            
        stepAdjustTable = [
            -1, -1, -1, -1, 2, 4, 6, 8,
            -1, -1, -1, -1, 2, 4, 6, 8
        ]
            
            
        imaTable = [
            7,    8,    9,   10,   11,   12,   13,   14,
            16,   17,   19,   21,   23,   25,   28,   31,
            34,   37,   41,   45,   50,   55,   60,   66,
            73,   80,   88,   97,  107,  118,  130,  143,
            157,  173,  190,  209,  230,  253,  279,  307,
            337,  371,  408,  449,  494,  544,  598,  658,
            724,  796,  876,  963, 1060, 1166, 1282, 1411,
            1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024,
            3327, 3660, 4026, 4428, 4871, 5358, 5894, 6484,
            7132, 7845, 8630, 9493,10442,11487,12635,13899,
            15289,16818,18500,20350,22385,24623,27086,29794,
            32767
        ]

        def CLIP (v, amin, amax):
            if (v < amin):
                return amin
            elif (v > amax):
                return amax
            else:
                return v

        def decodeIMA(code, channel, status):
            E = int((2 * (code & 0x7) + 1) * imaTable[status.ima_ch[channel].stepIndex] / 8)
            diff = int(-E if (code & 0x08) else E)
            samp = int(CLIP(status.ima_ch[channel].last + diff, -32768, 32767))
            
            status.ima_ch[channel].last = int(samp)
            status.ima_ch[channel].stepIndex += int(stepAdjustTable[code])
            status.ima_ch[channel].stepIndex = int(CLIP(status.ima_ch[channel].stepIndex, 0, 88))

            return samp
    
    
        sampleSize = struct.unpack("<I",f.read(4))[0]
        rate = struct.unpack("<I",f.read(4))[0]
        inBuffer = bytearray(f.read(sampleSize))
        uncompressedSize = sampleSize * 2;
        outBuffer = [0 for k in range(uncompressedSize)]
        
        # Decode
        decodedSamples = [0,0]
        decodedSampleCount = 0

        status = ADPCMStatus()
        status.ima_ch[0] = imach()
        status.ima_ch[1] = imach()
        
        for samples in range(uncompressedSize):
            if decodedSampleCount == 0:
                data = inBuffer[samples >> 1]
                decodedSamples[0] = decodeIMA((data >> 4) & 0x0f, 0, status)
                decodedSamples[1] = decodeIMA((data >> 0) & 0x0f, 0, status) # 1 channel, hardcoded
                decodedSampleCount = 2
            outBuffer[samples] = decodedSamples[1 - (decodedSampleCount - 1)]
            decodedSampleCount -= 1

        f = SaveWAV(outBuffer, rate)

        self.sound = f
        
        
    def Unpack_LOC(self, f):
    
        def Color(p):
            r = ((p >> 10) & 0x1F) << 3
            g = ((p >> 5) & 0x1F) << 3
            b = ((p & 0x1F) << 3)
            return (r,g,b)
    
        head = f.read(3)
        if head != b"LOX":
            raise Exception("Неверный заголовок LOX!")
        f.seek(1, 1)
        l = struct.unpack("B",f.read(1))[0]
        f.seek(l, 1)
        f.seek(12, 1)
        w, h = struct.unpack("<II",f.read(8))
        
        rgb = np.frombuffer(f.read(w*h*2), dtype=np.uint16)
        rgb = np.array(rgb, np.uint16).reshape(h, w)
        r,g,b = Color(rgb)
        rgb = np.dstack((r,g,b))
        rgb = np.uint8(rgb)
        
        self.images.append(Image.fromarray(rgb,"RGB"))
    