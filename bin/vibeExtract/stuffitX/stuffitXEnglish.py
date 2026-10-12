# Vibe coded by Codex
"""Decode StuffIt X's fixed-dictionary English preprocessing filter.

Based on XADMaster's XADStuffItXEnglishHandle.m:
Copyright (c) 2017-present, MacPaw Way Ltd. All rights reserved.
This module is licensed under LGPL-2.1-or-later, without any warranty.
See LICENSE-XADMaster.txt and stuffitX.txt for provenance.
"""

import gzip
import hashlib
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def english_dictionary():
    """Load and authenticate the format's ordered, immutable word list."""
    path = Path(__file__).with_name('stuffitXEnglishDictionary.gz')
    try:
        with gzip.open(path, 'rb') as source:
            data = source.read(881864)
    except (OSError, EOFError) as exc:
        raise ValueError(f'Cannot load English dictionary {path}: {exc}') from exc
    if (len(data) != 881863 or hashlib.sha256(data).hexdigest() !=
            '6095ebdbadd794ac50fe5b53b12a744b5833e046658777ee37dcb6da82512a31'):
        raise ValueError('Invalid StuffIt X English dictionary')
    return tuple(data[:-1].split(b'\n'))


def unfilter_english(data, output_size):
    """Expand all tokens, refusing truncated, invalid, or oversized output."""
    if len(data) < 4:
        raise ValueError('Truncated English filter header')
    escape, plain, first, upper = data[:4]
    if len({escape, plain, first, upper}) != 4:
        raise ValueError('Duplicate English filter control bytes')
    words = english_dictionary()
    result = bytearray()
    pos = 4
    sentence_start = True

    while pos < len(data):
        char = data[pos]
        pos += 1
        if char == escape:
            if pos == len(data):
                raise ValueError('Truncated English literal escape')
            result.append(data[pos])
            pos += 1
            sentence_start = False
        elif char in (plain, first, upper):
            index = 0
            delimiter = None
            while pos < len(data):
                digit = data[pos]
                pos += 1
                if 97 <= digit <= 122:
                    index = index * 52 + digit - 96
                elif 65 <= digit <= 90:
                    index = index * 52 + digit - 38
                else:
                    delimiter = digit
                    break
                if index >= len(words):
                    raise ValueError(f'English dictionary index out of range: {index}')

            word = words[index]
            if char == upper:
                word = word.upper()
            elif char == first:
                word = word[:1].upper() + word[1:]
            if sentence_start:
                word = word[:1].swapcase() + word[1:]
            result.extend(word)

            # The terminator belongs to this token; it is not another opcode.
            if delimiter == escape:
                if pos == len(data):
                    raise ValueError('Truncated English delimiter escape')
                delimiter = data[pos]
                pos += 1
            if delimiter is not None:
                result.append(delimiter)
            sentence_start = delimiter in (ord('.'), ord('?'), ord('!'))
        else:
            if sentence_start and (65 <= char <= 90 or 97 <= char <= 122):
                char ^= 32
                sentence_start = False
            if char in (ord('.'), ord('?'), ord('!')):
                sentence_start = True
            elif char not in b' \n\r\t':
                sentence_start = False
            result.append(char)

        if len(result) > output_size:
            raise ValueError('English filter output exceeds declared size')

    if len(result) != output_size:
        raise ValueError(f'English filter size mismatch: expected {output_size}, got {len(result)}')
    return bytes(result)
