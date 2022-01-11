# work out the height of a glyph in order to calculate dimensions
# like ascender, capHeight etc
def getHeight(glyphBitmap, pixelsBelowBaseline):
    height = len(glyphBitmap)
    for row in glyphBitmap:
        if int(row) > 0:
            break
        height -= 1

    return height - pixelsBelowBaseline + 1

# work out the depth of a glyph in order to calculate descender
def getDepth(glyphBitmap, pixelsBelowBaseline):
    reversedGlyphBitmap = list(reversed(glyphBitmap))
    height = 0
    for row in reversedGlyphBitmap:
        if int(row) > 0:
            break
        height += 1

    return height - pixelsBelowBaseline + 1