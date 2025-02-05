#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ZetpeR xax007@yandex.ru
# Сказки на бересте: Хождение за тридевять земель

import os, sys, io, struct
from PIL import Image
import numpy as np

NAME = "Сказки на бересте: Хождение за тридевять земель" 
FORMATS_ARCHIVE = ['000']
TYPES_ARCHIVE = [('Сказки на бересте: Хождение за тридевять земель', ('*.000'))]
GAMES = ["Сказки на бересте: Хождение за тридевять земель"]
AUTHOR = "ZetpeR xax007@yandex.ru"

class Game_Res(object):
    def __init__(self,app):
        self.file = None
        self.data = [] 
        self.app = app

        self.sup_formats = ["snd",
                            "wav",
                            "txt",
                            "gif",
                            "chf",
                            "spr"]

        self.sup_types = {"snd":3,
                          "wav":3,
                          "txt":4,
                          "gif":1,
                          "chf":2,
                          "spr":2}

        self.images = []  
        self.sound = None
        self.text = None

    def open_data(self,file):
        format = file.split(".")[-1].lower()
        if format == "000":
            self.OpenArchive000(file)

    def unpack(self,data_res):
        self.images = []
        self.sound = None

        name = data_res[0]
        offset = data_res[1]
        size = data_res[2]
        format = data_res[3]
        self.file.seek(offset)
        if format == "snd":
            self.Unpack_SND(io.BytesIO(self.file.read(size)))
        elif format == "wav":
            self.Unpack_WAV(io.BytesIO(self.file.read(size)))
        elif format == "txt":
            self.Unpack_TXT(io.BytesIO(self.file.read(size)))
        elif format == "gif":
            self.Unpack_GIF(io.BytesIO(self.file.read(size)))
        elif format == "chf":
            self.Unpack_CHF(io.BytesIO(self.file.read(size)), data_res[4]) 
        elif format == "spr":
            self.Unpack_SPR(io.BytesIO(self.file.read(size)), data_res[4])

    def OpenArchive000(self,file):
        self.data = []

        f = open(file,"rb")
        path_1, mult_file = os.path.split(file) # Разбиение на путь и файл

        type = f.read(30) # Тип архива
        if type != b'SGRSresource file\r\n\x1a\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00': # Проверка на архив
            print("ЭТО НЕ АРХИВ", type)
            return(0)

        offset_tab = struct.unpack("<I",f.read(4))[0] # Оффсет таблицы файлов
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        fd = f.read(66) # Непонятный блок данных заголовка

        f.seek(offset_tab) # Переход на начало таблицы
        unclear = struct.unpack("<I",f.read(4))[0] # Непонятно Байты всегда 45 83 57 34
        col = struct.unpack("<I",f.read(4))[0] # Количество файлов
        ss = -1 # Номер файла для архива GRAPHICS.000 нужно для чтения палитр

        for i in range(col): # Одна строчка занимает 88 байт
            offset = struct.unpack("<I",f.read(4))[0] # Оффсет в начале файла непонятный заголовок +114 байт
            size = struct.unpack("<I",f.read(4))[0] # Размер
            f_path_1 = f.read(40).split(b"\x00")[0].decode("utf8") # Просто имя файла
            f_path_2 = f.read(40).split(b"\x00")[0].decode("utf8") # Имя файла с путём к папке

            # NOISE.000
            # Первые 40 байт Только часть имени файла.
            # Вторые 40 байт Есть имя файлов нет папок

            # SPEECH.000
            # Первые 40 байт Только часть имени файла.
            # Вторые 40 байт Второй блок есть имя файлов нет папок,

            # TEXT.000 
            # Первые 40 байт Есть папки. 
            # Вторые 40 байт Нету текста.

            # GRAPHICS.000
            # Первые 40 байт Есть путь папки и имя файла (Имя файла отличается от вторых данных)
            # Вторые 40 байт Есть имена файлов но не у всех файлов

            if mult_file.lower() in ["noise.000", "speech.000"]:
                # noise.000 все файлы внутри формата .wav
                # speech.000 все файлы внутри формата .snd

                self.data.append(("Заголовки\\"+f_path_2+".bin", offset, 114, "bin")) # Непонятный заголовок у файлов

                format = f_path_2.split(".")[-1].lower()
                self.data.append((f_path_2, offset+114, size, format))

            elif mult_file.lower() == "text.000": # Тип файла у всех будет txt
                broken_list = f_path_1.split(".") # Разбиваем по разделителю
                col_broken_list = len(broken_list) # На сколько разделено частей
                f_path_3 = "" # Путь к файлу

                for ii in range(col_broken_list-2): # Последнии два не трогаем это имя файла и тип файла.
                    f_path_3 += broken_list[0]+"\\" # Добавляем первый элемент списка к новому пути
                    broken_list.pop(0) # Удаляем первый элемент папки

                if broken_list[1] == "": # После файла идёт . точка это создаёт ошибку просто добавляем .txt      TEXT.observ.busy2. встречается только в одном файле.
                    name = broken_list[0]+".txt" # Имя файла
                    #print(f_path_1, " ", f_path_3, "", name)

                else:
                    name = broken_list[0]+"."+broken_list[1]+".txt" # Имя файла + тип файла
                    # но так перезаписываются два файла

                if name == "laby.use_ink.txt" or name == "use_ink.noise.txt": # Это файл перезаписывается 
                    #print(f_path_1, " ", f_path_3, "", name, i)
                    name = str(i)+" "+name # Даём ему уникальный номер
                    # TEXT два файла перезаписались
                    # 704 TEXT.labywat.laby.use_ink
                    # 705 TEXT.labywat.laby.use_ink
                    # 702 TEXT.labywat.laby.use_ink.noise
                    # 706 TEXT.labywat.laby.use_ink.noise

                self.data.append(("Заголовки\\"+f_path_3+name+".bin", offset, 114, "bin")) # Непонятный заголовок у файлов

                format = (f_path_3+name).split(".")[-1].lower()
                self.data.append((f_path_3+name, offset+114, size, format))

            elif mult_file.lower() == "graphics.000":
                broken_list = f_path_1.split(".") # Разбиваем по разделителю
                col_broken_list = len(broken_list)-1 # На сколько разделено частей
                f_path_3 = broken_list[0]+"\\" # Путь к файлу
                broken_list.pop(0) # Удаляем из списка путь

                # Работаем с именим файла втором строчке
                # Сначало идёт это нужно удалить из имени #: если он есть
                if f_path_2[:2] == "#:": # Берём срез если первые два символа это #: то удаляем их
                    f_path_2 = f_path_2[2:] # Удаляем первые два символа "#:" из имени файла
                broken_list_f_path_2 = f_path_2.split(".") # Разбиваем по разделителю имя файла f_path_2

                # Обрабатываем имена файлов и расширений чтобы они были правельными
                if f_path_2 == "": # Пустая строчка нечего не делаем
                    # Вторая строчка нет имени файла ""
                    pass

                # Файлам с типом .pal даём новый тип .col
                # Первая строчка тип файла pal а вовторой строчке тип файла col меняем чтоб в первой строчке тип файла был col
                elif broken_list[col_broken_list-1] == "pal" and broken_list_f_path_2[1] == "col":
                    broken_list.pop(col_broken_list-1) # Удаляем из списка
                    broken_list.append("col") # Добавляем расширение для файла
                    #print(broken_list,broken_list_f_path_2)

                # Добавляем картинкам расширение spr
                elif broken_list_f_path_2[1] == "spr":
                    broken_list.append("spr") # Добавляем расширение
                    # Получается что тип файлов .spr всегда надо добавлять к именам файлов так как уних нет типа файла в первой строчке, уних есть только имя.

                # Нечего не делаем
                elif broken_list_f_path_2[1] in ["col", "tab", "z"]:
                    pass

                # Добавляем расширение
                elif broken_list_f_path_2[1] in ["chf", "smk", "xmi", "txt", "gif", "bld"]:
                    broken_list.append(broken_list_f_path_2[1]) # Добавляем расширение

                else: # Что надо сделать чтобы имена файлов были правельные слева
                    print("Исправить эти файлы")
                    print(f_path_3, "", broken_list, "", f_path_2)

                name = "" # Имя файла собрано
                temp = len(broken_list)

                for ii in range(temp):
                    name += broken_list[0] # Добавляем первый элемент списка к новому пути
                    broken_list.pop(0) # Удаляем первый элемент папки
                    if ii == temp-1: # Это чтобы не добавить точку в строчку после последнего расшинения файла
                        break
                    name += "." # Добавляем точку

                # Меняем тип файлов на текстовый
                b_list = name.split(".") # Разбиваем по разделителю
                col_b = len(b_list) # На сколько разделено частей
                if b_list[col_b-1] in ["bld", "help", "id", "z"]:
                    name += ".txt"

                ss += 1
                self.data.append(("Заголовки\\"+f_path_3+name+".bin", offset, 114, "bin")) # Непонятный заголовок у файлов

                format = (f_path_3+name).split(".")[-1].lower()
                self.data.append((f_path_3+name, offset+114, size, format, ss))
        self.file = f

    def Unpack_SND(self, f):
        fd = f.read()
        size = f.tell()

        wav = b""
        wav += b"RIFF"
        wav += struct.pack("<I", size+44-8) # chunkSize размер файла-8
        wav += b"WAVE" # format WAVE
        wav += b"fmt " # subchunk1Id fmt 0x666d7420

        subchunk1Size = 16 # 
        audioFormat = 1 #
        numChannels = 1 # Количество каналов
        sampleRate = 11025 # Первая частота
        byteRate = 44100 # Вторая частота
        blockAlign = 2
        bitsPerSample = 8 # 16 битность звука

        wav += struct.pack("<IHHIIHH", subchunk1Size, audioFormat, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample)
        wav += b"data"
        wav += struct.pack("<I", size)
        wav += fd # Данные
        f2 = io.BytesIO(wav)
        self.sound = f2
        f.close()

    def Unpack_WAV(self, f):
        self.sound = f

    def Unpack_TXT(self, f):
        f.seek(0,2)
        end_f = f.tell() # Получаем размер файла
        f.seek(0)

        f.seek(end_f-2)
        check_1 = f.read(2) # Проверка

        f.seek(end_f-1)
        check_2 = f.read(1) # Проверка

        if check_1 == b'\x00\x1A':
            f.seek(0)
            self.text = f.read(end_f-2).decode("cp866")

        elif check_2 == b'\x1A':
            f.seek(0)
            self.text = f.read(end_f-1).decode("cp866")

        else:
            print("Текст, непонятно есть ли ненужные байты", check_1)

    def Unpack_GIF(self, f):
        image = Image.open(f)
        self.images = [image]

    def Unpack_CHF(self, f, file_number):
        #default.chf game.chf game_white.chf puzzle.cross.font.chf system.chf times22.chf
        if file_number in [887, 890, 891, 1038, 889, 888]:
            name_2 = 1757 # "map.map3.col"

        elif file_number == 894: # "game_cyan.chf"
            name_2 = 741 # "xlabx.col"

        elif file_number in [892, 893]: # game_green.chf  game_shadow.chf
            name_2 = 251 # "loug.col"

        else:
            print("ОШИБКА непонятно какая палитра нужна", file_number)

        # Чтение палитры
        self.file.seek(self.data[name_2][1] + 8)
        Pal = self.file.read(768) # Палитра

        data = [] # Список ширин картинок
        type = f.read(4) # Тип архива
        if type != b'TSG\x00': # Проверка
            print("ЭТО шрифт", type)
            return(0) # Остановка скрипта

        f.seek(0,2)
        end_f = f.tell() # Конец файла

        f.seek(9)
        col_pic = struct.unpack("<H",f.read(2))[0] # Количество картинок

        f.seek(15)
        h = struct.unpack("<H",f.read(2))[0] # Читаем высоту
        #print("Размер файла", end_f, "Количество картинок", col_pic, "Высота картинок", h)

        f.seek(81)
        for i in range(223):
            w = struct.unpack("<H",f.read(2))[0] # Читаем ширину
            if w != 0: # Если ширина картинки неравна 0
                data.append(w)

        f.seek(529) # Начало картинок
        ss = 0 # Номер картинки для имени файла

        for ii in range(len(data)):
            ss += 1
            fd = f.read(1)[0] # Чтения одного байта
            size = data[ii] * h # Размер картинки
            #print(fd, "ширина высота картинки", data[ii], h, "размер файла", size, "позиция", f.tell()-1)

            w = data[ii] # Ширина картинки
            f_image = Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1)
            f_image.putpalette(Pal) # Добавляем палитру в картинку
            self.images.append(f_image)

        f.close()

    def Unpack_SPR(self, f, file_number):
        dictionary = {483:65,486:65,484:65,485:65,487:65,714:390,715:390,716:390,717:390,718:395,719:395,720:395,721:395,569:195,570:200,571:200,572:200,573:200,574:200,575:200,576:200,490:75,488:75,492:75,494:75,489:75,493:75,495:75,491:75,496:80,497:80,498:80,499:80,500:80,501:80,502:80,503:80,504:80,737:420,746:420,747:420,748:420,749:420,738:420,739:420,740:420,741:420,742:420,743:420,744:420,745:420,736:420,577:205,579:205,578:205,505:85,506:85,515:85,516:85,517:85,518:85,519:85,520:85,521:85,507:85,508:85,509:85,510:85,511:85,512:85,513:85,514:85,449:0,580:210,752:925,750:925,754:925,756:925,751:925,755:925,757:925,753:925,583:215,584:215,582:215,581:215,687:315,758:759,522:90,523:90,762:929,760:929,764:929,766:929,761:929,765:929,767:929,763:929,524:95,525:100,526:105,453:5,451:452,450:5,454:10,457:15,458:15,456:15,455:15,587:220,586:220,585:220,588:220,463:20,460:20,459:20,461:20,462:20,859:420,818:420,772:420,775:420,773:420,828:420,784:420,814:420,812:420,798:420,817:420,785:420,822:420,776:420,786:420,771:420,782:420,806:420,819:420,813:420,823:420,781:420,791:420,827:420,804:420,821:420,824:420,778:420,796:420,795:420,797:420,794:420,793:420,805:420,800:420,801:420,803:420,790:420,807:420,826:420,780:420,788:420,820:420,808:420,810:420,811:420,783:420,815:420,816:420,799:420,779:420,809:420,774:420,789:420,825:420,792:420,777:420,802:420,787:420,861:420,863:420,860:420,862:420,527:110,856:420,855:420,854:420,853:420,857:420,866:420,865:420,864:420,869:420,868:420,867:420,533:115,534:115,530:115,531:115,532:115,529:115,528:115,847:937,845:937,849:937,851:937,846:937,850:937,852:937,848:937,831:937,829:937,833:937,835:937,830:937,834:937,836:937,832:937,839:937,837:937,841:937,843:937,838:937,842:937,844:937,840:937,618:265,619:265,621:265,620:265,589:225,590:225,591:225,592:225,599:230,593:230,594:230,595:230,596:230,597:230,598:230,600:235,601:235,602:240,464:25,466:30,467:30,468:30,465:30,622:270,623:270,624:270,625:270,626:270,627:270,628:270,535:120,536:120,882:877,870:876,871:877,872:878,873:879,874:880,875:881,886:884,883:884,537:130,538:130,541:135,540:135,539:135,632:275,629:275,633:275,631:275,630:275,723:400,722:400,688:320,542:140,724:405,725:405,726:405,543:145,1019:1020,1022:1020,1023:1037,1032:1037,1034:1037,1036:1037,1039:1040,1042:1040,1043:1040,1024:1025,1026:1025,1045:1046,1047:1046,1048:1046,1049:1046,1027:1028,1030:1028,1031:1028,1029:1028,690:325,689:325,858:420,727:410,728:410,729:410,730:410,469:35,644:280,643:280,634:280,635:280,636:280,637:280,638:280,639:280,640:280,641:280,642:280,646:285,645:285,472:40,470:40,471:40,544:150,546:150,545:150,547:150,549:155,548:155,691:330,692:330,550:160,551:160,476:45,475:45,477:45,474:45,473:45,647:290,648:290,649:290,650:290,651:290,652:290,603:245,604:245,605:245,606:250,607:250,653:295,654:295,655:295,656:295,657:295,658:295,659:295,660:295,661:300,663:300,664:300,665:300,662:300,608:255,732:415,733:415,735:415,731:415,734:415,554:175,552:175,553:175,478:55,480:55,479:55,481:55,555:180,556:180,557:180,558:180,559:180,560:180,561:180,562:180,563:180,668:305,670:305,667:305,666:305,669:305,564:185,482:420,611:420,609:420,613:420,615:420,610:420,614:420,616:420,612:420,685:420,686:420,708:420,706:420,710:420,712:420,707:420,711:420,713:420,709:420,693:345,694:345,695:345,696:345,697:350,700:350,699:350,698:350,701:355,703:380,702:380,705:385,704:385,566:190,567:190,565:190,568:190,675:310,671:310,672:310,673:310,674:310,676:310,677:310,678:310,679:310,680:310,681:310,682:310,683:310,684:310,896:897,900:901,904:905,908:933,912:913,916:917,920:937,924:925,928:929,932:933,936:937,940:941,944:945,948:949,952:953,956:957,960:961,964:965,968:969,972:973,980:981,984:985,976:977,988:989,992:993,996:997,1000:1001,1004:1005,1008:1009,1012:1013,1016:1017,617:260}

        report = dictionary.get(file_number) # Возвращает значение ключа

        if report != None: # Если у файла есть палитра
            report = (report*2)+1 # Номер палитры в архиве
            self.file.seek(self.data[report][1] + 8)
            #size = struct.unpack("<I",self.file.read(4))[0] # Размер 8 + 768
            #unclear = struct.unpack("<I",self.file.read(4))[0] # Непонятно
            Pal = self.file.read(768) # Палитра
            #self.file.read(1) # Непонятно 1 байт 1A

        else:
            print("Неизвестна какая палитра у файла")

        f.seek(0,2)
        end_f = f.tell() # Конец файла
        f.seek(0)

        tip = f.read(5) # Тип файла
        # TSGs контейнер с несколькими файлами Заголовок занимает 27 байт
        # TSGbu Одна картинка

        if tip == b'TSGs\x00': # Заголовок 31 байт
            unclear_1 = f.read(2) # Непонятно
            col_1 = struct.unpack("<H",f.read(2))[0] # Количество кадров
            col_2 = struct.unpack("<H",f.read(2))[0]
            #print("Количество кадров", col_1, col_2)
            unclear_2 = f.read(16) # Непонятно

            for i in range(col_1):
                f_pos_0 = f.tell()
                unclear_3 = f.read(2) # Непонятно записано всегда байты 73 10
                animation_number = struct.unpack("<H",f.read(2))[0] # Номер анимации начинается с 00 00
                #print("Начало данных картинки",f_pos_0, "Номер анимации",animation_number)

                tip_2 = f.read(5) # Тип файла
                if tip_2 in [b'TSGbu', b'TSGbr']:
                    f.seek(f_pos_0+4) # Начало картинки
                    self.Unpacking_spr(f, Pal) # Распаковка

                else:
                    print("   Ошибка другой тип анимации заголовка", f_pos_0, tip_2, mult_file)
                    f.close()
                    return(0) # Остановка скрипта

        elif tip == b'TSGbu': # Всего таких файлов 58 
            f.seek(0) # Возврат на начало файла
            self.Unpacking_spr(f, Pal) # Распаковка

        else:
            print("Непонятный тип",tip,mult_file)
            f.close()
            return(0) # Остановка скрипта

        check = f.read(1) # Проверка должен быть 1A это чтото вроде остановки
        if check != b'\x1A':
            print("Ошибка последний байт не 1A:",check)

        if f.tell() != end_f:
            print("Ошибка в конце есть ещё непрочитанные данные",f.tell())

        f.close()

    def Unpacking_spr(self, f, Pal):
        f_pos = f.tell()
        tip_2 = f.read(5) # Тип файла может быть TSGbr или TSGbu
        unclear_1 = f.read(2) # Непонятно
        w, h = struct.unpack("<HH",f.read(4)) # Ширина и высота
        unclear_2 = f.read(10) # Непонятно
        size = struct.unpack("<I",f.read(4))[0] # Размер одной картинки
        unclear_3 = f.read(8) # Непонятно

        if tip_2 == b'TSGbu': # Не сжатая картинка
            if w == 0 and h == 0:
                #print("Пустой кадр Высота и ширина", w,h)
                pass

            else:
                #print("Высота и ширина", w,h)
                f_image = Image.frombuffer('P', (w,h), f.read(w*h), 'raw', 'P', 0, 1)
                f_image.putpalette(Pal)
                self.images.append(f_image)

        elif tip_2 == b'TSGbr': # Сжатая картинка
            fd = f.read(size) # Сжатые данные
            f1 = io.BytesIO(fd) # Файл с жатыми данными
            f2 = io.BytesIO() # Распакованные данные

            while f1.tell() != size: # Остановка когда достигним конца файла.
                byte = f1.read(1) # Байт индефикатор
                if byte[0] > 0xC0: # Байт сжат 
                    f2.write(f1.read(1)*(byte[0] - 0xC0)) # Сколько раз повторить следующий байт за ним
                else:
                    f2.write(byte)

            f1.close() # Закрытие файла сжатыми данными

            if f2.tell() == w*h:
                f2.seek(0)
                f_image = Image.frombuffer('P', (w,h), f2.read(w*h), 'raw', 'P', 0, 1)
                f_image.putpalette(Pal)
                self.images.append(f_image)

            else:
                print("    Ошибка распакованый файл неправельного размера",f2.tell(),"должен быть размером", w*h)

            f2.close()
