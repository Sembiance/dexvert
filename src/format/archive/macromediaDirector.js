import {Format} from "../../Format.js";

export class macromediaDirector extends Format
{
	name           = "Macromedia Director";
	website        = "http://fileformats.archiveteam.org/wiki/Shockwave_(Director)";
	ext            = [".dir", ".dxr", ".drx", ".cxt", ".cst", ".dcr"];
	forbidExtMatch = true;
	magic          = [
		"Macromedia Director project", "Adobe Director Protected Cast", "Macromedia Director Protected Movie", "Director - Shockwave movie", "Generic RIFX container", "Macromedia Director Shockwave Cast", "Director Cast data",
		/^fmt\/(317|486)( |$)/, /^x-fmt\/341( |$)/
	];
	weakMagic      = ["Generic RIFX container"];
	idMeta         = ({macFileType, macFileCreator}) => ([3, 4, 5, 6, 7].some(num => ([`M*9${num}`, `M!9${num}`, `MV9${num}`, `MC9${num}`].includes(macFileType) && macFileCreator===`MD9${num}`)) ||
		(macFileType==="FGDM" && macFileCreator==="MD00") ||
		(macFileType==="M!85" && macFileCreator==="MD03")
	);
	slow           = true;
	converters     = [
		// Director CastRipper has fully replaced macromediaDirector.js
		// Some files must be unprotected first in order to get "all" the files (such as the lingo scripts), thus projectorrays goes first (DREAM3.DXR for example, without projectorrays then cast ripper only gets 14 files, decompiling it first gets 24 total)
		"projectorRays -> directorCastRipper12",

		// Next, try going straight to directorCastRipper12, which will handle cast files more directly
		"directorCastRipper12",

		// Some files like easyData.dxr are not properly handled by directorCastRipper12. So we use 'dirOpener' which actually re-packs the file as a modern director file, and then pass that to directorCastRipper12
		// This isn't super ideal because dirOpener can mess up assets, but it's better than having nothing at all
		"projectorRays -> dirOpener -> directorCastRipper12",
		"dirOpener -> directorCastRipper12",

		// Some files directorCatRipper12 chokes on (julie) so we just fallback to macromediaDrector itself
		"recover_cct -> macromediaDirector"

		/* Other extractors are available. Some were tried in the past (see sandbox/legacy/program/), some haven't been:
		macromediaDirector	Used to use this for all extraction, but now thanks to Director Cast Ripper, it's not needed anymore

		SCUMMVM		https://github.com/scummvm/scummvm/tree/master/engines/director
					Has great director support including extracting director files out of EXEs, but no CLI extraction tool. In theory could create one, but it looks like it'd be a LOT of work.
					https://github.com/scummvm/scummvm/blob/master/engines/director/resource.cpp
					https://github.com/scummvm/scummvm/blob/master/engines/director/archive.cpp

		drxtract	https://github.com/System25/drxtract
					Works, mostly, but not for all file types. Code also appears to be held together with scotch tape and doesn't have deep support for various bitmap formats
		
		dirry		https://github.com/markhughes/dirry
					Couldn't actually get it to extract anything, but it 'looked' like it was trying. Also no longer being updated.
		
		recover_cct	Used to use this to recover certain .cct files (T4.cct), but now Director Cast Ripper handles them fine

		dirOpener	This tool used to not only un-protect a file, but also re-wrapped it in a modern up to date version of director, though sometimes would mess up some assets.
					It was still an amazingly useful tool to use until Director Cast Ripper was created and now isn't needed at all
		*/
	];
}

// Additional format info:
// https://docs.google.com/document/d/1jDBXE4Wv1AEga-o1Wi8xtlNZY4K2fHxW2Xs8RgARrqk/edit#
// https://docs.google.com/document/d/18FMRZ0EvR2uF9rKTtvt-TXyIMFIBVg13bUhmV3_iHD0/edit
