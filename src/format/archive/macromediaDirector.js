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
		// Often the Director/Cast file will be protected/encrypted

		// projectorRays is the most optimal un-protector
		"projectorRays -> macromediaDirector",
		
		// some files though are old versions like jigsaw.dcr and dirOpener under windows not only un-protects but will also update it to the latest version allowing them to be opened in Director MX 2004
		"dirOpener -> macromediaDirector",

		// Some .cct files (T4.cct) can be un-proceted to cast .cst files that can then be opened
		"recover_cct -> macromediaDirector",

		// Lastly, just try directly with macromediaDirector, which as an Xtra installed that allows opening protected formats: https://github.com/tomysshadow/Movie-Restorer-Xtra
		// This is useful for some files like pbc99.dxr that wouldn't open with dirOpener or recover_cct (but does not work ok with projectorRays)
		"macromediaDirector"
	];
}

// Additional format info:
// https://docs.google.com/document/d/1jDBXE4Wv1AEga-o1Wi8xtlNZY4K2fHxW2Xs8RgARrqk/edit#
// https://docs.google.com/document/d/18FMRZ0EvR2uF9rKTtvt-TXyIMFIBVg13bUhmV3_iHD0/edit

// Program that scans files for director files: https://github.com/n0samu/director-files-extract/blob/master/shock.py
// Programs that extract anything that looks like a RIFFX file:
// https://github.com/irrwahn/riffx
// https://github.com/PKBeam/RiffExt
