def pad_up(size, factor):
    """Pad size up to a multiple of a factor"""
    x = size + factor - 1
    return x - (x % factor)


def bits(ntotal, nset):
    """Return a buffer of ntotal bits with the first nset set to 1"""
    assert ntotal % 8 == 0

    nset = max(nset, 0)
    nset = min(nset, ntotal)

    accum = bytearray()

    accum.extend(b'\xFF' * (nset // 8))
    nset -= len(accum) * 8

    partial = nset % 8
    if partial:
        accum.extend([b'\x00', b'\x80', b'\xC0', b'\xE0', b'\xF0', b'\xF8', b'\xFC', b'\xFE', b'\xFF'][partial])
        nset =- partial

    final_len = pad_up(ntotal, 8) // 8
    accum.extend(b'\x00' * (final_len - len(accum)))

    return bytes(accum)


def chunkify(b, blksize):
    for i in range(0, len(b), blksize):
        ab = b[i:i+blksize]
        if len(ab) < blksize: ab += bytes(blksize-len(ab))
        yield ab


def pstring(orig):
    return bytes([len(orig)]) + orig
