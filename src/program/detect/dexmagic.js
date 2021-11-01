import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

const DEXMAGIC_CHECKS =
{
	// archive
	"pcxLib compressed"   : [{offset : 0, match : "pcxLib"}, {offset : 10, match : "Copyright (c) Genus Microprogramming, Inc."}],
	"TTW Compressed File" : [{offset : 0, match : "TTW!"}, {offset : 8, match : [0x00]}, {offset : 12, match : [0x01]}],

	// image
	"CAD/Draw TVG"             : "TommySoftware TVG",
	"Second Nature Slide Show" : "Second Nature Software\r\nSlide Show\r\nCollection",

	// unsupported
	"Amiga Action Reply 3 Freeze File" : [{offset : 0, match : [0x41, 0x52, 0x50, 0x33, 0x00]}, {offset : 8, match : [0x00]}, {offset : 12, match : [0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00]}, {offset : 22, match : Array(10).fill(0x00)}]
};
/*

# IFF LIST packed
0	string/b	LIST
>8	string/b	SSETPROP	IFF LIST file

# IFF FORMs
0	string/b	FORM
>8	string/b	MLDFBMHD	MLDF BMHD file

# IFF VAXL
0	string/b	FORM
>8	string/b	VAXL	IFF VAXL file

# IFF SDBG
0	string/b	FORM
>8	string/b	SDBG	IFF SDBG file

# IFF DMCS
0	string/b	FORM
>8	string/b	DMCS	IFF Deluxe Music Score

# IFF FRAY
0	string/b	FORM
>8	string/b	FRAY	IFF Cinema 4D file

# AMOS Memory Bank (Tracker )
0		string/b	AmBk	AMOS Memory Bank
>12		string/b	Tracker\ 	\b, Tracker format
>12		string/b	Data\ \ \ \ 	\b, Data format

# RIFF types
0		string/b	RIFF
>8		string/b	MSFX	RIFF MSFX file
>8		string/b	MIDS	RIFF MIDS file
>8		string/b	STYL	RIFF STYL file
>8		string/b	ANIM	RIFF ANIM file
>8		string/b	MxSt	RIFF MxSt file

# RIFX
0		string/b	RIFX
>8		string/b	MV93	RIFX MV93 file

# Lingo Script
0	string/b	\x04\x11\x71\x50\x00\x00\x00\x01\x00\x00	Lingo Script

# NAPLPS Image
0	string/b	\x0C\x0E\x20\x4C\x6F\x21\x48\x40\x40\x49\x3E\x40\x3C\x40\x40\x40\x3E	NAPLPS Image

# Picasso 64 Image
0   string/b    \x00\x18    Picasso 64 Image

# Saracen Paint Image
0   string/b    \x00\x78    Saracen Paint Image

# WAD2
0	string/b	WAD2	WAD2 file

# multiArtist
0   string/b    \x4D\x47\x48\x01	multiArtist

# Paintworks
54	string/b	ANvisionA	Paintworks

# Turbo Rascal Syntax Error
0	string/b	FLUFF64	Turbo Rascal Syntax Error

# Funny Paint
0	string/b	\x00\x0a\xcf\xe2	Funny Paint

# Fullscreen Construction Kit
0	string/b	KD	Fullscreen Construction Kit

# PMG Designer
0	string/b	\xF0\xED\xE4	PMG Designer

# XLD4 Data Document
21	string/b	XLD4\ GRAPHIC\ DATA\ \ DOCUMENT	XLD4 Data Document

# ArtMaster 88
0	string/b	SS\x5FSIF	ArtMaster88

# ZX Spectrum BSP
0	string/b	bsp\xC0	ZX Spectrum BSP

# ZX Spectrum CHR
0	string/b	chr\x24	ZX Spectrum CHR

# CharPad
0	string/b	CTM\x05	CharPad

# Apple IIGS Preferred Format
2	string/b	\x00\x00\x04MAIN	Apple IIGS Preferred Format

# imageUSB
0	string/b	i\x00m\x00a\x00g\x00e\x00U\x00S\x00B	imageUSB

# Alias PIX
4	string/b	\x00\x00\x00\x00\x00\x18	Alis PIX

# OLB Library
0	string/b	Gnu\ is\ Not\ eUnuchs\x2E\x0A\x5F\x5F\x2ESYMDEF	OLB Library

# Atari GEM OBM File
0	string/b	\x00\x01\x00\x22\x00\x00
>17	string/b	\x00\x00\x00\x00\x00
>34	string/b	\x00
>36	string/b	\x00
>38	string/b	\x00\x02
>53	string/b	\x00\x00\x00\x00\x00	Atari GEM OBM File

# Calamus Document
0	string/b	DMC\ CALAMUS\ 
>13	string/b	CDK	Calamus Document

# Kyss KYG
0	string/b	KYGformat\ ver.	Kyss KYG

# PageStream Document
0	string/b	\x07\x23\x19\x92\x00\x0D\x02\x00\x00	PageStream Document

# FM-TownsOS EXP
0	string/b	P3	FM-TownsOS EXP P3
0	string/b	MP	FM-TownsOS EXP MP

# MacWrite
0	string/b	\x00\x06\x00
>4	string/b	\x00\x02\x00\x02	MacWrite Document
>4	string/b	\x00\x06\x00\x02	MacWrite Document

# GNU Info
0	string/b	This\ is\ Info\ file	GNU Info

# VideoTracker
0	string/b	PVC!	VideoTracker Routine

# Director STXT
0	string/b	\x00\x00\x00\x0C\x00\x00	Director STXT

# MediaPaq DCF
0	string/b	EKIF	MediaPaq DCF

# SCR Package
0	string/b	This\ is\ SCR\ Package\ File	SCR Package

# VCD Entries File
0	string/b	ENTRYVCD	VCD Entries File

# VCD Info File
0	string/b	VIDEO_CD	VCD Info File

# PCBoard Programming Language Executable
0	string/b	PCBoard\ Programming\ Language\ Executable	PCBoard Programming Language Executable

# Wildcat WCX
0	string/b	GHSH	Wildcat WCX

# Atari CTB File
0	string/b	GSP22-CTB	Atari CTB File

*/
Object.mapInPlace(DEXMAGIC_CHECKS, (k, v) => (typeof v==="string" ? ([k, [{offset : 0, match : v}]]) : [k, v]));
Object.values(DEXMAGIC_CHECKS).flat().forEach(check =>
{
	if(typeof check.match==="string")
		check.match = (new TextEncoder()).encode(check.match);
});
const DEXMAGIC_BYTES_MAX = Object.values(DEXMAGIC_CHECKS).flat().map(check => (check.offset+check.match.length)).max();

export class dexmagic extends Program
{
	website = "https://github.com/Sembiance/dexvert/tree/master/src/program/detect/dexmagic.js";
	loc = "local";

	exec = async r =>
	{
		r.meta.detections = [];

		const f = await Deno.open(r.input.primary.absolute);
		const buf = new Uint8Array(DEXMAGIC_BYTES_MAX);
		await Deno.read(f.rid, buf);
		Deno.close(f.rid);
		
		for(const [matchid, checks] of Object.entries(DEXMAGIC_CHECKS))
		{
			let match=true;
			for(const check of checks)
			{
				for(let loc=check.offset, i=0;i<check.match.length;loc++, i++)
				{
					if(buf[loc]!==check.match[i])
					{
						match = false;
						break;
					}
				}

				if(!match)
					break;
			}

			if(!match)
				continue;
			
			r.meta.detections.push(Detection.create({value : matchid, from : "dexmagic", file : r.inputOriginal.primary}));
		}
	}
}
