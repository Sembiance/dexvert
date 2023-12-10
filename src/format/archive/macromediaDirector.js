import {Format} from "../../Format.js";

// Often the Director/Cast file will be protected/encrypted
const UNPROTECTORS =
[
	"projectorRays",	// projectorRays is the most optimal un-protector
	"dirOpener",		// some files though are old versions like jigsaw.dcr and dirOpener under windows not only un-protects but will also update it to the latest version allowing them to be opened in Director MX 2004
	"recover_cct"		// Some .cct files (T4.cct) can be un-proceted to cast .cst files that can then be opened
];

export class macromediaDirector extends Format
{
	name           = "Macromedia Director";
	website        = "http://fileformats.archiveteam.org/wiki/Shockwave_(Director)";
	ext            = [".dir", ".dxr", ".drx", ".cxt", ".cst", ".dcr"];
	forbidExtMatch = true;
	magic          = ["Macromedia Director project", "Adobe Director Protected Cast", "Macromedia Director Protected Movie", "Director - Shockwave movie", "Generic RIFX container", "Macromedia Director Shockwave Cast", /^fmt\/(317|486)( |$)/, /^x-fmt\/341( |$)/];
	weakMagic      = ["Generic RIFX container"];
	unsupported    = true;	// TODO REMOVE THIS!!
	
	auxFiles = (input, otherFiles, otherDirs) =>
	{
		const xtrasDir = otherDirs.find(otherDir => otherDir.name.toLowerCase()==="xtras");
		return xtrasDir ? [xtrasDir] : false;
	};
	notes      = "While 'xtras' is included here, it is NOT copied over into Windows with macromediaDirector. See more details in program/archive/macromediaDirector.js";
	converters = [
		"directorCastRipper12"
		
		// We try each unprotector in combination with the prefered priority of extractors before just trying it directly with the extractor
		// This is useful for some files like pbc99.dxr that wouldn't open with dirOpener or recover_cct (but does not work ok with projectorRays)
		//...UNPROTECTORS.map(v => `${v} -> directorCastRipper12`), "directorCastRipper12",
		//...UNPROTECTORS.map(v => `${v} -> directorCastRipper10`), "directorCastRipper10",
		//...UNPROTECTORS.map(v => `${v} -> macromediaDirector`), "macromediaDirector"

		/* Other extractors are available. Some were tried in the past, some haven't been:
		drxtract	https://github.com/System25/drxtract
					Works, mostly, but not for all file types. Code also appears to be held together with scotch tape and doesn't have deep support for various bitmap formats
		
		dirry		https://github.com/markhughes/dirry
					Couldn't actually get it to extract anything, but it 'looked' like it was trying. Also no longer being updated.
		
		SCUMMVM		https://github.com/scummvm/scummvm/tree/master/engines/director
					Has great director support including extracting director files out of EXEs, but no CLI extraction tool. In theory could create one, but it looks like it'd be a LOT of work.
					https://github.com/scummvm/scummvm/blob/master/engines/director/resource.cpp
					https://github.com/scummvm/scummvm/blob/master/engines/director/archive.cpp
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
