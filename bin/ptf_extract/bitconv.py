#!/usr/bin/env python3

def str_encode(data, pos, value, strsz, encoding='ascii', terminator=b'\x00'):
    try:
        bytedata = value.encode(encoding)
        if strsz < 0:
            bytedata += terminator
            strsz = len(bytedata)
        if len(bytedata) < strsz:
            bytedata += terminator * (strsz - len(bytedata))
        elif len(bytedata) > strsz:
            raise ValueError('input string too long')
        if pos >= len(data):
            data += bytedata
        else:
            data = data[:pos] + bytedata + data[pos+strsz:]
        return data, pos + strsz
    except IndexError:
        return data, pos + strsz

def int_encode(data, pos, value, intsz=4, byteorder='little'):
    try:
        bytedata = value.to_bytes(intsz, byteorder=byteorder)
        if pos >= len(data):
            data += bytedata
        else:
            data = data[:pos] + bytedata + data[pos+intsz:]
        return data, pos + intsz
    except IndexError:
        return data, pos + intsz

def str_decode(data, pos, strsz, encoding='ascii', terminator=b'\x00'):
    try:
        if strsz < 0:
            strsz = data[pos:].find(terminator) + 1
            if strsz < 0:
                strsz = 1
        value = data[pos:pos+strsz].rstrip(terminator).decode(encoding)
        return value, pos + strsz
    except IndexError:
        return None, pos + strsz

def int_decode(data, pos, intsz=4, byteorder='little'):
    try:
        value = int.from_bytes(data[pos:pos+intsz], byteorder=byteorder)
        return value, pos + intsz
    except IndexError:
        return None, pos + intsz
