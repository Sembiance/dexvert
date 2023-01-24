import {xu} from "xu";
import {fileUtil} from "xutil";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

// Most file detections from from 'file', 'TrID' and 'siegfried'. Below are a couple additional detections.
// All offsets matches must match (except a match array that has a subarray, the subarry is a list of possible matches for that byte position)

/* eslint-disable unicorn/no-hex-escape, max-len */
const DEXMAGIC_CHECKS =
{
	// 3d
	"IFF Cinema 4D file" : [{offset : 0, match : "FORM"}, {offset : 8, match : "FRAY"}],

	// archive
	"ActiveMime (Base64 Encoded)" : [{offset : 0, match : "QWN0aXZlTWltZQ"}],
	"Anna-Marie Archive"          : [{offset : 0, match : "Anna-Marie"}],
	"Anna-Marie Archive (alt)"    : [{offset : -160, match : "Anna-Marie"}],
	"HTTP Response"               : [{offset : 0, match : "HTTP/1."}, {offset : 8, match : " 200 OK\r\n"}],
	"IFF CAT file"                : [{offset : 0, match : "CAT "}],
	"IFF LIST file"               : [{offset : 0, match : "LIST"}, {offset : 8, match : "SSETPROP"}],
	"imageUSB"                    : [{offset : 0, match : "i\x00m\x00a\x00g\x00e\x00U\x00S\x00B"}],
	"MINICAT Archive"             : [{offset : 0, match : "MINICAT"}],
	"NeXT Disk Image Dump"        : [{offset : 46, match : "dlV3"}],
	"Palm Web Content Record"     : [{offset : 0, match : [0x00, 0x00, 0x00, 0x14]}, {offset : 0x0C, match : [[0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06]]}, {offset : 0x0D, match : [[0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06]]}],
	"pcxLib compressed"           : [{offset : 0, match : "pcxLib"}, {offset : 10, match : "Copyright (c) Genus Microprogramming, Inc."}],
	"SCR Package"                 : [{offset : 0, match : "This is SCR Package File"}],
	"TTW Compressed File"         : [{offset : 0, match : "TTW!"}, {offset : 8, match : [0x00]}, {offset : 12, match : [0x01]}],
	"Visual Novel DPK Archive"    : [{offset : 0, match : "PA"}],
	"WAD2 file"                   : [{offset : 0, match : "WAD2"}],

	// audio
	"EA BNK Audio" : [{offset : 0, match : "BNKl"}],
	"KORG File"    : [{offset : 0, match : "KORG"}],

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
	"Alias PIX"                   : [{offset : 4, match : [0x00, 0x00, 0x00, 0x00, 0x00, 0x18]}],
	"Apple IIGS Preferred Format" : [{offset : 2, match : [0x00, 0x00, 0x04]}, {offset : 5, match : "MAIN"}],
	"ArtMaster88"                 : [{offset : 0, match : "SS"}, {offset : 2, match : [0x5F]}, {offset : 3, match : "SIF"}],
	"Auto/FX Image"               : [{offset : 0, match : [0x89, 0x41, 0x46, 0x58]}],
	"CAD/Draw TVG"                : [{offset : 0, match : "TommySoftware TVG"}],
	"CD-I IFF Image"              : [{offset : 0, match : "FORM"}, {offset : 8, match : "IMAGIHDR"}],
	"CharPad"                     : [{offset : 0, match : "CTM"}, {offset : 3, match : [0x05]}],
	"DeskMate Paint Alt"          : [{offset : 0, match : "PNT"}],
	"Funny Paint"                 : [{offset : 0, match : [0x00, 0x0A, 0xCF, 0xE2]}],
	"GoDot Clip"                  : [{offset : 0, match : "GOD1"}],
	"Konica Quality Photo"        : [{offset : 0, match : [0x42, 0x4D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}, {offset : 30, match : [0x4A, 0x50, 0x45, 0x47]}],
	"MLDF BMHD file"              : [{offset : 0, match : "FORM"}, {offset : 8, match : "MLDFBMHD"}],
	"multiArtist"                 : [{offset : 0, match : [0x4D, 0x47, 0x48, 0x01]}],
	"NAPLPS Image"                : [{offset : 0, match : [0x0C, 0x0E, 0x20, 0x4C, 0x6F, 0x21, 0x48, 0x40, 0x40, 0x49, 0x3E, 0x40, 0x3C, 0x40, 0x40, 0x40, 0x3E]}],
	"PaintWorks"                  : [{offset : 54, match : "ANvisionA"}],
	"PCR Image"                   : [{offset : 0, match : "KPG"}, {offset : 5, match : [0x10]}],
	"Picasso 64 Image"            : [{offset : 0, match : [0x00, 0x18]}],
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
	"IFF Deluxe Music Score"           : [{offset : 0, match : "FORM"}, {offset : 8, match : "DMCS"}],
	"RIFF MIDS file"                   : [{offset : 0, match : "RIFF"}, {offset : 8, match : "MIDS"}],

	// other
	"Atari ST Guide Hypertext"         : [{offset : 0, match : "HDOC"}],
	"Director STXT"                    : [{offset : 0, match : [0x00, 0x00, 0x00, 0x0C, 0x00, 0x00]}],
	"MegaZeux Board"                   : [{offset : 0, match : [0xFF]}, {offset : 1, match : ["M", ["B", 0x02]]}],
	"MegaZeux Save"                    : [{offset : 0, match : ["M", "Z", ["S", "X"], ["V", "S", 0x02]]}],
	"MegaZeux World"                   : [{offset : 25, match : [0x00]}, {offset : 26, match : ["M", ["Z", 0x02]]}],
	"MegaZeux World (Encrypted)"       : [{offset : 25, match : [0x01]}, {offset : 41, match : ["M", ["Z", 0x02]]}],
	"MegaZeux World (Encrypted) (Alt)" : [{offset : 25, match : [0x01]}, {offset : 42, match : ["M", ["Z", 0x02]]}],
	"OLB Library"                      : [{offset : 0, match : "Gnu is Not eUnuchs"}, {offset : 18, match : [0x2E, 0x0A, 0x5F, 0x5F, 0x2E]}, {offset : 23, match : "SYMDEF"}],
	"VCD Info File"                    : [{offset : 0, match : "VIDEO_CD"}],
	"ZZT World"                        : [{offset : 0, match : [0xFF, 0xFF]}, {offset : 3, match : [0x00]}],

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
/* eslint-enable unicorn/no-hex-escape, max-len */

const DEXMAGIC_FILE_META_CHECKS =
[
	// uniso[hfs] will output the macintosh file type for each output file. This may be fed back into a future dexvert/identifcation as fileMeta. So we check that here
	// file and creator types: sandbox/txt/MacOS_File_Types_and_Creator_Codes.pdf  (originally from https://vintageapple.org/macbooks/pdf/The_Macintosh_System_Fitness_Plan_(system_7.5)_1995.pdf)
	({macFileType, macCreatorType}) =>	// eslint-disable-line no-unused-vars
	{
		switch(macFileType)
		{
			case "DRWG":
				return "Macintosh MacDraw II Document";

			case "GIFf":
				return "Macintosh GIF";
			
			case "MooV":
				return "Macintosh QuickTime Movie";
			
			case "PICT":
				return "Macintosh PICT";
			
			case "PNTG":
				return "Macintosh MacPaint";
			
			case "SIT5":
				return "Macintosh StuffIt 5 Archive";

			case "TEXT":
			case "ttro":
				return "Macintosh Text File";

			case "TIFF":
				return "Macintosh TIFF";
		}

		return null;
	}
];

Object.values(DEXMAGIC_CHECKS).flat().forEach(check =>
{
	if(typeof check.match==="string")
		check.match = (new TextEncoder()).encode(check.match);
});
const DEXMAGIC_BYTES_MAX = Object.values(DEXMAGIC_CHECKS).flat().map(check => ((check.size || check.offset || 0)+(check.match?.length || 0))).max();

export class dexmagic extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	loc     = "local";
	exec    = async r =>
	{
		r.meta.detections = [];

		if(r.f.input.meta)
		{
			for(const fmc of DEXMAGIC_FILE_META_CHECKS)
			{
				const value = fmc(r.f.input.meta);
				if(value)
					r.meta.detections.push(Detection.create({value, from : "dexmagic", file : r.f.input}));
			}
		}

		const buf = await fileUtil.readFileBytes(r.inFile({absolute : true}), DEXMAGIC_BYTES_MAX);
		
		for(const [matchid, checks] of Object.entries(DEXMAGIC_CHECKS))
		{
			let match=true;
			for(const check of checks)
			{
				if(Object.hasOwn(check, "fn"))
				{
					match = await check.fn(r);
				}
				else if(Object.hasOwn(check, "offset"))
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
							if(backBuf[i]!==check.match[i])
							{
								match = false;
								break;
							}
						}
					}
					else
					{
						for(let loc=check.offset, i=0;i<check.match.length;loc++, i++)
						{
							if(Array.isArray(check.match[i]))
							{
								if(!check.match[i].map(v => (typeof v==="string" ? v.charCodeAt(0) : v)).includes(buf[loc]))
								{
									match = false;
									break;
								}
							}
							else
							{
								const matchByte = typeof check.match[i]==="string" ? check.match[i].charCodeAt(0) : check.match[i];
								if(buf[loc]!==matchByte)
								{
									match = false;
									break;
								}
							}
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
