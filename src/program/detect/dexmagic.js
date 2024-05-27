import {xu} from "xu";
import {fileUtil} from "xutil";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {path} from "std";

// Most file detections from from 'file', 'TrID' and 'siegfried'. Below are a couple additional detections.
// All offsets matches must match 'match' property
// match can be a string, which means it has to match that string
// if match is an array of strings, then it can match any of those strings
// if match is an array of bytes then it must match those bytes exactly
// if match has a subarray, then it matches if any of those bytes in that subarray match the loc (NOTE! So if you need to match 0x4A OR 0x4B its match : [[0x4A, 0x4B]]  NOT [[0x4A], [0x4B]])
// You can also specify a size and it will look for the 'match' bytes anywhere in the first 'size' bytes of the file

/* eslint-disable unicorn/no-hex-escape */
const DEXMAGIC_CHECKS =
{
	// 3d
	"IFF Cinema 4D file" : [{offset : 0, match : "FORM"}, {offset : 8, match : "FRAY"}],
	"Cinema 4D XML"      : [{size : 256, match : "<c4d_file"}],

	// archive
	"ActiveMime (Base64 Encoded)" : [{offset : 0, match : "QWN0aXZlTWltZQ"}],
	"Anna-Marie Archive"          : [{offset : 0, match : "Anna-Marie"}],
	"Anna-Marie Archive (alt)"    : [{offset : -160, match : "Anna-Marie"}],
	"HTTP Response"               : [{offset : 0, match : "HTTP/1."}, {offset : 8, match : " 200 OK\r\n"}],
	"IFF CAT file"                : [{offset : 0, match : "CAT "}],
	"IFF LIST file"               : [{offset : 0, match : "LIST"}, {offset : 8, match : "SSETPROP"}],
	"imageUSB"                    : [{offset : 0, match : "i\x00m\x00a\x00g\x00e\x00U\x00S\x00B"}],
	"Macromedia Projector"        : [{offset : 0, match : ["RIFX", "XFIR"]}, {offset : 8, match : ["LPPA", "APPL"]}],
	"MINICAT Archive"             : [{offset : 0, match : "MINICAT"}],
	"NeXT Disk Image Dump"        : [{offset : 46, match : "dlV3"}],
	"PACKIT Installation Archive" : [{offset : 0, match : "PACKIT by MJP"}],
	"Palm Web Content Record"     : [{offset : 0, match : [0x00, 0x00, 0x00, 0x14]}, {offset : 0x0C, match : [[0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06]]}, {offset : 0x0D, match : [[0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06]]}],
	"pcxLib compressed"           : [{offset : 0, match : "pcxLib"}, {offset : 10, match : "Copyright (c) Genus Microprogramming, Inc."}],
	"POD Archive"                 : [{offset : 4, match : [["Startup", "TV", "Disk", "Fury"]]}],
	"SCR Package"                 : [{offset : 0, match : "This is SCR Package File"}],
	"TTW Compressed File"         : [{offset : 0, match : "TTW!"}, {offset : 8, match : [0x00]}, {offset : 12, match : [0x01]}],
	"ThumbsUp Database"           : [{offset : 0, match : [0xBE, 0xBA, 0xDA, 0xBE]}],
	"Visual Novel DPK Archive"    : [{offset : 0, match : "PA"}],
	"VICE Installer EXE"          : [{offset : -8, match : "ESIV"}, {offset : -4, match : [0xA0, 0x9A, 0x00, 0x00]}],
	"Wacky Wheels Archive"        : [{offset : 2, match : "WACKY.ING"}],
	"WAD2 file"                   : [{offset : 0, match : "WAD2"}],

	// audio
	"EA BNK Audio"          : [{offset : 0, match : "BNKl"}],
	"GameCube Music (IDSP)" : [{offset : 0, match : "IDSP"}],
	"KORG File"             : [{offset : 0, match : "KORG"}],
	"RedSpark Audio"        : [{offset : 0, match : "RSD"}, {offset : 3, match : [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]]}],

	// document
	"DocBook"                                 : [{size : 256, match : "DOCTYPE book"}],
	"GNU Info"                                : [{offset : 0, match : "This is Info file"}],
	"MacWrite Document"                       : [{offset : 0, match : [0x00, 0x06, 0x00]}, {offset : 4, match : [0x00, 0x06, 0x00, 0x02]}],
	"Microsoft Publisher v1"                  : [{offset : 0, match : [0xE7, 0xAC, 0x2C, 0x00]}],
	"PageStream Document"                     : [{offset : 0, match : [0x07, 0x23, 0x19, 0x92, 0x00, 0x0D, 0x02, 0x00, 0x00]}],
	"PCBoard Programming Language Executable" : [{offset : 0, match : "PCBoard Programming Language Executable"}],
	"Wildcat WCX"                             : [{offset : 0, match : "GHSH"}],

	// executable
	"FM-TownsOS EXP P3" : [{offset : 0, match : "P3"}],
	"FM-TownsOS EXP MP" : [{offset : 0, match : "MP"}],
	
	// font
	"PCR Font" : [{offset : 0, match : "KPG"}, {offset : 5, match : [0x20]}],

	// image
	"101 Clips Image"             : [{offset : 0, match : [0xFF, 0xFF, 0xFF, 0xFF, [0x02, 0x03]]}],
	"3D Browser Pro Catalogue"    : [{offset : 0, match : [0x03]}, {offset : 1, match : "obv"}],
	"Alias PIX"                   : [{offset : 4, match : [0x00, 0x00, 0x00, 0x00, 0x00, 0x18]}],
	"Apple IIGS Preferred Format" : [{offset : 2, match : [0x00, 0x00, 0x04]}, {offset : 5, match : "MAIN"}],
	"ArtMaster88"                 : [{offset : 0, match : "SS"}, {offset : 2, match : [0x5F]}, {offset : 3, match : "SIF"}],
	"Auto/FX Image"               : [{offset : 0, match : [0x89, 0x41, 0x46, 0x58]}],
	"CAD/Draw TVG"                : [{offset : 0, match : "TommySoftware TVG"}],
	"CD-I IFF Image"              : [{offset : 0, match : "FORM"}, {offset : 8, match : "IMAGIHDR"}],
	"CharPad"                     : [{offset : 0, match : "CTM"}, {offset : 3, match : [0x05]}],
	"DeskMate Paint Alt"          : [{offset : 0, match : "PNT"}],
	"Digi-Pic 2"                  : [{offset : 32000, match : [0x01, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}],
	"ECI Graphic Editor"          : [{offset : 0, match : [0x00, 0x40]}],
	"FM-Towns HEL Animation"      : [{offset : 0, match : "he1"}],
	"Funny Paint"                 : [{offset : 0, match : [0x00, 0x0A, 0xCF, 0xE2]}],
	"GoDot Clip"                  : [{offset : 0, match : "GOD1"}],
	"Konica Quality Photo"        : [{offset : 0, match : [0x42, 0x4D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}, {offset : 30, match : [0x4A, 0x50, 0x45, 0x47]}],
	"MLDF BMHD file"              : [{offset : 0, match : "FORM"}, {offset : 8, match : "MLDFBMHD"}],
	"multiArtist"                 : [{offset : 0, match : [0x4D, 0x47, 0x48, 0x01]}],
	"NAPLPS Image"                : [{offset : 0, match : [0x0C, 0x0E, 0x20, 0x4C, 0x6F, 0x21, 0x48, 0x40, 0x40, 0x49, 0x3E, 0x40, 0x3C, 0x40, 0x40, 0x40, 0x3E]}],
	"PaintWorks"                  : [{offset : 54, match : "ANvisionA"}],
	"PCR Image"                   : [{offset : 0, match : "KPG"}, {offset : 5, match : [0x10]}],
	"Picasso 64 Image"            : [{offset : 0, match : [0x00, 0x18]}],
	"QPC Image"                   : [{offset : 0, match : "QPC Graphic Data Headder Block"}],
	"Reko CardSet - RKP"          : [{offset : 0, match : "PCRKP"}],
	"Reko CardSet - REKO"         : [{offset : 0, match : "PCREKO"}],
	"Saracen Paint Image"         : [{offset : 0, match : [0x00, 0x78]}],
	"Second Nature Slide Show"    : [{offset : 0, match : "Second Nature Software\r\nSlide Show\r\nCollection"}],
	"SLP Image"                   : [{offset : 0, match : "2.0N"}],
	"Universal BitMap Format"     : [{offset : 0, match : "UBF92a"}],
	"Young Picasso"               : [{offset : 0, match : [0x50, 0x00, 0x00, 0x50, 0x00, 0x00, 0x52, 0x00, 0x00]}],
	"ZX Spectrum BSP"             : [{offset : 0, match : "bsp"}, {offset : 3, match : [0xC0]}],
	"ZX Spectrum CHR"             : [{offset : 0, match : "chr"}, {offset : 3, match : [0x24]}],

	// music
	"AdLib MUS"                        : [{offset : 0, match : [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0]}],
	"AMOS Memory Bank, Tracker format" : [{offset : 0, match : "AmBk"}, {offset : 12, match : "Tracker "}],
	"Ben Daglish"                      : [{offset : 0, match : [0x60, 0x00]}, {offset : 4, match : [0x60, 0x00]}, {offset : 9, match : [0x00, 0x60, 0x00]}],
	"Chaos Music Composer (CMC)"       : [{offset : 0, match : [0xFF, 0xFF]}, {offset : 6, match : [0xA0, 0xE3, 0xED, 0xE3, 0xA0, 0xE4, 0xE1, 0xF4, 0xE1, 0xA0, 0xE6, 0xE9, 0xEC, 0xE5, 0xA0, 0x8E, 0x95, 0x0D, 0x20]}],
	"Chaos Music Composer (CMS)"       : [{offset : 6, match : [0x80, 0xA4, 0xEF, 0xF5, 0xE2, 0xEC, 0xE5, 0x80, 0xB3, 0xA3]}],
	"Delta Music Composer"             : [{offset : 0, match : [0xFF, 0xFF, 0x00, 0x20, 0xFF]}, {offset : 5, match : [[0x4B, 0x4C]]}],
	"Digital Studio (AY)"              : [{offset : 168, match : [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xAE, 0x7E, 0xAE, 0x7E, 0x51, 0x00, 0x00, 0x00, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20]}],
	"E-Tracker (Alt)"                  : [{offset : 1213, match : "ETracker (C) BY ESI"}],
	"Future Composer Atari"            : [{offset : 0, match : [0x26, 0x23]}],
	"Galaxy Music System"              : [{offset : 0, match : "MUSE"}, {offset : 4, match : [0xDE, 0xAD, [0xBE, 0xBA], [0xAF, 0xBE]]}],
	"IFF Deluxe Music Score"           : [{offset : 0, match : "FORM"}, {offset : 8, match : "DMCS"}],
	"Music ProTracker"                 : [{offset : 211, match : [0x78, 0x72, 0x6B, 0x65, 0x5F, 0x5A, 0x55, 0x50, 0x4B, 0x47, 0x43]}],
	"NTSP-system"                      : [{offset : 0, match : "SPNT"}],
	"Pha Packer"                       : [{offset : 8, match : [0x00, 0x00, 0x03, 0xC0]}],
	"The Player 2.2A"                  : [{offset : 0, match : "P22A"}],
	"The Player 3.0A"                  : [{offset : 0, match : "P30A"}],
	"Promizer 1.0c/1.8"                : [{offset : 0, match : [0x60, 0x38, 0x60, 0x00, 0x00, 0xA0, 0x60, 0x00, 0x01, 0x3E, 0x60, 0x00, 0x01, 0x0C, 0x48, 0xE7]}],
	"Promizer 2.0"                     : [{offset : 0, match : [0x60, 0x00, 0x00, 0x16, 0x60, 0x00, 0x01, 0x40, 0x60, 0x00, 0x00, 0xF0, 0x3F, 0x00, 0x10, 0x3A]}],
	"RIFF MIDS file"                   : [{offset : 0, match : "RIFF"}, {offset : 8, match : "MIDS"}],
	"SQ Digital Tracker"               : [{offset : 247, match : [0xDD, 0x36, 0x79, 0x00, 0xCD, 0x54, 0xDE, 0xFD, 0x36]}],
	"Theta Music Composer 1.x"         : [{offset : 0, match : [0xFF, 0xFF]}, {offset : 35, match : [0x20]}],
	"Theta Music Composer 2.x"         : [{offset : 0, match : [0xFF, 0xFF]}, {offset : 6, match : [0x0E, 0x15, 0x8D, 0xD4, 0xCD, 0xC3, 0xA0, 0xD3, 0xCF, 0xCE, 0xC7, 0xA0, 0xC6, 0xC9, 0xCC, 0xC5, 0xA0, 0xB2, 0xAE, 0xB0, 0x8D, 0x15, 0x0E]}],
	"Tracker Packer 1/2"               : [{offset : 0, match : "MEXX"}],
	"TurboFM Dumped"                   : [{offset : 0, match : "TFMDM"}],
	"WonderSwan WSR Audio"             : [{offset : -32, match : "WSRF"}],

	// other
	"Atari ST Guide Hypertext"         : [{offset : 0, match : "HDOC"}],
	"Bolo Map"                         : [{offset : 0, match : "BMAPBOLO"}],
	"Director STXT"                    : [{offset : 0, match : [0x00, 0x00, 0x00, 0x0C, 0x00, 0x00]}],
	"MegaZeux Board"                   : [{offset : 0, match : [0xFF]}, {offset : 1, match : ["M", ["B", 0x02]]}],
	"MegaZeux Save"                    : [{offset : 0, match : ["M", "Z", ["S", "X"], ["V", "S", 0x02]]}],
	"MegaZeux World"                   : [{offset : 25, match : [0x00]}, {offset : 26, match : ["M", ["Z", 0x02]]}],
	"MegaZeux World (Encrypted)"       : [{offset : 25, match : [0x01]}, {offset : 41, match : ["M", ["Z", 0x02]]}],
	"MegaZeux World (Encrypted) (Alt)" : [{offset : 25, match : [0x01]}, {offset : 42, match : ["M", ["Z", 0x02]]}],
	"OLB Library"                      : [{offset : 0, match : "Gnu is Not eUnuchs"}, {offset : 18, match : [0x2E, 0x0A, 0x5F, 0x5F, 0x2E]}, {offset : 23, match : "SYMDEF"}],
	"VCD Info File"                    : [{offset : 0, match : "VIDEO_CD"}],
	"ZZT World"                        : [{offset : 0, match : [0xFF, 0xFF]}, {offset : 3, match : [0x00]}],

	// poly
	"Inter-Quake Model"                : [{offset : 0, match : "INTERQUAKEMODEL"}],
	"Google SketchUp Model"            : [{offset : 1, match : "SketchUp Model"}],
	"rtcwMDC"                          : [{offset : 0, match : "IDPC"}],

	// video
	"Disney Animation Studio Secure Animation" : [{offset : 0, match : "SSFFANM"}],
	"RIFF ANIM file"                           : [{offset : 0, match : "RIFF"}, {offset : 8, match : "ANIM"}],

	// unsupported
	"Amiga Action Reply 3 Freeze File" : [{offset : 0, match : [0x41, 0x52, 0x50, 0x33, 0x00]}, {offset : 8, match : [0x00]}, {offset : 12, match : [0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00]}, {offset : 22, match : Array(10).fill(0x00)}],
	"AMOS Memory Bank, Data format"    : [{offset : 0, match : "AmBk"}, {offset : 12, match : "Datas   "}],
	"Atari CTB File"                   : [{offset : 0, match : "GSP22-CTB"}],
	"Atari GEM OBM File"               : [{offset : 0, match : [0x00, 0x01, 0x00, 0x22, 0x00, 0x00]}, {offset : 17, match : Array(5).fill(0x00)}, {offset : 34, match : [0x00]}, {offset : 36, match : [0x00]}, {offset : 38, match : [0x00, 0x02]}, {offset : 53, match : Array(5).fill(0x00)}],
	"IFF GXUI file"                    : [{offset : 0, match : "FORM"}, {offset : 8, match : "GXUI"}],
	"IFF SDBG file"                    : [{offset : 0, match : "FORM"}, {offset : 8, match : "SDBG"}],
	"RIFF MSXF file"                   : [{offset : 0, match : "RIFF"}, {offset : 8, match : "MSXF"}],
	"RIFF MxSt file"                   : [{offset : 0, match : "RIFF"}, {offset : 8, match : "MxSt"}],
	"RIFF STYL file"                   : [{offset : 0, match : "RIFF"}, {offset : 8, match : "STYL"}],
	"VCD Entries File"                 : [{offset : 0, match : "ENTRYVCD"}],
	"VideoTracker Routine"             : [{offset : 0, match : "PVC!"}]
};
/* eslint-enable unicorn/no-hex-escape */

const DEXMAGIC_CUSTOMS =
[
	// sometimes a .bin file can be valid but not match any magics at all, but format iso doesn't match on .bin extension due to how common it is
	// So we just do a quick check to see if we have a corresponding .cue file in the same dir
	async function checkBinCue(r)
	{
		if(r.f.input.ext?.toLowerCase()!==".bin")
			return;
		
		if(await fileUtil.exists(path.join(r.f.input.dir, `${r.f.input.name}.cue`)))
			return "BIN with CUE";
	},
	
	async function checkInstallIt(r)
	{
		if(r.f.input.size<43)
			return;

		const suffix = await fileUtil.readFileBytes(r.f.input.absolute, 6, -43);
		if(suffix.indexOfX([0x43, 0x50, 0x32, 0x2E, 0x30, 0x30])===0)	// CP2.00 in hex
			return "InstallIt! compressed file";
	},

	async function checkMacromediaProjector(r)
	{
		if(r.f.input.size<8)
			return;

		const header = await fileUtil.readFileBytes(r.f.input.absolute, 8);
		if(!["PJ93", "PJ95", "39JP", "59JP"].includes(header.getString(0, 4)))
			return;

		const rifxOffset = header.getUInt32BE(4);
		if(rifxOffset<8 || (rifxOffset+12)>=r.f.input.size)
			return;

		const rifxHeader = await fileUtil.readFileBytes(r.f.input.absolute, 12, rifxOffset);
		if(!["RIFX", "XFIR"].includes(rifxHeader.getString(0, 4)))
			return;

		if(!["LPPA", "APPL"].includes(rifxHeader.getString(8, 4)))
			return;

		return "Macromedia Projector (alt)";
	},

	async function checkFMTownsSND(r)
	{
		if(r.f.input.size<33)
			return;

		// logic from ggxsnd-0.8.1/snd.h and checkSndHeader in snd_file.c (sandbox/app/)
		const header = await fileUtil.readFileBytes(r.f.input.absolute, 32);
		if(header.getUInt32LE(12)!==(r.f.input.size-32))
			return;
		
		const rate = header.getUInt16LE(24);
		if(rate>2024)
			return;

		if(header.getUInt8(29)!==0 || header.getUInt16LE(30)!==0)
			return;
		
		return "FM-Towns SND";
	}
];

const textEncoder = new TextEncoder();
Object.values(DEXMAGIC_CHECKS).flat().forEach(check =>
{
	if(Array.isArray(check.match))
		check.match = check.match.map(match => (typeof match==="string" ? Array.from(textEncoder.encode(match)) : match));
	else if(typeof check.match==="string")
		check.match = Array.from(textEncoder.encode(check.match));
});
const DEXMAGIC_BYTES_MAX = Object.values(DEXMAGIC_CHECKS).flat().map(check => ((check.size || check.offset || 0)+(check.match?.length || 0))).max();

export class dexmagic extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	loc     = "local";
	exec    = async r =>
	{
		r.meta.detections = [];

		for(const custom of DEXMAGIC_CUSTOMS)
		{
			const value = await custom(r);
			if(value)
				r.meta.detections.push(Detection.create({value, from : "dexmagic", file : r.f.input}));
		}

		const checkMatcher = (data, loc, matcher) =>
		{
			if(Array.isArray(matcher))
			{
				if(!matcher.map(v => (typeof v==="string" ? v.charCodeAt(0) : v)).includes(data[loc]))
					return false;
			}
			else
			{
				const matchByte = typeof matcher==="string" ? matcher.charCodeAt(0) : matcher;
				if(data[loc]!==matchByte)
					return false;
			}

			return true;
		};

		const buf = await fileUtil.readFileBytes(r.inFile({absolute : true}), DEXMAGIC_BYTES_MAX);
		
		for(const [matchid, checks] of Object.entries(DEXMAGIC_CHECKS))
		{
			let match=true;
			for(const check of checks)
			{
				if(Object.hasOwn(check, "offset"))
				{
					if(check.offset<0)
					{
						if(Math.abs(check.offset)>r.f.input.size)
						{
							match = false;
							break;
						}
						
						// check from back of file, requires reading in what is needed, only allows one match
						const backBuf = await fileUtil.readFileBytes(r.inFile({absolute : true}), check.match.length, check.offset);
						for(let i=0;i<check.match.length;i++)
						{
							match = checkMatcher(backBuf, i, check.match[i]);
							if(!match)
								break;
						}
					}
					else
					{
						for(let loc=check.offset, i=0;i<check.match.length;loc++, i++)
						{
							match = checkMatcher(buf, loc, check.match[i]);
							if(!match)
								break;
						}
					}
				}
				else if(Object.hasOwn(check, "size"))
				{
					match = buf.indexOfX(check.match)!==-1;
				}

				if(!match)
					break;
			}

			if(!match)
				continue;
			
			r.meta.detections.push(Detection.create({value : matchid, from : "dexmagic", file : r.f.input}));
		}
	};
	renameOut = false;
}
