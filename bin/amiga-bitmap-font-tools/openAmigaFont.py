#!/usr/bin/python3

import json
import sys
import getopt
from shutil import rmtree
from metrics import getHeight, getDepth
from drawing import drawPixel
from style import getHumanReadableStyle, expandStyle, expandFlags
from utils import chunks, getRange, getNiceGlyphName
from fontParts.world import *
from fontmake import font_project


def main(argv):
    inputFile = ''
    outputFile = ''
    fontFormat = ''
    tmpPath = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:f:t:",["input_file=","output_file=","format=","tmp_path="])
    except getopt.GetoptError:
        print('Usage: openAmigaFont.py -i <inputfile> -o <outputfile> -f <format> -t <tmpPath>')
        print('where format is one of ufo, ttf, otf')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: openAmigaFont.py -i <inputfile> -o <outputfile> -f <format> -t <tmpPath>')
            print('where format is one of ufo, ttf, otf')
            sys.exit()
        elif opt in ("-i", "--input_file"):
            inputFile = arg
        elif opt in ("-o", "--output_file"):
            outputFile = arg
        elif opt in ("-t", "--tmp_path"):
            tmpPath = arg
        elif opt in ("-f", "--format"):
            fontFormat = arg
            if fontFormat not in ('ufo', 'ttf', 'otf'):
                print('Format must be one of ufo, ttf, otf')
                sys.exit(2)

    if inputFile == '':
        print('Please specify the path to an input file')
        sys.exit(2)
    
    if outputFile == '':
        print('Please specify the path to an output file')
        sys.exit(2)

    if tmpPath == '':
        print('Please specify the path to an tmp path')
        sys.exit(2)
       

    binaryFile = open(inputFile, 'rb')
    rawBytes = bytearray(binaryFile.read())

    # strip the first 32 bytes off to make the pointer locations accurate
    fontBytes = rawBytes[32:]

    fontNameBytes = bytearray(32)
    fontNameBytes[:] = fontBytes[26:58]
    trimmedFontNameBytes = fontNameBytes.replace(b'\x00', b'')

    fontName = trimmedFontNameBytes.decode('ascii')
    ySize = int.from_bytes(fontBytes[78:80], byteorder='big', signed=False)
    style = int.from_bytes(fontBytes[80:81], byteorder='big', signed=False)
    flags = int.from_bytes(fontBytes[81:82], byteorder='big', signed=False)
    xSize = int.from_bytes(fontBytes[82:84], byteorder='big', signed=False)
    baseline = int.from_bytes(fontBytes[84:86], byteorder='big', signed=False)
    boldSmear = int.from_bytes(fontBytes[86:88], byteorder='big', signed=False)
    loChar = int.from_bytes(fontBytes[90:91], byteorder='big', signed=False)
    hiChar = int.from_bytes(fontBytes[91:92], byteorder='big', signed=False)

    # there's an extra "notdef" character which is why we add 2
    charRange = hiChar - loChar + 2

    styleDict = expandStyle(style)
    flagsDict = expandFlags(flags)

    fontDataStart = int.from_bytes(fontBytes[92:96], byteorder='big', signed=False)
    modulo = int.from_bytes(fontBytes[96:98], byteorder='big', signed=False)
    locationDataStart = int.from_bytes(fontBytes[98:102], byteorder='big', signed=False)
    locationData = fontBytes[locationDataStart:]

    if flagsDict['proportional']:
        spacingDataStart = int.from_bytes(fontBytes[102:106], byteorder='big', signed=False)
        kerningDataStart = int.from_bytes(fontBytes[106:110], byteorder='big', signed=False)
        kerningData = fontBytes[kerningDataStart:]
        spacingData = fontBytes[spacingDataStart:]


    fontBitmapData = fontBytes[fontDataStart:(fontDataStart + (modulo * ySize))]
    # From https://stackoverflow.com/questions/43787031/python-byte-array-to-bit-array
    fontBitArray = ''.join(format(byte, '08b') for byte in fontBitmapData)

    fontBitmapRows = list(chunks(fontBitArray, modulo * 8))

    print('Parsing', fontName)
    print(flagsDict, styleDict)

    glyphs = {}

    for i in range(0, charRange):
        charCode = loChar + i
        locationStart = int.from_bytes(locationData[i * 4:i * 4 + 2], byteorder='big', signed=False)
        bitLength = int.from_bytes(locationData[i * 4 + 2:i * 4 + 4], byteorder='big', signed=False)
        charCodeIndex = '.notdef' if charCode > hiChar else str(charCode)
        glyphs[charCodeIndex] = {
            "character": '.notdef' if charCode > hiChar else chr(charCode),
            "bitmap": list(map(lambda arr: getRange(arr, locationStart, bitLength), fontBitmapRows))
        }
        if flagsDict['proportional']:
            glyphs[charCodeIndex]['kerning'] = int.from_bytes(kerningData[i * 2: i * 2 + 2], byteorder='big', signed=True)
            glyphs[charCodeIndex]['spacing'] = int.from_bytes(spacingData[i * 2: i * 2 + 2], byteorder='big', signed=True)

    font = NewFont(familyName=fontName, showInterface=False)
    font.info.unitsPerEm = 1000


    try:
        layer = font.layers[0]
        layer.name = getHumanReadableStyle(styleDict)

        pixelSize = int(font.info.unitsPerEm / ySize)
        print('Font size:', ySize, '... Width', xSize, '... Baseline:', baseline, '...Block size:', pixelSize)
        pixelsBelowBaseline = ySize - baseline

        # work out x-height from the letter x (ASCII code 120)
        xHeight = getHeight(glyphs['120']['bitmap'], pixelsBelowBaseline)
        if xHeight > 0:
            font.info.xHeight = xHeight * pixelSize

        # work out cap height from the letter E (ASCII code 69)
        capHeight = getHeight(glyphs['69']['bitmap'], pixelsBelowBaseline)
        if capHeight > 0:
            font.info.capHeight = capHeight * pixelSize

        # work out ascender from the letter b (ASCII code 98)
        ascender = getHeight(glyphs['98']['bitmap'], pixelsBelowBaseline)
        if ascender > 0:
            font.info.ascender = ascender * pixelSize

        # work out descender from the letter p (ASCII code 112)
        descender = getDepth(glyphs['112']['bitmap'], pixelsBelowBaseline)
        if descender < 0:
            font.info.descender = descender * pixelSize

        for char, amigaGlyph in glyphs.items():
            if amigaGlyph['character'] == '.notdef':
                glyphName = '.notdef'
            else:
                unicodeInt = ord(amigaGlyph['character'])
                glyphName = getNiceGlyphName(unicodeInt)
                print('Creating', unicodeInt, glyphName)

            glyph = font.newGlyph(glyphName)
            
            if amigaGlyph['character'] != '.notdef':
                glyph.unicode = unicodeInt

            glyph.width = ((amigaGlyph['spacing'] + amigaGlyph['kerning']) * pixelSize) if flagsDict['proportional'] else (xSize * pixelSize)

            for rowNumber, rowData in enumerate(amigaGlyph['bitmap']):
                rowPosition = ySize - rowNumber - pixelsBelowBaseline
                for colNumber, colData in enumerate(rowData):
                    colPosition = (colNumber + amigaGlyph['kerning']) if flagsDict['proportional'] else colNumber
                    if colData == '1':
                        rect = drawPixel( rowPosition, colPosition, pixelSize )
                        glyph.appendContour(rect)
            glyph.removeOverlap()

        if fontFormat == 'ufo':
            font.save(outputFile)
        else:
            font.save(tmpPath)
            fontmaker = font_project.FontProject()
            ufo = fontmaker.open_ufo(tmpPath)
            if fontFormat == 'otf':
                fontmaker.build_otfs([ufo], output_path=outputFile)
            else:
                fontmaker.build_ttfs([ufo], output_path=outputFile)
            rmtree(tmpPath)

        print('Job done. Enjoy the pixels.')
    except Exception as e:
        print('Script error!')
        raise e

if __name__ == "__main__":
   main(sys.argv[1:])
