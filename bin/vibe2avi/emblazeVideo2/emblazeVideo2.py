#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert the supported Emblaze Video 2 profile to lossless FFV1/PCM AVI.

Requires Python 3.9+ and ffmpeg on PATH. No third-party Python modules or
reference files are needed. See emblazeVideo2.txt for the precise scope.
"""
import argparse
from collections import Counter
from dataclasses import dataclass, field
from fractions import Fraction
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

MAGIC = b"GEO INTERACTIVE MEDIA GROUP\x1a"

VLC = {'intra': {'1': 3,
           '001': 19,
           '010': 35,
           '011': 51,
           '0001': 4,
           '000001': 20,
           '000010': 36,
           '000011': 52,
           '000000001': 255},
 'inter': {'1': 0,
           '010': 2,
           '011': 1,
           '0010': 32,
           '0011': 16,
           '00011': 3,
           '000100': 4,
           '000101': 48,
           '0000011': 51,
           '0000100': 34,
           '0000101': 18,
           '0000110': 33,
           '0000111': 17,
           '00000011': 35,
           '00000100': 19,
           '00000101': 50,
           '000000001': 255,
           '000000010': 52,
           '000000011': 36,
           '000000100': 20,
           '000000101': 49},
 'cbpy': {'11': 0,
          '0011': 15,
          '0100': 3,
          '0101': 5,
          '0110': 1,
          '0111': 10,
          '1000': 2,
          '1001': 12,
          '1010': 4,
          '1011': 8,
          '00010': 7,
          '00011': 11,
          '00100': 13,
          '00101': 14,
          '000010': 9,
          '000011': 6},
 'mv': {'1': 0,
        '010': 1,
        '011': 63,
        '0010': 2,
        '0011': 62,
        '00010': 3,
        '00011': 61,
        '0000110': 4,
        '0000111': 60,
        '00000110': 7,
        '00000111': 57,
        '00001000': 6,
        '00001001': 58,
        '00001010': 5,
        '00001011': 59,
        '0000010010': 10,
        '0000010011': 54,
        '0000010100': 9,
        '0000010101': 55,
        '0000010110': 8,
        '0000010111': 56,
        '00000001000': 24,
        '00000001001': 40,
        '00000001010': 23,
        '00000001011': 41,
        '00000001100': 22,
        '00000001101': 42,
        '00000001110': 21,
        '00000001111': 43,
        '00000010000': 20,
        '00000010001': 44,
        '00000010010': 19,
        '00000010011': 45,
        '00000010100': 18,
        '00000010101': 46,
        '00000010110': 17,
        '00000010111': 47,
        '00000011000': 16,
        '00000011001': 48,
        '00000011010': 15,
        '00000011011': 49,
        '00000011100': 14,
        '00000011101': 50,
        '00000011110': 13,
        '00000011111': 51,
        '00000100000': 12,
        '00000100001': 52,
        '00000100010': 11,
        '00000100011': 53,
        '000000000100': 30,
        '000000000101': 34,
        '000000000110': 29,
        '000000000111': 35,
        '000000001000': 28,
        '000000001001': 36,
        '000000001010': 27,
        '000000001011': 37,
        '000000001100': 26,
        '000000001101': 38,
        '000000001110': 25,
        '000000001111': 39,
        '0000000000101': 32,
        '0000000000110': 31,
        '0000000000111': 33},
 'dct': {'10': 1,
         '110': 17,
         '0111': 4097,
         '1110': 33,
         '1111': 2,
         '01011': 81,
         '01100': 65,
         '01101': 49,
         '001100': 4161,
         '001101': 4145,
         '001110': 4129,
         '001111': 4113,
         '010000': 145,
         '010001': 129,
         '010010': 113,
         '010011': 97,
         '010100': 18,
         '010101': 3,
         '0000011': 7167,
         '0010000': 4225,
         '0010001': 4209,
         '0010010': 4193,
         '0010011': 4177,
         '0010100': 193,
         '0010101': 177,
         '0010110': 161,
         '0010111': 4,
         '00010011': 4353,
         '00010100': 4337,
         '00010101': 4321,
         '00010110': 4305,
         '00010111': 4289,
         '00011000': 4273,
         '00011001': 4257,
         '00011010': 4241,
         '00011011': 225,
         '00011100': 209,
         '00011101': 34,
         '00011110': 19,
         '00011111': 5,
         '000010001': 4481,
         '000010010': 4465,
         '000010011': 4449,
         '000010100': 4433,
         '000010101': 4417,
         '000010110': 4401,
         '000010111': 4385,
         '000011000': 4369,
         '000011001': 4098,
         '000011010': 353,
         '000011011': 337,
         '000011100': 321,
         '000011101': 305,
         '000011110': 289,
         '000011111': 273,
         '000100000': 257,
         '000100001': 241,
         '000100010': 66,
         '000100011': 50,
         '000100100': 7,
         '000100101': 6,
         '0000000100': 4545,
         '0000000101': 4529,
         '0000000110': 4513,
         '0000000111': 4497,
         '0000001000': 146,
         '0000001001': 130,
         '0000001010': 114,
         '0000001011': 98,
         '0000001100': 82,
         '0000001101': 51,
         '0000001110': 35,
         '0000001111': 20,
         '0000100000': 9,
         '0000100001': 8,
         '00000000100': 4114,
         '00000000101': 4099,
         '00000000110': 11,
         '00000000111': 10,
         '00000100000': 12,
         '00000100001': 21,
         '00000100010': 369,
         '00000100011': 385,
         '00000100100': 4561,
         '00000100101': 4577,
         '00000100110': 4593,
         '00000100111': 4609,
         '000001010000': 22,
         '000001010001': 36,
         '000001010010': 67,
         '000001010011': 83,
         '000001010100': 99,
         '000001010101': 162,
         '000001010110': 401,
         '000001010111': 417,
         '000001011000': 4625,
         '000001011001': 4641,
         '000001011010': 4657,
         '000001011011': 4673,
         '000001011100': 4689,
         '000001011101': 4705,
         '000001011110': 4721,
         '000001011111': 4737}}

class FormatError(Exception):
    """Not the supported target format; do not create the destination."""


class Damage(Exception):
    """A structurally identified target stream is damaged."""


class Unsupported(FormatError):
    """A known target feature that this implementation cannot decode."""


@dataclass
class Movie:
    fps: Fraction
    has_audio: bool
    auxiliary: int
    declared_video: int
    declared_audio: int
    video: bytes = b""
    audio: bytes = b""
    packets: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    file_size: int = 0
    trailing_header: bytes = b""


def demux(data):
    """Parse the original reader's exact integer expressions, without scanning."""
    if not data.startswith(MAGIC):
        raise FormatError("not Emblaze Video 2: vendor signature does not match")
    if len(data) < 32:
        raise FormatError("vendor signature alone does not establish EV2 version 2")
    if data[28:32] != b"\x02\0\0\0":
        if len(data) > 28 and data[28] >> 4 == 13:
            raise FormatError("Emblaze Audio (EA), not the EV2 video container")
        raise FormatError("vendor-family file without the EV2 version-2 identifier")
    if len(data) < 44:
        raise Damage("confirmed EV2, but its file header is truncated")
    if data[32] not in (0, 1):
        raise Damage("invalid audio-present flag in confirmed EV2")
    fps = Fraction(f"{data[33]}.{data[34]}")
    if fps <= 0:
        raise Damage("invalid zero frame rate in confirmed EV2")
    def total(b):
        return b[0] + 256*b[1] + 65536*b[2] + 4096*b[3]
    m = Movie(fps, bool(data[32]), data[35], total(data[36:40]),
              total(data[40:44]), file_size=len(data))
    streams = [bytearray(), bytearray()]
    pos, stream = 44, 0
    while pos < len(data):
        if len(data)-pos < 4:
            m.trailing_header = data[pos:]
            m.warnings.append(f"truncated packet header at file offset {pos}: "
                              f"{len(data)-pos} of 4 bytes remain")
            break
        h = data[pos:pos+4]
        size = h[0] + 256*h[1] + 4096*h[2] + 65536*(h[3] & 127)
        available = min(size, len(data)-pos-4)
        m.packets.append(dict(offset=pos, stream=stream,
                              stream_offset=len(streams[stream]), declared=size,
                              available=available, keyframe=bool(h[3]&128),
                              header=h.hex()))
        streams[stream] += data[pos+4:pos+4+available]
        pos += 4+available
        if available != size:
            m.warnings.append(f"truncated {'audio' if stream else 'video'} packet "
                              f"at {pos-available-4}: {available}/{size} bytes")
            break
        stream = 1-stream if m.has_audio else 0
    m.video, m.audio = map(bytes, streams)
    for name, actual, declared in [('video',len(m.video),m.declared_video),
                                    ('audio',len(m.audio),m.declared_audio)]:
        if actual != declared:
            m.warnings.append(f"{name} total differs: header {declared}, available {actual}")
    return m


class Bits:
    def __init__(self, data):
        self.s = ''.join(f'{b:08b}' for b in data)
        self.p = 0

    def get(self, n):
        if self.p+n > len(self.s):
            raise Damage(f"truncated video at elementary-stream bit {self.p}")
        value = int(self.s[self.p:self.p+n], 2) if n else 0
        self.p += n
        return value

    def peek(self, n):
        return int((self.s[self.p:self.p+n]+'0'*n)[:n], 2)

    def vlc(self, name):
        code = ''
        for _ in range(13):
            code += str(self.get(1))
            if code in VLC[name]:
                return VLC[name][code]
        raise Damage(f"invalid {name} VLC at elementary-stream bit {self.p-13}")


@dataclass
class Picture:
    timestamp: int
    width: int
    height: int
    mode: int
    flags: int
    quant: int
    suffix: str
    payload: str
    start_bit: int
    end_bit: int
    header_end: int
    macroblocks: int
    recovered: bool = False


def read_picture_header(r):
    start = r.p
    if r.get(22) != 32:
        raise Damage(f"expected picture start code at elementary-stream bit {start}")
    tr, flags, sf = r.get(20), r.get(5), r.get(3)
    if flags >> 3 != 2:
        raise Damage(f"invalid H.263 marker/identifier at bit {start+42}")
    if sf == 4:
        height, width = r.get(13), r.get(13)
    elif sf in (1, 2, 3, 5):
        width, height = {1:(128,96), 2:(176,144), 3:(352,288), 5:(240,176)}[sf]
    else:
        raise Unsupported(f"unsupported source-format code {sf}")
    if not width or not height:
        raise Damage("zero picture dimension")
    mode = r.get(5)
    if mode & 4:
        raise Unsupported("EV2 syntax-based arithmetic coding (SAC) is not implemented")
    if mode & 1:
        raise Unsupported("EV2 PB pictures are not implemented")
    suffix_start = r.p
    quant = r.get(5)
    if not quant:
        raise Damage("zero picture quantizer")
    # The original decoder consumes CPM but has no PSBI field.
    r.get(1)
    while r.get(1):
        r.get(8)
    return Picture(tr,width,height,mode,flags,quant,r.s[suffix_start:r.p],
                   '',start,0,r.p,0)


def read_macroblock(r, pic, counts):
    inter = bool(pic.mode & 16)
    if inter and r.get(1):
        counts['skipped_macroblocks'] += 1
        return True
    code = r.vlc('inter' if inter else 'intra')
    if code == 255:
        counts['stuffing_codes'] += 1
        return False
    mode = code & 7
    if mode == 2 and not (pic.mode & 2):
        raise Damage("four-vector macroblock without advanced prediction")
    counts[f'macroblock_mode_{mode}'] += 1
    intra = mode in (3,4)
    cbpy = r.vlc('cbpy') ^ (15 if intra else 0)
    cbp = cbpy*4 + (code >> 4)
    if mode in (1,4):
        r.get(2)  # DQUANT: -1, -2, +1, +2; the decoder clips to 1..31.
        counts['dquant_codes'] += 1
    if mode in (0,1,2):
        for _ in range(4 if mode == 2 else 1):
            r.vlc('mv')
            r.vlc('mv')
            counts['motion_vectors'] += 1
    for block in range(6):
        if intra:
            dc = r.get(8)
            if dc in (0,128):
                raise Damage(f"reserved intra DC value {dc}")
            counts['intra_dc_values'] += 1
        if not cbp & (1 << (5-block)):
            continue
        index = 1 if intra else 0
        while True:
            value = r.vlc('dct')
            if value == 7167:
                last, run, level = r.get(1), r.get(6), r.get(8)
                if level in (0,128):
                    raise Damage(f"reserved escaped coefficient level {level} "
                                 f"at elementary-stream bit {r.p-8}")
                counts['escaped_coefficients'] += 1
            else:
                last, run = (value >> 12)&1, (value >> 4)&255
                r.get(1)  # sign
                counts['vlc_coefficients'] += 1
            index += run
            if index >= 64:
                raise Damage("coefficient run extends beyond its 8x8 block")
            if last:
                break
            index += 1
    return True


def parse_video(m):
    r, pictures, counts = Bits(m.video), [], Counter()
    last_one = r.s.rfind('1')
    while r.p <= last_one:
        padding_start = r.p
        # H.263 start-code alignment is explicitly zero stuffing, not a search
        # over arbitrary data. A nonzero non-start-code bit is an error.
        while r.peek(22) not in (32,63):
            if r.get(1):
                m.warnings.append(f"invalid inter-picture padding at bit {r.p-1}; "
                                  "stopped at the last recoverable picture")
                counts['unrecoverable_tail_bits'] += len(r.s)-padding_start
                return pictures, dict(counts)
        counts['zero_alignment_bits'] += r.p-padding_start
        if r.peek(22) == 63:
            r.get(22)
            counts['end_of_sequence_bits'] += 22
            if '1' in r.s[r.p:]:
                m.warnings.append("nonzero data follows the end-of-sequence code")
                counts['unrecoverable_tail_bits'] += len(r.s)-r.p
                return pictures, dict(counts)
            break
        header_start = r.p
        try:
            pic = read_picture_header(r)
        except Damage as exc:
            m.warnings.append(str(exc))
            counts['unrecoverable_tail_bits'] += len(r.s)-header_start
            return pictures, dict(counts)
        if pictures and (pic.width,pic.height) != (pictures[0].width,pictures[0].height):
            raise Unsupported("picture dimension changes within a stream are not implemented")
        if pictures and pic.timestamp <= pictures[-1].timestamp:
            # The source field is a modulo-2^20 counter; only an actual wrap is
            # unwrapped. Arbitrary backwards timestamps are reported as damage.
            base = pictures[-1].timestamp // (1 << 20) * (1 << 20)
            pic.timestamp += base
            if pic.timestamp <= pictures[-1].timestamp:
                if (pictures[-1].timestamp % (1<<20)) == (1<<20)-1:
                    pic.timestamp += 1<<20
                else:
                    m.warnings.append("non-increasing picture timestamps; stopped at the previous picture")
                    counts['unrecoverable_tail_bits'] += len(r.s)-header_start
                    return pictures, dict(counts)
        mbw, mbh = (pic.width+15)//16, (pic.height+15)//16
        total, mb = mbw*mbh, 0
        good_end = r.p
        try:
            while mb < total:
                if r.peek(16) == 0:
                    pad = r.p
                    while r.peek(17) != 1:
                        if r.get(1):
                            raise Damage("invalid GOB alignment")
                    counts['gob_alignment_bits'] += r.p-pad
                    r.get(17)
                    gob, gfid, gquant = r.get(5), r.get(2), r.get(5)
                    if not (1 <= gob <= 30 and gob*mbw == mb and gquant):
                        raise Damage(f"invalid or premature GOB header at bit {pad}")
                    counts['gob_headers'] += 1
                if read_macroblock(r,pic,counts):
                    mb += 1
                    good_end = r.p
            pic.payload = r.s[pic.header_end:r.p]
            pic.end_bit, pic.macroblocks = r.p, mb
        except Damage as exc:
            m.warnings.append(f"picture {pic.timestamp}: {exc}; "
                              f"{mb}/{total} complete macroblocks")
            counts['unrecoverable_tail_bits'] += len(r.s)-good_end
            if pictures and (pic.mode & 16) and not (pic.mode & 2):
                # P-picture COD=1 precisely means copy the colocated previous
                # macroblock. Keep every fully decoded MB, replace only damage.
                pic.payload = r.s[pic.header_end:good_end] + '1'*(total-mb)
                pic.end_bit, pic.macroblocks, pic.recovered = good_end, mb, True
                pictures.append(pic)
                counts['concealed_macroblocks'] += total-mb
            return pictures, dict(counts)
        pictures.append(pic)
    counts['terminal_zero_bits'] += len(r.s)-r.p
    return pictures, dict(counts)


def intel_packet(pic):
    """Lossless header adaptation to FFmpeg's Intel H.263 parser.

    The H.263 macroblock syntax and its Annex D motion-vector interpretation
    are unchanged. Coded dimensions come from the intermediary AVI header;
    the Intel decoder ignores the display-size fields, as its source confirms.
    """
    w, h = (pic.width+15)//16*16, (pic.height+15)//16*16
    bits = (f'{32:022b}{pic.timestamp%256:08b}{pic.flags:05b}111'
            f'{pic.mode:05b}110' + '00000' + '00000' + '00001'
            + '0001' + f'{min(w//4-1,511):09b}' + '1'
            + f'{min(h//4,511):09b}' + pic.suffix + pic.payload)
    bits += '0'*(-len(bits)%8)
    return int(bits,2).to_bytes(len(bits)//8,'big')


def riff_chunk(tag, data):
    return tag + struct.pack('<I',len(data)) + data + b'\0'*(len(data)%2)


def riff_list(tag, data):
    return riff_chunk(b'LIST', tag+data)


def write_intermediate(path, pictures, fps):
    w,h = (pictures[0].width+15)//16*16, (pictures[0].height+15)//16*16
    n = len(pictures)
    avih = struct.pack('<14I',round(1000000/fps),0,0,16,n,0,1,0,w,h,0,0,0,0)
    strh = struct.pack('<4s4sIHHIIIIIIIIhhhh',b'vids',b'I263',0,0,0,0,
                       fps.denominator,fps.numerator,0,n,0,0xffffffff,0,0,0,w,h)
    strf = struct.pack('<IiiHH4sIiiII',40,w,h,1,24,b'I263',w*h*3,0,0,0,0)
    hdrl = riff_list(b'hdrl',riff_chunk(b'avih',avih)+riff_list(b'strl',
                     riff_chunk(b'strh',strh)+riff_chunk(b'strf',strf)))
    with open(path,'wb') as out:
        out.write(b'RIFF\0\0\0\0AVI '+hdrl+b'LIST\0\0\0\0movi')
        movi_start = out.tell()-4
        index = bytearray()
        for pic in pictures:
            payload = intel_packet(pic)
            index += struct.pack('<4sIII',b'00dc',0 if pic.mode&16 else 16,
                                 out.tell()-movi_start,len(payload))
            out.write(riff_chunk(b'00dc',payload))
        movi_end = out.tell()
        out.write(riff_chunk(b'idx1',index))
        size = out.tell()
        out.seek(4)
        out.write(struct.pack('<I',size-8))
        out.seek(movi_start-4)
        out.write(struct.pack('<I',movi_end-movi_start))


def checked_run(command):
    result = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors='replace').strip() or
                           f"ffmpeg failed with status {result.returncode}")
    # -v error reports decode errors even where ffmpeg exits successfully.
    if result.stderr.strip():
        raise RuntimeError(result.stderr.decode(errors='replace').strip())


def prepare_audio(m):
    complete = len(m.audio)//33*33
    if complete != len(m.audio):
        m.warnings.append(f"discarded incomplete final GSM frame: {len(m.audio)-complete} bytes")
    frames = []
    # A standard GSM silent frame, used only for explicitly damaged packets.
    silence = bytes.fromhex('d820a2e15a50004924924924500049249249245000492492492450004924924924')
    for offset in range(0,complete,33):
        packet = m.audio[offset:offset+33]
        if packet[0] >> 4 != 13:
            m.warnings.append(f"bad GSM signature at audio byte {offset}; substituted silence")
            packet = silence
        frames.append(packet)
    return b''.join(frames)


def convert(input_path, output_path, audit_path=None):
    input_path, output_path = Path(input_path), Path(output_path)
    if input_path.resolve() == output_path.resolve():
        raise FormatError("input and output paths must be different")
    if audit_path and Path(audit_path).resolve() in (input_path.resolve(),output_path.resolve()):
        raise FormatError("audit path must differ from the input and AVI paths")
    m = demux(input_path.read_bytes())
    pictures, syntax = parse_video(m)
    if not pictures:
        raise Damage("confirmed EV2 but no complete or recoverable picture remains")
    if pictures[0].mode & 16:
        raise Damage("the first recoverable picture is predictive; no reference image exists")
    audio = prepare_audio(m)
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required on PATH (h263i, gsm, ffv1, pcm_s16le support)")
    if not output_path.parent.is_dir():
        raise RuntimeError(f"output directory does not exist: {output_path.parent}")
    w,h = pictures[0].width,pictures[0].height
    cw,ch = (w+15)//16*16,(h+15)//16*16
    frame_size = cw*ch*3//2
    final_frame = pictures[-1].timestamp
    frame_count = final_frame+1
    if frame_count > 20_000_000:
        raise Unsupported("timeline exceeds the converter's 20-million-frame resource limit")
    base = [ffmpeg,'-hide_banner','-v','error','-nostdin']
    # The destination is replaced atomically only after both codecs succeed.
    with tempfile.TemporaryDirectory(prefix='.ev2-',dir=output_path.parent) as tmpdir:
        tmp = Path(tmpdir)
        intermediate, raw, gsm, result = [tmp/name for name in
            ('decode.avi','decoded.yuv','audio.gsm','result.avi')]
        write_intermediate(intermediate,pictures,m.fps)
        checked_run(base+['-i',str(intermediate),'-an','-pix_fmt','yuv420p',
                          '-fps_mode','passthrough','-f','rawvideo','-y',str(raw)])
        if raw.stat().st_size != frame_size*len(pictures):
            raise RuntimeError("decoder frame count does not match the parsed picture count")
        command = base+['-f','rawvideo','-pixel_format','yuv420p','-video_size',
                        f'{cw}x{ch}','-framerate',str(m.fps),'-i','pipe:0']
        if audio:
            gsm.write_bytes(audio)
            command += ['-f','gsm','-i',str(gsm)]
        # EV2 uses bottom-up coded planes. The original player shifts the
        # flipped padded picture upward by the number of padded bottom lines.
        command += ['-map','0:v:0']
        if audio:
            command += ['-map','1:a:0','-c:a','pcm_s16le','-ar','8000','-ac','1']
        command += ['-vf',f'vflip,crop={w}:{h}:0:{ch-h}:exact=1,setsar=1',
                    '-c:v','ffv1','-level','3','-g','1','-pix_fmt','yuv420p',
                    '-color_range','tv','-colorspace','smpte170m',
                    '-f','avi','-y',str(result)]
        with open(tmp/'encode.log','wb+') as error_log, open(raw,'rb') as decoded:
            proc = subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,
                                    stderr=error_log)
            try:
                first = decoded.read(frame_size)
                previous, tick = first, 0
                for index,pic in enumerate(pictures):
                    current = first if index == 0 else decoded.read(frame_size)
                    # Hold the previous decoded picture for omitted timestamps.
                    while tick < pic.timestamp:
                        proc.stdin.write(previous)
                        tick += 1
                    proc.stdin.write(current)
                    tick += 1
                    previous = current
                proc.stdin.close()
                status = proc.wait()
            except BaseException:
                proc.kill()
                proc.wait()
                raise
            error_log.seek(0)
            errors = error_log.read().decode(errors='replace').strip()
            if status or errors:
                raise RuntimeError(errors or f"ffmpeg encoding failed ({status})")
        os.chmod(result,0o664)
        os.replace(result,output_path)
    audit = dict(status='recovered' if m.warnings else 'converted',
                 input_bytes=m.file_size,header_bytes=44,auxiliary_byte=m.auxiliary,
                 fps=str(m.fps),width=w,height=h,coded_width=cw,coded_height=ch,
                 video_bytes=len(m.video),audio_bytes=len(m.audio),
                 declared_video_bytes=m.declared_video,declared_audio_bytes=m.declared_audio,
                 packet_count=len(m.packets),zero_length_packets=sum(p['declared']==0 for p in m.packets),
                 packet_header_bytes=4*len(m.packets),
                 trailing_partial_header=m.trailing_header.hex(),
                 accounted_container_bytes=44+4*len(m.packets)+len(m.video)+len(m.audio)+len(m.trailing_header),
                 encoded_pictures=len(pictures),output_frames=frame_count,
                 held_frames=frame_count-len(pictures),video_seconds=float(Fraction(frame_count,m.fps)),
                 gsm_frames=len(audio)//33,audio_samples=len(audio)//33*160,
                 audio_seconds=len(audio)//33/50,
                 syntax=syntax,warnings=m.warnings,
                 accounted_video_bits=sum(p.end_bit-p.start_bit for p in pictures)
                    + syntax.get('zero_alignment_bits',0)
                    + syntax.get('terminal_zero_bits',0)
                    + syntax.get('end_of_sequence_bits',0)
                    + syntax.get('unrecoverable_tail_bits',0),
                 pictures=[dict(timestamp=p.timestamp,start_bit=p.start_bit,end_bit=p.end_bit,
                                header_end=p.header_end,macroblocks=p.macroblocks,
                                recovered=p.recovered,keyframe=not bool(p.mode&16)) for p in pictures],
                 packets=m.packets)
    if audit_path:
        Path(audit_path).write_text(json.dumps(audit,indent=2)+'\n')
        os.chmod(audit_path,0o664)
    return audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputFile')
    parser.add_argument('outputFile')
    parser.add_argument('--audit',metavar='JSON',help='write a packet and syntax audit after conversion')
    args = parser.parse_args()
    try:
        audit = convert(args.inputFile,args.outputFile,args.audit)
    except (FormatError,Damage,RuntimeError,OSError,ValueError) as exc:
        print(f'emblazeVideo2: {exc}',file=sys.stderr)
        return 1
    for warning in audit['warnings']:
        print(f'emblazeVideo2: warning: {warning}',file=sys.stderr)
    print(f"{args.outputFile}: {audit['width']}x{audit['height']}, "
          f"{audit['output_frames']} frames at {audit['fps']} fps, "
          f"{audit['audio_seconds']:.3f} s audio")
    return 0


if __name__ == '__main__':
    sys.exit(main())
