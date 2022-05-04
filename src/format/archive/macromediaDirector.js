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
		// We always start out with passing it to dirOpener
		// For 'protected' formats like DXR/CXT it will unprotect it
		// Other files that are really old are updated to a version that the MX 2004 will actually open
		// It handles both
		// If it doesn't need to do anything, it ends up producing an identical output file, which it keeps with allowDupOut = true
		// dirOpener will automatically chain it's result to macromediaDirector
		"dirOpener",

		// Some .cct files (T4.cct) can be converted to un-proceted .cst files and then opened
		"recover_cct",

		// Sometimes dirOpener fails to produce an output file (pbc99.dxr)
		// So we just try directly with macromediaDirector, which as an Xtra installed that allows opening protected formats: https://github.com/tomysshadow/Movie-Restorer-Xtra
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
