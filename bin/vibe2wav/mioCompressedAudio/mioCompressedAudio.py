#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode Entis MIO audio. Usage: mioCompressedAudio.py inputFile outputDir [-verbose].

Python 3.9+ and a C++17 compiler (c++, g++, or clang++) are required. The complete
codec source is embedded below, compiled in a temporary directory, and removed
on exit. No downloaded codec, Python package, or companion file is required.

Algorithm attribution: ERISA-Library 1.07e, Copyright (C) 2000-2004 Leshade
Entis, Entis-soft; GARbro's C# port by morkt. This adaptation uses the GNU GPL
option offered by ERISA-Library's license and is distributed under GPL-2.0-or-later,
without warranty. See https://www.gnu.org/licenses/old-licenses/gpl-2.0.html .
"""

import argparse
import ctypes
import io
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
from dataclasses import dataclass, asdict


CODEC_SOURCE = r'''
// Vibe coded by Codex
// SPDX-License-Identifier: GPL-2.0-or-later
// Algorithms: ERISA-Library 1.07e, (C) 2000-2004 Leshade Entis, Entis-soft.
// Consulted also: GARbro's C# port by morkt.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <vector>
using std::vector;
static constexpr double PI = 3.141592653589793238462643383279502884;
static constexpr int ROOT=512, NIL=32768;
static constexpr uint32_t LEAF=0x80000000u, ESC=0x7fffffffu;
static void require(bool b, const char *s) { if (!b) throw std::runtime_error(s); }

struct Bits {
    const uint8_t *data; size_t size, pos=0;
    uint32_t get(int n) {
        require(n>=0 && n<=32, "invalid bit width");
        require(size*8-pos >= size_t(n), "truncated compressed bitstream");
        uint32_t value=0;
        while (n) {
            int take=std::min(n, 8-int(pos&7));
            value=(value<<take) | ((data[pos>>3]>>(8-int(pos&7)-take))&((1u<<take)-1));
            pos+=take; n-=take;
        }
        return value;
    }
    uint32_t gamma() {
        uint32_t value=1;
        while (get(1)) {
            require(value < 0x40000000u, "zero-run length overflow");
            value=(value<<1)|get(1);
        }
        return value;
    }
};

struct Node { uint32_t weight=0; int parent=NIL; uint32_t child=NIL; };
struct Tree {
    std::array<Node,513> nodes{};
    int first=ROOT;
    void recount(int p) {
        require(p>=0 && p<=ROOT && nodes[p].child<ROOT, "invalid Huffman parent");
        int c=nodes[p].child;
        nodes[p].weight=nodes[c].weight+nodes[c+1].weight;
    }
    void relink(int p) {
        if (!(nodes[p].child&LEAF)) {
            int c=nodes[p].child;
            require(c>=0 && c<ROOT, "invalid Huffman child");
            nodes[c].parent=nodes[c+1].parent=p;
        }
    }
    void normalize(int entry) {
        while(entry<ROOT) {
            int swap=entry+1;
            while(swap<ROOT && nodes[swap].weight<nodes[entry].weight) ++swap;
            --swap;
            if(swap!=entry) {
                int pe=nodes[entry].parent, ps=nodes[swap].parent;
                std::swap(nodes[entry],nodes[swap]);
                nodes[entry].parent=pe; nodes[swap].parent=ps;
                relink(entry); relink(swap);
                entry=swap;
            }
            entry=nodes[entry].parent;
            recount(entry);
        }
    }
    void rebuild() {
        int next=ROOT;
        for(int i=ROOT-1;i>=first;--i) if(nodes[i].child&LEAF) {
            nodes[i].weight=(nodes[i].weight+1)>>1;
            nodes[next--]=nodes[i];
        }
        ++next;
        for(int i=first;;i+=2) {
            nodes[i]=nodes[next]; nodes[i+1]=nodes[next+1]; next+=2;
            relink(i); relink(i+1);
            uint32_t weight=nodes[i].weight+nodes[i+1].weight;
            if(next>ROOT) {
                nodes[ROOT]={weight,NIL,uint32_t(i)};
                nodes[i].parent=nodes[i+1].parent=ROOT;
                break;
            }
            int j=next;
            while(j<=ROOT && weight>nodes[j].weight) { nodes[j-1]=nodes[j]; ++j; }
            nodes[j-1].weight=weight; nodes[j-1].child=i;
            --next;
        }
    }
    void add(uint32_t code) {
        if(first==0) {
            int i=nodes[0].child==(LEAF|ESC) ? 1:0;
            nodes[i].child=LEAF|code;
            return;
        }
        first-=2; int i=first;
        nodes[i].weight=1; nodes[i].child=LEAF|code;
        if(nodes[ROOT].child==NIL) {
            nodes[i].parent=ROOT;
            nodes[i+1]={1,ROOT,LEAF|ESC};
            nodes[ROOT]={2,NIL,uint32_t(i)};
        } else {
            nodes[i+1]=nodes[i+2];
            nodes[i+2].weight=1+nodes[i+1].weight;
            nodes[i+2].child=i;
            nodes[i].parent=nodes[i+1].parent=i+2;
            normalize(i+2);
        }
    }
    uint32_t decode(Bits &bits, bool length, uint64_t &rebuilds) {
        if(first!=ROOT) {
            int entry=ROOT;
            do {
                entry=nodes[entry].child+bits.get(1);
                require(entry>=first && entry<=ROOT, "invalid Huffman path");
            } while(!(nodes[entry].child&LEAF));
            uint32_t code=nodes[entry].child&~LEAF;
            ++nodes[entry].weight; normalize(entry);
            if(nodes[ROOT].weight>=0x4000) { rebuild(); ++rebuilds; }
            if(code!=ESC) return code;
        }
        uint32_t code=length ? bits.gamma():bits.get(8);
        add(code);
        return code;
    }
};

struct Entropy {
    vector<Tree> trees;
    int previous=0;
    size_t pending=0;
    uint64_t rebuilds=0;
    void reset() { trees=vector<Tree>(257); previous=0; pending=0; }
    vector<uint8_t> decode(Bits &bits, size_t count, bool initial) {
        if(initial) reset();
        require(!trees.empty(), "continuation packet has no entropy reset");
        vector<uint8_t> result(count,0);
        size_t i=std::min(count,pending); pending-=i;
        while(i<count) {
            uint32_t symbol=trees[previous].decode(bits,false,rebuilds);
            result[i++]=symbol;
            if(symbol==0) {
                size_t length=trees[256].decode(bits,true,rebuilds);
                require(length>0, "zero-length zero run");
                --length;
                size_t used=std::min(length,count-i); i+=used; pending=length-used;
            }
            previous=symbol;
        }
        return result;
    }
};

struct Trig { float s,c; };
struct Matrix {
    int degree,n;
    vector<Trig> rotations;
    vector<float> cosines[13];
    float cp4=float(std::cos(PI/4)), cp4x2=2*cp4;
    explicit Matrix(int d):degree(d),n(1<<d) {
        for(int k=1;k<13;++k) {
            int m=1<<k; double angle=PI/(4*m),step=2*angle;
            cosines[k].resize(m);
            for(int i=0;i<m;++i,angle+=step) cosines[k][i]=float(std::cos(angle));
        }
        double k=PI/(2*n);
        for(int step=2;step<n;step*=8) {
            size_t base=rotations.size();
            for(int i=0;i<7;++i) {
                double ws=1,a=0;
                for(int j=0;j<i;++j) {
                    a+=step;
                    ws=ws*rotations[base+j].s+rotations[base+j].c*std::cos(a*k);
                }
                double r=std::atan2(ws,std::cos((a+step)*k));
                rotations.push_back({float(std::sin(r)),float(std::cos(r))});
            }
        }
    }
    void odd(float *x) const {
        int index=1,step=2,lc=(n/2)/8,base=0;
        for(;;) {
            base+=7; index+=step*7; step*=8;
            if(lc<=8) break;
            lc/=8;
        }
        auto rotate=[&](int k,int j) {
            float a=x[k],b=x[k+step]; const Trig &t=rotations[base+j];
            x[k]=a*t.c+b*t.s; x[k+step]=b*t.c-a*t.s;
        };
        for(int j=lc-2,k=index+step*(lc-2);j>=0;--j,k-=step) rotate(k,j);
        for(;lc<=(n/2)/8;lc*=8) {
            base-=7; step/=8; index-=step*7;
            for(int i=0;i<lc;++i)
                for(int j=6,k=i*step*8+index+step*6;j>=0;--j,k-=step) rotate(k,j);
        }
    }
    void dct(float *dst,int stride,float *src,float *work,int d) const {
        if(d==2) {
            float a=src[0]+src[3], b=src[1]+src[2];
            float c=cosines[1][0]*(src[0]-src[3]);
            float e=cosines[1][1]*(src[1]-src[2]);
            dst[0]=0.5f*(a+b); dst[2*stride]=cp4*(a-b);
            dst[stride]=c+e; dst[3*stride]=cp4x2*(c-e)-dst[stride];
            return;
        }
        int width=1<<d,h=width/2;
        for(int i=0;i<h;++i) { work[i]=src[i]+src[width-1-i]; work[h+i]=src[i]-src[width-1-i]; }
        dct(dst,stride*2,work,src,d-1);
        for(int i=0;i<h;++i) work[h+i]*=cosines[d-1][i];
        dct(dst+stride,stride*2,work+h,work,d-1);
        for(int i=0;i<h;++i) dst[(2*i+1)*stride]+=dst[(2*i+1)*stride];
        for(int i=1;i<h;++i) dst[(2*i+1)*stride]-=dst[(2*i-1)*stride];
    }
    void idct(float *dst,const float *src,int stride,float *work,int d) const {
        if(d==2) {
            float a=src[0], b=cp4*src[stride*2];
            float c=cosines[1][0]*src[stride],e=cosines[1][1]*src[stride*3];
            float f=c+e,g=cp4x2*(c-e)-f;
            dst[0]=(a+b)+f; dst[3]=(a+b)-f;
            dst[1]=(a-b)+g; dst[2]=(a-b)-g;
            return;
        }
        int width=1<<d,h=width/2;
        idct(dst,src,stride*2,work,d-1);
        for(int i=0;i<h;++i) work[i]=src[(2*i+1)*stride]*cosines[d-1][i];
        dct(dst+h,1,work,work+h,d-1);
        for(int i=0;i<h;++i) dst[h+i]+=dst[h+i];
        for(int i=1;i<h;++i) dst[h+i]-=dst[h+i-1];
        for(int i=0;i<h/2;++i) {
            float a=dst[i]+dst[h+i],b=dst[i]-dst[h+i];
            float c=dst[h-1-i]+dst[width-1-i],e=dst[h-1-i]-dst[width-1-i];
            dst[i]=a; dst[h-1-i]=c; dst[h+i]=e; dst[width-1-i]=b;
        }
    }
    vector<float> dequant(const int16_t *q, bool half,uint32_t weight,uint32_t coefficient) const {
        static const int shifts[7]={-6,-6,-5,-4,-3,-2,-1};
        int points[7],end=0;
        double ratios[7];
        for(int i=0;i<7;++i) {
            int width=1<<(degree+shifts[i]); points[i]=end+width/2; end+=width;
            ratios[i]=i==6 ? 1.0:1.0/std::pow(2.0,(int((weight>>(i*5))&31)-15)*0.5);
        }
        vector<float> weights(n),result(n);
        int i=0;
        while(i<points[0]) weights[i++]=float(ratios[0]);
        for(int j=1;j<7;++j) {
            double a=ratios[j-1],k=(ratios[j]-a)/(points[j]-points[j-1]);
            while(i<points[j]) { weights[i]=float(k*(i-points[j-1])+a); ++i; }
        }
        while(i<n) weights[i++]=1.0f;
        float oddweight=float(((weight>>30)+2)/2.0);
        for(int k=15;k<n;k+=16) weights[k]*=oddweight;
        weights[n-1]=float(coefficient);
        double scale=std::sqrt(2.0/n)*coefficient;
        for(int k=0;k<n;++k) {
            int v=half ? ((k&1) ? q[k/2]:0):q[k];
            if(coefficient==0 && k==n-1) result[k]=float(std::sqrt(2.0/n)*v);
            else { float reciprocal=1.0f/weights[k]; result[k]=float(scale*reciprocal*v); }
        }
        return result;
    }
};

struct Operation { int channel,degree,kind,rotation; uint32_t weight,coefficient; };
// kind: 0 = leading half block, 1 = internal block, 2 = trailing half block.
struct Statistics {
    uint64_t side_bits,entropy_bits,padding_bits,nonzero_padding,extra_bytes,missing_padding_bits;
    uint64_t divisions[4],operations[3],rebuilds,coefficients,zero_run_pending;
    uint64_t reserved_weights,zero_quantizers;
};
struct Decoder {
    Entropy entropy;
    vector<Matrix> matrices;
    Decoder() { for(int d=6;d<=12;++d) matrices.emplace_back(d); }
    void packet(const uint8_t *data,size_t size,int channels,int degree,int transform,int samplebits,
                uint32_t frames,bool initial,uint8_t *output,Statistics &stats) {
        Bits bits{data,size};
        size_t count=size_t(frames)*channels;
        if(transform==0x03020000) {
            auto raw=entropy.decode(bits,count*(samplebits/8),initial);
            for(int ch=0;ch<channels;++ch) {
                uint16_t value=0,delta=0;
                for(uint32_t i=0;i<frames;++i) {
                    if(samplebits==8) {
                        value=uint8_t(value+raw[size_t(ch)*frames+i]);
                        output[size_t(i)*channels+ch]=uint8_t(value);
                    } else {
                        size_t p=size_t(ch)*frames*2+i;
                        uint8_t lo=raw[p+frames],hi=raw[p]^(lo>=128 ? 255:0);
                        delta=uint16_t(delta+(uint16_t(hi)<<8)+lo); value=uint16_t(value+delta);
                        size_t o=(size_t(i)*channels+ch)*2;
                        output[o]=value&255; output[o+1]=value>>8;
                    }
                }
            }
        } else {
            require(bits.get(1)==0,"nonzero first reserved audio bit");
            bool mss=transform==0x105 && channels==2;
            int groups=mss ? 1:channels, n=1<<degree;
            size_t sets=(size_t(frames)+n-1)/n,all=sets*n*channels;
            vector<Operation> ops;
            int last[2]={-1,-1};
            auto append=[&](int ch,int d,int kind) {
                int rotation=mss ? int(bits.get(kind==1 ? 4:2)):0;
                uint32_t weight=bits.get(32),coefficient=bits.get(16);
                stats.reserved_weights+=(weight>>30)==3;
                stats.zero_quantizers+=coefficient==0;
                ops.push_back({ch,d,kind,rotation,weight,coefficient});
                ++stats.operations[kind];
            };
            for(size_t i=0;i<sets;++i) for(int ch=0;ch<groups;++ch) {
                int division=bits.get(2); ++stats.divisions[division];
                require(division<=2,"reserved transform division code 3");
                bool lead=last[ch]!=division;
                if(lead && i) append(ch,degree-last[ch],2);
                last[ch]=division;
                for(int k=0;k<(1<<division);++k) append(ch,degree-division,lead && k==0 ? 0:1);
            }
            if(sets) for(int ch=0;ch<groups;++ch) append(ch,degree-last[ch],2);
            require(bits.get(1)==0,"nonzero second reserved audio bit");
            stats.side_bits=bits.pos;
            auto raw=entropy.decode(bits,all*2,initial);
            vector<int16_t> quantum(all);
            size_t row=mss ? n*2:n,rows=all/row;
            for(size_t x=0;x<row;++x) for(size_t y=0;y<rows;++y) {
                size_t p=x*rows+y;
                uint8_t lo=raw[all+p],hi=raw[p]^(lo>=128 ? 255:0);
                quantum[y*row+x]=int16_t((uint16_t(hi)<<8)|lo);
            }
            size_t source=0,written[2]={0,0};
            vector<float> lap[2];
            for(const Operation &op:ops) {
                int width=1<<op.degree,nch=mss ? 2:1;
                Matrix &mat=matrices[op.degree-6];
                vector<float> x[2];
                for(int ch=0;ch<nch;++ch) {
                    size_t take=op.kind==1 ? width:width/2;
                    require(source+take<=all,"coefficient array overrun");
                    x[ch]=mat.dequant(quantum.data()+source,op.kind!=1,op.weight,op.coefficient);
                    source+=take;
                }
                if(mss) for(int k=0;k<width;++k) {
                    int angle=op.kind==1 ? ((k&1) ? op.rotation&3:op.rotation>>2):op.rotation;
                    float s=float(std::sin(angle*PI/8)),c=float(std::cos(angle*PI/8));
                    float a=x[0][k],b=x[1][k];
                    x[0][k]=a*c-b*s; x[1][k]=a*s+b*c;
                }
                for(int ch=0;ch<nch;++ch) {
                    int channel=mss ? ch:op.channel;
                    auto &v=x[ch]; mat.odd(v.data());
                    if(op.kind!=1) for(int i=0;i<width;i+=2) v[i]=op.kind==0 ? v[i+1]:-v[i+1];
                    for(int i=0;i<width;i+=2) {
                        float a=v[i],b=v[i+1]; v[i]=0.5f*(a+b); v[i+1]=0.5f*(a-b);
                    }
                    if(op.kind==0) { lap[channel]=std::move(v); continue; }
                    require(lap[channel].size()==size_t(width),"missing LOT overlap state");
                    vector<float> combined(width),pcm(width),work(width);
                    for(int i=0;i<width;i+=2) {
                        float a=lap[channel][i],b=v[i+1]; combined[i]=a+b; combined[i+1]=a-b;
                    }
                    if(op.kind==1) lap[channel]=std::move(v);
                    mat.idct(pcm.data(),combined.data(),1,work.data(),op.degree);
                    size_t emit=std::min(size_t(width),size_t(frames)-written[channel]);
                    for(size_t i=0;i<emit;++i) {
                        require(std::isfinite(pcm[i]),"nonfinite reconstructed sample");
                        double r=pcm[i]>=0 ? std::floor(double(pcm[i])+0.5):std::ceil(double(pcm[i])-0.5);
                        int value=int(std::max(-32768.0,std::min(32767.0,r)));
                        size_t p=((written[channel]+i)*channels+channel)*2;
                        output[p]=value&255; output[p+1]=(uint32_t(value)>>8)&255;
                    }
                    written[channel]+=emit;
                }
            }
            require(source==all,"coefficient count mismatch");
            for(int ch=0;ch<channels;++ch) require(written[ch]==frames,"decoded frame count mismatch");
            stats.coefficients=all;
        }
        stats.entropy_bits=bits.pos-stats.side_bits;
        size_t expected_padding=(-bits.pos)&31;
        size_t available=size*8-bits.pos;
        stats.padding_bits=std::min(available,expected_padding);
        stats.missing_padding_bits=expected_padding-stats.padding_bits;
        for(size_t i=0;i<stats.padding_bits;++i) stats.nonzero_padding+=bits.get(1)!=0;
        stats.extra_bytes=(size*8-bits.pos)/8;
        // Extra bytes and nonzero pad bits are reported as damage, never silently unaccounted.
        stats.rebuilds=entropy.rebuilds;
        stats.zero_run_pending=entropy.pending;
    }
};
extern "C" {
void *mio_new() { try { return new Decoder; } catch(...) { return nullptr; } }
void mio_free(void *p) { delete static_cast<Decoder*>(p); }
int mio_packet(void *p,const uint8_t *data,size_t size,int channels,int degree,int transform,int samplebits,
               uint32_t frames,int initial,uint8_t *output,Statistics *stats,char *error,size_t error_size) {
    try {
        *stats={};
        static_cast<Decoder*>(p)->packet(data,size,channels,degree,transform,samplebits,frames,initial,output,*stats);
        return 0;
    } catch(const std::exception &e) {
        std::snprintf(error,error_size,"%s",e.what()); return 1;
    } catch(...) { std::snprintf(error,error_size,"unknown native decoder error"); return 1; }
}
}
'''


class MioError(Exception):
    """Recognized but damaged input, or a conversion/environment failure."""


class Unsupported(MioError):
    """Input is outside the explicitly implemented format profile."""


@dataclass
class SoundInfo:
    version: int
    transformation: int
    architecture: int
    channels: int
    sample_rate: int
    blockset_count: int
    subband_degree: int
    sample_count: int
    lapped_degree: int
    bits_per_sample: int


@dataclass
class Packet:
    offset: int
    length: int
    version: int
    flags: int
    reserved: int
    frames: int
    truncated: bool = False


class Container:
    def __init__(self, data):
        self.data = data
        self.regions = []
        self.issues = []
        self.packets = []
        self.text = {}
        self.info = None
        self.file_header = None
        self.parse()

    def region(self, start, end, kind):
        self.regions.append({"offset": start, "length": end-start, "kind": kind})

    def records(self, start, end, context):
        while start < end:
            if end-start < 16:
                self.region(start, end, "truncated record header")
                self.issues.append(f"Truncated {context} record header at 0x{start:x}")
                return
            tag, length = struct.unpack_from("<8sQ", self.data, start)
            body = start+16
            actual_end = min(body+length, end)
            truncated = body+length > end
            self.region(start, body, f"{context}/{tag.decode('ascii', 'replace')} record header")
            if truncated:
                self.issues.append(f"{tag!r} at 0x{start:x} extends {body+length-end} bytes past its available parent")
            yield tag, body, actual_end, truncated
            start = actual_end

    def parse(self):
        data = self.data
        if len(data) < 64 or data[:8] != b"Entis\x1a\0\0" or struct.unpack_from("<I", data, 8)[0] != 0x03000100:
            raise Unsupported("Not an Entis MIO container (64-byte header/signature/file ID)")
        name = data[16:64].split(b"\0", 1)[0]
        if name != b"Music Interleaved and Orthogonal transformed":
            raise Unsupported("Entis container does not declare the MIO audio format")
        self.region(0, 64, "EMC signature, file ID, reserved word, and zero-padded format name")
        if struct.unpack_from("<I", data, 12)[0] or any(data[16+len(name):64]):
            self.issues.append("Nonzero reserved file-header bytes")
        seen_header = seen_stream = False
        for tag, start, end, truncated in self.records(64, len(data), "root"):
            if tag == b"Header  ":
                if seen_header or seen_stream:
                    raise Unsupported("Multiple or out-of-order Header records")
                seen_header = True
                first_record = True
                for subtag, a, b, cut in self.records(start, end, "Header"):
                    payload = data[a:b]
                    if first_record and subtag != b"FileHdr ":
                        raise Unsupported("Header must begin with FileHdr")
                    first_record = False
                    if subtag == b"FileHdr ":
                        if self.file_header is not None or len(payload) != 20:
                            raise Unsupported("FileHdr must occur once with its 20-byte layout")
                        self.file_header = struct.unpack("<5I", payload)
                        version, contains, keyframes, frames, duration = self.file_header
                        if version != 0x20100 or contains != 0x100 or frames != 0:
                            raise Unsupported("Unsupported FileHdr version or non-audio/mixed media content")
                        self.region(a, b, "FileHdr: version, content flags, keyframe interval, image count, duration in ms")
                    elif subtag == b"SoundInf":
                        if self.info is not None or len(payload) != 40:
                            raise Unsupported("SoundInf must occur once with its 40-byte layout")
                        self.info = SoundInfo(*struct.unpack("<10I", payload))
                        self.region(a, b, "SoundInf: ten unsigned little-endian 32-bit fields")
                    elif subtag in (b"cpyright", b"descript"):
                        encoding = "utf-16" if payload[:2] in (b"\xff\xfe", b"\xfe\xff") else "cp932"
                        self.text[subtag.decode()] = payload.decode(encoding, errors="replace").rstrip("\0")
                        self.region(a, b, f"{subtag.decode()} text ({encoding})")
                    else:
                        raise Unsupported(f"Unsupported Header record {subtag!r} at 0x{a-16:x}")
            elif tag == b"Stream  ":
                if not seen_header or seen_stream:
                    raise Unsupported("Missing Header or multiple Stream records")
                seen_stream = True
                for subtag, a, b, cut in self.records(start, end, "Stream"):
                    if subtag != b"SoundStm":
                        raise Unsupported(f"Unsupported Stream record {subtag!r} at 0x{a-16:x}")
                    if b-a < 8:
                        self.region(a, b, "truncated SoundStm header")
                        self.issues.append(f"Incomplete SoundStm header at 0x{a:x}; skipped")
                        continue
                    version, flags, reserved, frames = struct.unpack_from("<BBHI", data, a)
                    if version != 1 or flags & ~1:
                        raise Unsupported(f"Unsupported SoundStm version/flags at 0x{a:x}: {version}/{flags:#x}")
                    if reserved:
                        self.issues.append(f"Nonzero SoundStm reserved word at 0x{a+2:x}")
                    self.region(a, a+8, "SoundStm: version, lead flag, reserved word, frame count")
                    self.region(a+8, b, "compressed audio bitstream and final 32-bit word padding")
                    self.packets.append(Packet(a+8, b-a-8, version, flags, reserved, frames, cut))
            else:
                raise Unsupported(f"Unsupported top-level record {tag!r} at 0x{start-16:x}")
        if self.info is None or self.file_header is None or not seen_stream:
            raise MioError("MIO is missing the required FileHdr, SoundInf, or Stream record")
        self.validate_info()
        # Disjoint interval accounting checks every byte, including malformed tails.
        cursor = 0
        for region in sorted(self.regions, key=lambda r: r["offset"]):
            if region["offset"] != cursor:
                raise MioError(f"Internal byte accounting error at 0x{cursor:x}")
            cursor += region["length"]
        if cursor != len(data):
            raise MioError("Internal byte accounting does not reach EOF")
        self.accounted_bytes = cursor
        total = sum(p.frames for p in self.packets)
        if total != self.info.sample_count:
            self.issues.append(f"SoundInf declares {self.info.sample_count} frames; packet headers declare {total}; packet lengths take precedence")

    def validate_info(self):
        s = self.info
        if s.version != 0x20300:
            raise Unsupported(f"Unsupported SoundInf revision {s.version:#x}; implemented revision is 0x20300")
        if s.channels not in (1, 2):
            raise Unsupported(f"Unsupported channel count {s.channels}")
        if not 1 <= s.sample_rate <= 0xffffffff//(s.channels*max(1, s.bits_per_sample//8)):
            raise MioError("Invalid PCM sample rate")
        if s.blockset_count:
            raise Unsupported("Nonzero blockset_count is not defined by this MIO revision")
        if s.transformation == 0x03020000:
            if s.architecture != 0xfffffffc or s.bits_per_sample not in (8, 16):
                raise Unsupported("Lossless MIO requires adaptive Huffman coding and 8/16-bit PCM")
        elif s.transformation in (5, 0x105):
            if s.architecture not in (0xffffffff, 0xfffffffc):
                raise Unsupported(f"Unsupported MIO entropy architecture {s.architecture:#x}; ERISA arithmetic/Nemesis is not implemented")
            if s.bits_per_sample != 16 or not 8 <= s.subband_degree <= 12 or s.lapped_degree != 1:
                raise Unsupported("LOT MIO requires 16-bit PCM, subband degree 8..12, and lapped degree 1")
        else:
            raise Unsupported(f"Unsupported MIO transformation {s.transformation:#x}")


class Statistics(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint64) for name in
                ("side_bits", "entropy_bits", "padding_bits", "nonzero_padding", "extra_bytes", "missing_padding_bits")]
    _fields_ += [("divisions", ctypes.c_uint64*4), ("operations", ctypes.c_uint64*3)]
    _fields_ += [(name, ctypes.c_uint64) for name in ("rebuilds", "coefficients", "zero_run_pending")]
    _fields_ += [(name, ctypes.c_uint64) for name in ("reserved_weights", "zero_quantizers")]

    def dictionary(self):
        return {name: list(getattr(self, name)) if name in ("divisions", "operations") else getattr(self, name)
                for name, _ in self._fields_}


class Codec:
    """A reusable in-process decoder; compilation happens once per Codec instance."""
    def __init__(self):
        compiler = next((shutil.which(c) for c in ("c++", "g++", "clang++") if shutil.which(c)), None)
        if not compiler:
            raise MioError("A C++17 compiler is required: install g++ or clang++")
        if sys.platform not in ("linux", "darwin"):
            raise MioError("This embedded native-code loader currently supports Linux and macOS")
        self.temp = tempfile.TemporaryDirectory(prefix="mio-codec-")
        Path(self.temp.name).chmod(0o750)
        source = Path(self.temp.name)/"codec.cpp"
        library = Path(self.temp.name)/("codec.dylib" if sys.platform == "darwin" else "codec.so")
        source.write_text(CODEC_SOURCE, encoding="utf-8")
        source.chmod(0o644)
        cmd = [compiler, "-std=c++17", "-O2", "-fPIC", "-ffp-contract=off",
               "-dynamiclib" if sys.platform == "darwin" else "-shared", str(source), "-o", str(library)]
        build = subprocess.run(cmd, capture_output=True, text=True)
        if build.returncode:
            self.temp.cleanup()
            raise MioError("Unable to compile embedded MIO codec:\n"+build.stderr)
        library.chmod(0o755)
        self.lib = ctypes.CDLL(str(library))
        self.lib.mio_new.argtypes = []
        self.lib.mio_new.restype = ctypes.c_void_p
        self.lib.mio_free.argtypes = [ctypes.c_void_p]
        self.lib.mio_free.restype = None
        self.lib.mio_packet.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32,
            ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(Statistics), ctypes.c_void_p, ctypes.c_size_t]
        self.lib.mio_packet.restype = ctypes.c_int

    def close(self):
        self.temp.cleanup()

    def decode(self, container):
        info = container.info
        context = self.lib.mio_new()
        if not context:
            raise MioError("Cannot allocate MIO decoder")
        output = io.BytesIO()
        audit = []
        synchronized = False
        good_packets = 0
        try:
            for index, packet in enumerate(container.packets):
                item = {"index": index, **asdict(packet)}
                audit.append(item)
                if packet.flags & 1:
                    synchronized = True
                if not synchronized:
                    item["error"] = "No valid lead/reset packet precedes this continuation"
                    container.issues.append(f"Packet {index}: {item['error']}; skipped")
                    continue
                size = packet.frames*info.channels*(info.bits_per_sample//8)
                # Fixed resource ceilings are explicit safety limits, not format guesses.
                if size > 256*1024*1024 or output.tell()+size > 0xffffffff-36:
                    raise MioError("PCM exceeds the 256 MiB per-packet or RIFF 4 GiB output limit")
                pcm = ctypes.create_string_buffer(size)
                compressed = container.data[packet.offset:packet.offset+packet.length]
                stats = Statistics()
                error = ctypes.create_string_buffer(512)
                status = self.lib.mio_packet(context, compressed, len(compressed), info.channels,
                    info.subband_degree, info.transformation, info.bits_per_sample, packet.frames,
                    bool(packet.flags & 1), pcm, ctypes.byref(stats), error, len(error))
                item.update(stats.dictionary())
                if status:
                    item["error"] = error.value.decode("utf-8", "replace")
                    container.issues.append(f"Packet {index}: {item['error']}; skipped")
                    synchronized = False
                    continue
                for key, label in (("nonzero_padding", "nonzero padding bits"), ("extra_bytes", "unexpected bytes after padding"),
                                   ("missing_padding_bits", "missing padding bits"), ("reserved_weights", "reserved weight values"),
                                   ("zero_quantizers", "zero overall quantizers (continuous inverse limit used)")):
                    if item[key]:
                        container.issues.append(f"Packet {index}: {item[key]} {label}; audio retained")
                output.write(pcm.raw)
                good_packets += 1
                item["decoded_frames"] = packet.frames
        finally:
            self.lib.mio_free(context)
        if not good_packets and container.packets:
            raise MioError("No audio packets could be recovered; " + "; ".join(container.issues[:4]))
        if output.tell() == 0 and (info.sample_count or any(p.frames for p in container.packets)):
            raise MioError("No nonempty audio could be recovered; " + "; ".join(container.issues[:4]))
        return output.getvalue(), audit


def convert(input_file, output_dir, verbose=False, codec=None):
    input_file, output_dir = Path(input_file), Path(output_dir)
    container = Container(input_file.read_bytes())
    own_codec = codec is None
    if own_codec:
        codec = Codec()
    try:
        pcm, packets = codec.decode(container)
    finally:
        if own_codec:
            codec.close()
    # Everything is parsed/decoded before creating any output path.
    output = output_dir/(input_file.stem+".wav")
    if input_file.resolve() == output.resolve():
        raise MioError("The WAV output path would overwrite the input")
    wav = io.BytesIO()
    info = container.info
    with wave.open(wav, "wb") as writer:
        writer.setnchannels(info.channels)
        writer.setsampwidth(info.bits_per_sample//8)
        writer.setframerate(info.sample_rate)
        writer.writeframes(pcm)
    missing_dirs = []
    directory = output_dir
    while not directory.exists():
        missing_dirs.append(directory)
        directory = directory.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    for directory in missing_dirs:
        directory.chmod(directory.stat().st_mode | 0o550)
    output.write_bytes(wav.getvalue())
    output.chmod(output.stat().st_mode | 0o440)
    result = {"input": str(input_file), "output": str(output), "input_bytes": len(container.data),
              "accounted_bytes": container.accounted_bytes, "info": asdict(info),
              "decoded_frames": len(pcm)//(info.channels*(info.bits_per_sample//8)),
              "file_header": dict(zip(("version", "contained_flags", "keyframe_interval", "image_frame_count", "duration_ms"), container.file_header)),
              "issues": container.issues, "text": container.text, "regions": container.regions, "packets": packets}
    if verbose:
        metadata = output_dir/(input_file.stem+".mio.json")
        metadata.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
        metadata.chmod(metadata.stat().st_mode | 0o440)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Convert Entis MIO audio to PCM WAV; requires a C++17 compiler.")
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    parser.add_argument("-verbose", "--verbose", action="store_true", help="also write a byte/bit accounting JSON report")
    args = parser.parse_args(argv)
    try:
        result = convert(args.inputFile, args.outputDir, args.verbose)
    except (MioError, OSError, ValueError, struct.error, MemoryError) as exc:
        print(f"mioCompressedAudio: {exc}", file=sys.stderr)
        return 1
    for issue in result["issues"]:
        print(f"Warning: {issue}", file=sys.stderr)
    print(f"{result['output']} ({result['decoded_frames']} frames)")
    return 2 if result["issues"] else 0


if __name__ == "__main__":
    sys.exit(main())
