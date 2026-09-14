# Vibe coded by Codex
"""MacBinary container framing for native MacDraw data forks.

The container is validated independently of the enclosed document signature.
No filenames, Finder type guesses, or searches for embedded magic are used.
"""
from __future__ import annotations

import binascii
from dataclasses import dataclass
import hashlib
import struct


class ContainerError(ValueError):
    pass


@dataclass
class Container:
    data: bytes
    data_offset: int
    resource: bytes
    resource_offset: int
    metadata: dict
    spans: list
    issues: list


def unpack_macbinary(raw, *, recover=False):
    """Return a bounded MacBinary I/II/III container, or None for other inputs."""
    if (len(raw) < 128 or raw[0] or not 1 <= raw[1] <= 63
            or raw[74] or raw[82]):
        return None
    issues = []
    def damage(offset, length, code, detail):
        if not recover:
            raise ContainerError(f'0x{offset:x}: {detail}')
        issues.append((offset, length, 'recovery_macbinary_'+code, detail))
    version = raw[122]
    if version not in (0,129,130):
        raise ContainerError(f'unsupported MacBinary version byte {version}')
    if version:
        if not 129 <= raw[123] <= version:
            raise ContainerError('unsupported MacBinary minimum version')
        if version == 130 and raw[102:106] != b'mBIN':
            raise ContainerError('MacBinary III header lacks mBIN signature')
        actual = binascii.crc_hqx(raw[:124],0)
        stored = struct.unpack_from('>H',raw,124)[0]
        if actual != stored:
            damage(124,2,'crc','MacBinary header CRC mismatch; declared fork boundaries retained')
        secondary = struct.unpack_from('>H',raw,120)[0]
    else:
        actual = stored = None
        secondary = 0
        if any(raw[101:128]):
            damage(101,27,'reserved_header','MacBinary I reserved header bytes are nonzero; interpreted only the version-I fields')
    dl,rl = struct.unpack_from('>2I',raw,83)
    comment_length = struct.unpack_from('>H',raw,99)[0]
    if dl > 0x7fffffff or rl > 0x7fffffff:
        raise ContainerError('invalid MacBinary fork length')
    spans = [(0,128,'macbinary_header')]
    def region(offset, length, name):
        if offset+length > len(raw):
            raise ContainerError(f'0x{offset:x}: truncated MacBinary {name}')
        if length:spans.append((offset,length,'macbinary_'+name))
        return offset+length
    def padding(offset, name, required=True):
        end = (offset+127)//128*128
        if end > len(raw):
            if required:
                raise ContainerError(f'0x{offset:x}: truncated MacBinary {name}')
            damage(offset,len(raw)-offset,'padding','MacBinary final alignment padding is truncated')
            end = len(raw)
        if end > offset:
            region(offset,end-offset,name)
            if any(raw[offset:end]):
                damage(offset,end-offset,'padding','MacBinary alignment padding is nonzero; fork contents retained')
        return end
    pos = region(128,secondary,'secondary_header')
    pos = padding(pos,'secondary_padding')
    da = pos
    pos = region(pos,dl,'data_fork')
    pos = padding(pos,'data_padding',required=bool(rl or comment_length))
    ra = pos
    pos = region(pos,rl,'resource_fork')
    if rl:pos = padding(pos,'resource_padding',required=bool(comment_length))
    ca = pos
    pos = region(pos,comment_length,'finder_comment')
    if comment_length:pos = padding(pos,'comment_padding',required=False)
    if pos < len(raw):
        region(pos,len(raw)-pos,'trailing_bytes')
        damage(pos,len(raw)-pos,'trailing_bytes','MacBinary has bytes beyond its declared forks/comment; retained as inactive container data')
    data,resource = raw[da:da+dl],raw[ra:ra+rl]
    def fork(offset,body):
        return dict(offset=offset,length=len(body),sha256=hashlib.sha256(body).hexdigest())
    meta = dict(format='MacBinary',version={0:'I',129:'II',130:'III'}[version],
                name=raw[2:2+raw[1]].decode('mac_roman'),
                file_type=raw[65:69].decode('mac_roman'),creator=raw[69:73].decode('mac_roman'),
                data_fork=fork(da,data),resource_fork=fork(ra,resource),
                secondary_header=dict(offset=128,length=secondary),
                finder_comment=dict(offset=ca,length=comment_length),
                header_crc_stored=stored,header_crc_calculated=actual)
    return Container(data,da,resource,ra,meta,spans,issues)
