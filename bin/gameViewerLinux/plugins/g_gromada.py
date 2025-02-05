#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Громада

import os, sys, io, struct
from PIL import Image

NAME = "Громада"
FORMATS_ARCHIVE = ['res']
TYPES_ARCHIVE = [('Громада', ('*.res'))]
GAMES = ["Громада"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = []
        self.app = app
        
        self.sup_formats = ["wav",
                            "pic"]

        self.sup_types = {"wav":3,
                          "pic":2}
        self.images = []
        self.sound = None

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
        if format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))
        elif format == "pic":
            self.Unpack_PIC(io.BytesIO(self.file.read(size)))

    def OpenArchiveRES(self,file):
        self.data = []
        f = open(file,"rb")

        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        for i in range(col):
            tip = f.read(1)[0] # Тип файла
            size = struct.unpack("<I",f.read(4))[0] # Размер
            offset = f.tell()
            f.seek(size,1) # Отступить на байт от нынешний позиции

            if tip == 33: # Сжатая картинка
                f.seek(offset+6)
                f_path2 = f.read(34).split(b"\x00")[0].decode("cp866") # Внутренние описание файла
                #print(f_path2)

                table = str.maketrans("", "", "\/:*?<>|") # Не допустимые символы
                f_path2 = f_path2.translate(table) # Удаляет не допустимые символы из текста f_path2
                f.seek(offset+size)
                self.data.append((f_path2+" "+str("%08d" %offset)+".pic",offset,size,"pic"))

            elif tip == 34: # Архив со звуками
                self.data.append((str("%08d" %offset)+".ArcWav",offset,size,"ArcWav"))

                f.seek(offset)
                col2 = struct.unpack("<H",f.read(2))[0] # Количество файлов звуков
                unclear = struct.unpack("<I",f.read(4))[0] # Непонятно
                #print("Количество звуков, непонятно",col2,unclear,"\n")
                for i in range(col2):
                    unclear2 = f.read(1)[0] # Непонятно
                    size2 = struct.unpack("<I",f.read(4))[0] # Размер
                    offset2 = f.tell()
                    f.seek(size2,1) # Отступить на байт от нынешний позиции
                    #print("Звук Оффсет, Непонятно, Размер",offset2,unclear2,size2)
                    self.data.append((str("%08d" %offset2)+".wav",offset2,size2,"wav"))

            elif tip == 35: # Непонятная таблица
                self.data.append((str("%08d" %offset)+".tab1",offset,size,"tab1"))

            elif tip == 37: # Непонятная таблица
                self.data.append((str("%08d" %offset)+".tab2",offset,size,"tab2"))

            else: # Непонятно
                self.data.append((str("%08d" %offset)+".bin",offset,size,"bin"))
        self.file = f

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_PIC(self, f): 
        data2 = [] # Список оффсетов и размеров картинок для повторения кадра
        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)
        unclear = struct.unpack("<H",f.read(2))[0] # Непонятно
        unclear_2 = struct.unpack("<I",f.read(4))[0] # Непонятно
        f_path = f.read(34).split(b"\x00")[0].decode("cp866") # Внутренние описание файла
        #print(f_path)

        if end_f == 273:
            print("В файле нет картинки.")
            
        else:
            f.seek(269)
            size = struct.unpack("<I",f.read(4))[0] # Размер файла до конца файла от следуюшего байта
            tip = f.read(1)[0] # Тип распаковки
            unclear = struct.unpack("<H",f.read(2))[0] # Непонятно
            col_frame = struct.unpack("<H",f.read(2))[0] # Количество сжатых файлов
            size0 = struct.unpack("<I",f.read(4))[0] # Размер файла до конца файла отщёт надо пропустить ширину и высоту картинки тогда отшитывать
            w, h = struct.unpack("<HH",f.read(4)) # Ширина и высота
            #print("Ширина и высота картинки",w, h)
            #print("Тип распаковки картинки",tip,"Непонятно",unclear)
            #print("Количество файлов",col_frame)

            Pal = f.read(768) # Палитра

            if tip == 4: # Тип 4 Для создания рандомной палитры, чтоб было видно картинки
                #Pal = b''
                #for i in range(768):
                    #Pal += struct.pack("B", random.randrange(0, 255)) # - возвращает случайно выбранное число из последовательности.
                """
                for i in range(256):
                    #Pal += struct.pack("BBB", i,i,i)
                    dss = 255-i
                    Pal += struct.pack("BBB", dss,dss,dss)
                """
                pass

            ss = 0 # Счётчик кадров
            while True:
                posf = f.tell()
                if posf == end_f:
                    #print("\nКонец файла ##########################################################\n")
                    break
                ss += 1

                size = struct.unpack("<I",f.read(4))[0] # Размер файла
                offset = f.tell()
                data2.append((offset,size)) # Добавляем для повторного чтения кадров
                fd = f.read(size)
                #print("\nНачало файла, размер файла",posf,size,"Номер файла",ss)

                f2 = io.BytesIO(fd)
                frame_repeated = struct.unpack("<H",f2.read(2))[0] # Номер кадра который надо повторить
                # В начале сжатия стоят 2 байта FF FF если размер сжатого файла равен 2 то в этих байтах будет номер кадра который надо повторить, если размер не равен 2 то тогда всегда стоит FF FF.

                if tip != 6: # Тип не равен 16 битной картинки, заполняем пустой файл нулями
                    f3 = io.BytesIO(b'\x00' *(w*h)) # Генерируем пустую картинку забитаю нулями

                # Распаковка данных по ширине картинки
                if size == 2: # Если размер файла равен 2 байтам то это Повтор кадра
                    #print("Номер кадра который надо повторить",frame_repeated,"Сейчас мы на кадре",ss)
                    posf2 = f.tell() # Для возврата

                    offset2, size2 = data2[frame_repeated] # Читаем оффсет и размер файла кадра который надо повторить

                    if size2 == 2:
                        print("ОШИБКА РАЗМЕР КАДРА КОТОРЫЙ ПОВТОРИТЬ РАВЕН 2 БАЙТАМ")
                        break

                    f.seek(offset2) # Преход на чтнение нужного кадра
                    fd2 = f.read(size2)
                    f2.close() # Закрытие файла с 2 байтами
                    f2 = io.BytesIO(fd2) # Для распаковки

                    f2.read(2) # Номер кадра который надо повторить. Сейчас это ненужно
                    if tip == 0: # Распаковка тип 0 Всего 22 файла
                        self.Unpack_type_0(f2,f3,size2,w,h,Pal)

                    elif tip == 2: # Распаковка тип 2 Всего 173 файла
                        self.Unpack_type_2(f2,f3,size2,w,h,Pal)

                    elif tip == 3: # Распаковка тип 3 Всего 7 файла
                        self.Unpack_type_3(f2,f3,size2,w,h,Pal)

                    elif tip == 4: # Распаковка тип 4 Всего 17 файла
                        self.Unpack_type_4(f2,f3,size2,w,h,Pal)

                    # Тип 6, 7 нет повторных кадров.

                    elif tip == 8: # Распаковка тип 8 Всего 43 файла
                        self.Unpack_type_8(f2,f3,size2,w,h,Pal)

                    f.seek(posf2) # Возврат
                    ###########################

                elif tip == 0: # Распаковка тип 0 Всего 22 файла
                    self.Unpack_type_0(f2,f3,size,w,h,Pal)

                elif tip == 2: # Распаковка тип 2 Всего 173 файла
                    self.Unpack_type_2(f2,f3,size,w,h,Pal)

                elif tip == 3: # Распаковка тип 3 Всего 7 файла
                    self.Unpack_type_3(f2,f3,size,w,h,Pal)

                elif tip == 4: # Распаковка тип 4 Всего 17 файла
                    self.Unpack_type_4(f2,f3,size,w,h,Pal)

                elif tip == 6: # Распаковка тип 6 Распаковка 16 битных картинок Всего 3 файла
                    self.Unpack_type_6(f2,size,w,h)

                elif tip == 7: # Распаковка тип 7 Всего 1 файла
                    self.Unpack_type_7(f2,f3,size,w,h,Pal)

                elif tip == 8: # Распаковка тип 8 Всего 43 файла
                    self.Unpack_type_8(f2,f3,size,w,h,Pal)

                else:
                    print("Ошибка НЕ ОПРЕДЕЛЁН ТИП РАСПАКОВКИ")
                    f2.close()
                    f3.close()
                    break
        f.close()
        
    def Unpack_type_0(self,f2,f3,size,w,h,Pal):
        #print("Не сжатые картинки")
        f_image = Image.frombuffer('P', (w,h), f2.read(w*h), 'raw', 'P', 0, 1) 
        f_image.putpalette(Pal)
        self.images.append(f_image)
        f3.close()
        f2.close()

    def Unpack_type_2(self,f2,f3,size,w,h,Pal):
        line_w = 0 # Строка на которой мы находимся
        skip_lines = struct.unpack("<H",f2.read(2))[0] # Сколько пропустить прозрачных строчек
        line_w += skip_lines # Для пропуска строчек в начале файла
        f3.seek(line_w*w) # Переход на новую строчку по высоте картинки
        number_lines = struct.unpack("<H",f2.read(2))[0] # Сколько прочетать строчек по ширине картинки с даными
        #print("Сколько пропустить прозрачных строчек",skip_lines,"Сколько прочетать строчек с даными",number_lines)

        while True:
            if f2.tell() == size:
                #print("Дошли до конца распаковки\n\n")
                break

            check = f2.read(1)[0] # Действие
            HEX = hex(check)[2:].rjust(2, '0')
            HEX = HEX.upper() # Преобразование строки к верхнему регистру
            #print("    Позиция чтения",f2.tell()-1,"что прочетали",check,"Байт",HEX)

            if check >= 0xC0: # Повторить следующий байт
                col = check - 0xC0
                fd = f2.read(1) # Повторить
                f3.write(fd* col)
                #print("Повторить цвет",col,"Байт",fd)

            elif check >= 0x80: # Сколько прочетать байтов цвета
                col = check - 0x80
                fd = f2.read(col) # Читаем цвет
                f3.write(fd)
                #print("Прочетать цветов",col)            

            elif check >= 0x40: # Отойти от левого края на байт
                col = check - 0x40
                f3.seek(col,1)
                #print("Отойти от левого края на байт",col,HEX)

            elif check >= 0x01: # Отойти от левого края на байт
                # Проверил работают комбинации от 0x01 до 0x3F
                #print("Отойти от левого края на байт",check,"Байт",HEX)
                f3.seek(check,1) # Отступить на байт от нынешний позиции

            elif check == 0:
                line_w += 1 # Закончили работу со строчкой
                f3.seek(line_w*w) # Переход на новую строчку по высоте картинки
                #print("Конец строчки Переход на новую",line_w*w,"Строчна номер",line_w)
                #print("##################################################")

        f3.seek(0,2) # Для расчёта Чтоб больше файла картинки не распаковалось
        posf3 = f3.tell() # Конец файла

        f3.seek(0)
        f_image = Image.frombuffer('P', (w,h), f3.read(w*h), 'raw', 'P', 0, 1) 
        f_image.putpalette(Pal)
        self.images.append(f_image)

        f3.close()
        f2.close()

        if w*h < posf3:
            print("   @@@@@@@@@@  Ошибка Распаковалось больше байт чем размер картинки на",posf3-w*h,"!!!!!!")

    def Unpack_type_3(self,f2,f3,size,w,h,Pal):
        line_w = 0 # Строка на которой мы находимся
        skip_lines = struct.unpack("<H",f2.read(2))[0] # Сколько пропустить прозрачных строчек
        line_w += skip_lines # Для пропуска строчек в начале файла
        f3.seek(line_w*w) # Переход на новую строчку по высоте картинки
        number_lines = struct.unpack("<H",f2.read(2))[0] # Сколько прочетать строчек по ширине картинки с даными
        #print("Сколько пропустить прозрачных строчек",skip_lines,"Сколько прочетать строчек с даными",number_lines)

        while True:
            if f2.tell() == size:
                #print("Дошли до конца распаковки\n\n")
                break

            check = f2.read(1)[0] # Действие
            HEX = hex(check)[2:].rjust(2, '0')
            HEX = HEX.upper() # Преобразование строки к верхнему регистру
            #print("    Позиция чтения",f2.tell()-1,"что прочетали",check,"Байт",HEX)

    # Номера цветов которые есть вовсех файлах палитр 12, 13, 14, 15, 16, 17, 18
    # Сновыми цветами картинки стали выглядить лучше

            if check >= 0xE0:
                col = check - 0xE0
                f3.write(b'\x18'*col)
                #print("E0 Прочетать цветов",col)

            elif check >= 0xC0:
                col = check - 0xC0
                f3.write(b'\x17'*col)
                #print("C0 Прочетать цветов",col)

            elif check >= 0xA0:
                col = check - 0xA0
                f3.write(b'\x16'*col)
                #print("A0 Прочетать цветов",col)

            elif check >= 0x80:
                col = check - 0x80
                f3.write(b'\x15'*col)
                #print("80 Прочетать цветов",col) 

            elif check >= 0x60:
                col = check - 0x60
                f3.write(b'\x14'*col)
                #print("60 Прочетать цветов",col)            

            elif check >= 0x40:
                col = check - 0x40
                f3.write(b'\x13'*col)
                #print("40 прочетали байтов цветов",col,)

            elif check >= 0x20:
                col = check - 0x20
                f3.write(b'\x12'*col)
                #print("20 прочетали байтов цветов",col)

            elif check >= 0x01: # Отойти от левого края на байт
                # Проверил работают комбинации от 0x01 до 0x3F
                #print("Отойти от левого края на байт",check,"Байт",HEX)
                f3.seek(check,1) # Отступить на байт от нынешний позиции

            elif check == 0:
                line_w += 1 # Закончили работу со строчкой
                f3.seek(line_w*w) # Переход на новую строчку по высоте картинки
                #print("Конец строчки Переход на новую",line_w*w,"Строчна номер",line_w)
                #print("##################################################")

            else:
                print("ОШИБКА НЕПОНЯТНЫЙ ТИП")
                break

        f3.seek(0,2) # Для расчёта Чтоб больше файла картинки не распаковалось
        posf3 = f3.tell() # Конец файла

        f3.seek(0)
        f_image = Image.frombuffer('P', (w,h), f3.read(w*h), 'raw', 'P', 0, 1) 
        f_image.putpalette(Pal)
        self.images.append(f_image)

        f3.close()
        f2.close()

        if w*h < posf3:
            print("   @@@@@@@@@@  Ошибка Распаковалось больше байт чем размер картинки на",posf3-w*h,"!!!!!!")

    def Unpack_type_4(self,f2,f3,size,w,h,Pal):
        line_w = 0 # Строка на которой мы находимся
        skip_lines = struct.unpack("<H",f2.read(2))[0] # Сколько пропустить прозрачных строчек
        line_w += skip_lines # Для пропуска строчек в начале файла
        f3.seek(line_w*w) # Переход на новую строчку по высоте картинки
        number_lines = struct.unpack("<H",f2.read(2))[0] # Сколько прочетать строчек по ширине картинки с даными
        #print("Сколько пропустить прозрачных строчек",skip_lines,"Сколько прочетать строчек с даными",number_lines)

        while True:
            if f2.tell() == size:
                #print("Дошли до конца распаковки\n")
                break

            check = f2.read(1)[0] # Действие
            fd = f2.read(1) # Читаем байт должен быть 00
            HEX = hex(check)[2:].rjust(2, '0')
            HEX = HEX.upper() # Преобразование строки к верхнему регистру
            #print("    Позиция чтения",f2.tell()-1,"что прочетали",check,"Байт",HEX)

            if check >= 0x80: # Сколько раз повторить байт цвета
                col = check - 0x80
                #fd = f2.read(1) # Читаем цвет
                f3.write(fd*col) # Повторить цвет
                #print("Повторить байт цвета",col)

            elif check >= 0x01: # Отойти от левого края на байт   от 0x01 до 0x7F
                #print("Отойти от левого края на байт",check,"Байт",HEX)
                f3.seek(check,1) # Отступить на байт от нынешний позиции

            elif check == 0: # 00 00
                line_w += 1 # Закончили работу со строчкой
                f3.seek(line_w*w) # Переход на новую строчку по высоте картинки
                #print("Конец строчки Переход на новую",line_w*w,"Строчна номер",line_w)
                #print("##################################################")

            else:
                print("ОШИБКА НЕПОНЯТНЫЙ ТИП")
                break

        f3.seek(0,2) # Для расчёта Чтоб больше файла картинки не распаковалось
        posf3 = f3.tell() # Конец файла

        f3.seek(0)
        f_image = Image.frombuffer('P', (w,h), f3.read(w*h), 'raw', 'P', 0, 1) 
        f_image.putpalette(Pal)
        self.images.append(f_image)

        f3.close()
        f2.close()

        if w*h < posf3:
            print("   @@@@@@@@@@  Ошибка Распаковалось больше байт чем размер картинки на",posf3-w*h,"!!!!!!")

    def Unpack_type_6(self,f2,size,w,h):
        f3 = io.BytesIO() # Распакованные данные
        while True:
            if f2.tell() == size: # Дошли до конца сжатого файла
                posf3 = f3.tell()
                #print("Конец сжатого файла",posf3)
                break

            check = f2.read(1)[0] # Действие
            #print("Действие",check,"позиция",f2.tell()-1)
            if check >= 0x80: # Повторить два следующих байта
                col = check - 0x80
                fd = f2.read(2) # Читаем цвет
                f3.write(fd*col)
                #print("Повторить 2 байта цвета",col)

            else:
                fd = f2.read(check*2)
                f3.write(fd)
                #print("Прочетать цветов",check)

        if (w*h)*2 != posf3: # Проверка на распаковку
            print("Ошибка неправельное количество байт распаковалось",(w*h)*2,posf3)

        f3.seek(0)
        f_image = Image.frombuffer('RGB', (w,h), f3.read(w*h*2), 'raw', 'BGR;15', 0, 1)
        self.images.append(f_image)
        f2.close()
        f3.close()

    def Unpack_type_7(self,f2,f3,size,w,h,Pal):
        line_w = 0 # Строка на которой мы находимся
        skip_lines = struct.unpack("<H",f2.read(2))[0] # Сколько пропустить прозрачных строчек
        line_w += skip_lines # Для пропуска строчек в начале файла
        f3.seek(line_w*w) # Переход на новую строчку по высоте картинки
        number_lines = struct.unpack("<H",f2.read(2))[0] # Сколько прочетать строчек по ширине картинки с даными
        #print("Сколько пропустить прозрачных строчек",skip_lines,"Сколько прочетать строчек с даными",number_lines)

        while True:
            if f2.tell() == size:
                #print("Дошли до конца распаковки\n\n")
                break

            posf = f2.tell()
            unclear = struct.unpack("<H",f2.read(2))[0] # Непонятно
            col = struct.unpack("<H",f2.read(2))[0] # Сколько прочетать цветов
            left = f2.read(1)[0] # Отойти от левого края на байт

            f3.seek(left,1) # Отступить на байт от нынешний позиции
            fd = f2.read(col)
            f3.write(fd)
            #print("Непонятно",unclear,"Позиция",posf)
            #print("Прочетать цветов",col)
            #print("Отойти от левого края на байт",left)

            line_w += 1 # Закончили работу со строчкой
            f3.seek(line_w*w) # Переход на новую строчку по высоте картинки
            #print("Конец строчки Переход на новую",line_w*w,"Строчна номер",line_w)
            #print("##################################################\n")

        f3.seek(0,2) # Для расчёта Чтоб больше файла картинки не распаковалось
        posf3 = f3.tell() # Конец файла

        f3.seek(0)
        f_image = Image.frombuffer('P', (w,h), f3.read(w*h), 'raw', 'P', 0, 1) 
        f_image.putpalette(Pal)
        self.images.append(f_image)

        f3.close()
        f2.close()

        if w*h < posf3:
            print("   @@@@@@@@@@  Ошибка Распаковалось больше байт чем размер картинки на",posf3-w*h,"!!!!!!")

    def Unpack_type_8(self,f2,f3,size,w,h,Pal):
        line_w = 0 # Строка на которой мы находимся
        skip_lines = struct.unpack("<H",f2.read(2))[0] # Сколько пропустить прозрачных строчек
        line_w += skip_lines # Для пропуска строчек в начале файла
        f3.seek(line_w*w) # Переход на новую строчку по высоте картинки
        number_lines = struct.unpack("<H",f2.read(2))[0] # Сколько прочетать строчек по ширине картинки с даными
        #print("Сколько пропустить прозрачных строчек",skip_lines,"Сколько прочетать строчек с даными",number_lines)

        while True:
            if f2.tell() == size:
                #print("Дошли до конца распаковки\n\n")
                break

            check = f2.read(1)[0] # Действие
            HEX = hex(check)[2:].rjust(2, '0')
            HEX = HEX.upper() # Преобразование строки к верхнему регистру
            #print("    Позиция чтения",f2.tell()-1,"что прочетали",check,"Байт",HEX)

            if check >= 0xE0: # Просто прочетать байты
                col = check - 0xE0
                fd = f2.read(col) # Прочетать
                f3.write(fd)
                #print("E0 прочетали байтов цветов",col,"Байты",fd)

            elif check >= 0xC0: # Повторить следующий байт
                col = check - 0xC0
                fd = f2.read(col) # Прочетать
                f3.write(fd)
                #print("C0 прочетали байтов цветов",col,"Байты",fd)

            elif check >= 0xA0: # Сколько прочетать байтов цвета
                col = check - 0xA0
                fd = f2.read(col) # Читаем цвет col
                f3.write(fd)
                #print("A0 Прочетать цветов",col)

            elif check >= 0x80: # Сколько прочетать байтов цвета
                col = check - 0x80
                fd = f2.read(col) # Читаем цвет
                f3.write(fd)
                #print("Прочетать цветов",col)

            elif check >= 0x60: # Просто прочетать Изменёный цвет
                col = check - 0x60
                fd = f2.read(col) # Читаем цвет
                f3.write(fd)
                #print("60 Прочетать цветов",col)            

            elif check >= 0x40: # Отойти от левого края на байт
                col = check - 0x40
                fd = f2.read(col) # Прочетать Изменёный цвет
                f3.write(fd)
                #print("40 прочетали байтов цветов",col,"Байты",fd)

            elif check >= 0x20: # Просто прочетать байты
                col = check - 0x20
                fd = f2.read(col) # Прочетать
                f3.write(fd)
                #print("20 прочетали байтов цветов",col,"Байты",fd)

            elif check >= 0x01: # Отойти от левого края на байт
                #print("Отойти от левого края на байт",check,"Байт",HEX)
                f3.seek(check,1) # Отступить на байт от нынешний позиции

            elif check == 0:
                line_w += 1 # Закончили работу со строчкой
                f3.seek(line_w*w) # Переход на новую строчку по высоте картинки
                #print("Конец строчки Переход на новую",line_w*w,"Строчна номер",line_w)
                #print("##################################################")

            else:
                print("ОШИБКА НЕПОНЯТНЫЙ ТИП")
                break

        f3.seek(0,2) # Для расчёта Чтоб больше файла картинки не распаковалось
        posf3 = f3.tell() # Конец файла

        f3.seek(0)
        f_image = Image.frombuffer('P', (w,h), f3.read(w*h), 'raw', 'P', 0, 1) 
        f_image.putpalette(Pal)
        self.images.append(f_image)

        f3.close()
        f2.close()

        if w*h < posf3:
            print("   @@@@@@@@@@  Ошибка Распаковалось больше байт чем размер картинки на",posf3-w*h,"!!!!!!")
        