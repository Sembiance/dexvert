from utils import bitIsSet

# gets a name from Amiga font style flags
def getHumanReadableStyle( style ):
    if style['normal']:
        return 'Regular'
    name = []
    if style['bold']:
        name.append('Bold')
    if style['italic']:
        name.append('Italic')
    if style['extended']:
        name.append('Extended')
    separator = ' '
    return separator.join(name)

def expandStyle( style ):
    return {
        'value': style,
        'normal': style == 0,
        'underlined': bitIsSet(style, 0),
        'bold': bitIsSet(style, 1),
        'italic': bitIsSet(style, 2),
        'extended': bitIsSet(style, 3),
        'colorfont': bitIsSet(style, 6),
        'tagged': bitIsSet(style, 7)
    }

def expandFlags(flags):
    return {
        'value': flags,
        'disk': bitIsSet(flags, 1),
        'proportional': bitIsSet(flags, 5),
        'designed': bitIsSet(flags, 6)
    }
