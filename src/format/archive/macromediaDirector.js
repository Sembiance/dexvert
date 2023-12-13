import {Format} from "../../Format.js";

export class macromediaDirector extends Format
{
	name           = "Macromedia Director";
	website        = "http://fileformats.archiveteam.org/wiki/Shockwave_(Director)";
	ext            = [".dir", ".dxr", ".drx", ".cxt", ".cst", ".dcr"];
	forbidExtMatch = true;
	magic          = ["Macromedia Director project", "Adobe Director Protected Cast", "Macromedia Director Protected Movie", "Director - Shockwave movie", "Generic RIFX container", "Macromedia Director Shockwave Cast", /^fmt\/(317|486)( |$)/, /^x-fmt\/341( |$)/];
	weakMagic      = ["Generic RIFX container"];
	
	auxFiles = (input, otherFiles, otherDirs) =>
	{
		const xtrasDir = otherDirs.find(otherDir => otherDir.name.toLowerCase()==="xtras");
		return xtrasDir ? [xtrasDir] : false;
	};
	notes      = "While 'xtras' is included here, it is NOT copied over into Windows with macromediaDirector. See more details in program/archive/macromediaDirector.js";
	converters = [
		// Director CastRipper has fully replaced macromediaDirector.js
		// Some files must be unprotected first in order to get "all" the files, thus projectorrays goes first (DREAM3.DXR for example, without projectorrays then cast ripper only gets 14 files, decompiling it first gets 24 total)
		"projectorRays -> directorCastRipper12",

		// Next it's best to go straight to directorCastRipper12, which will handle casts more directly
		"directorCastRipper12",

		// Next try dirOpener which will not only un-protects it but wraps it in a modern up to date version of director for use
		// We've been warned that dirOpener can mess up files it generates, cutting off sounds and such, thus it's a last resort here
		"dirOpener -> directorCastRipper12"

		// recover_cct"		// Some .cct files (T4.cct) can be un-proceted to cast .cst files that can then be opened

		/* Other extractors are available. Some were tried in the past, some haven't been:
		SCUMMVM		https://github.com/scummvm/scummvm/tree/master/engines/director
					Has great director support including extracting director files out of EXEs, but no CLI extraction tool. In theory could create one, but it looks like it'd be a LOT of work.
					https://github.com/scummvm/scummvm/blob/master/engines/director/resource.cpp
					https://github.com/scummvm/scummvm/blob/master/engines/director/archive.cpp

		drxtract	https://github.com/System25/drxtract
					Works, mostly, but not for all file types. Code also appears to be held together with scotch tape and doesn't have deep support for various bitmap formats
		
		dirry		https://github.com/markhughes/dirry
					Couldn't actually get it to extract anything, but it 'looked' like it was trying. Also no longer being updated.
		*/
	];
}

// Additional format info:
// https://docs.google.com/document/d/1jDBXE4Wv1AEga-o1Wi8xtlNZY4K2fHxW2Xs8RgARrqk/edit#
// https://docs.google.com/document/d/18FMRZ0EvR2uF9rKTtvt-TXyIMFIBVg13bUhmV3_iHD0/edit

// Program that scans files for director files: https://github.com/n0samu/director-files-extract/blob/master/shock.py
// Programs that extract anything that looks like a RIFFX file:
// https://github.com/irrwahn/riffx
// https://github.com/PKBeam/RiffExt
