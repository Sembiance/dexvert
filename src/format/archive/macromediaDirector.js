import {Format} from "../../Format.js";

export class macromediaDirector extends Format
{
	name           = "Macromedia Director";
	website        = "http://fileformats.archiveteam.org/wiki/Shockwave_(Director)";
	ext            = [".dir", ".dxr", ".drx", ".cxt", ".cst", ".dcr"];
	forbidExtMatch = true;
	magic          = ["Macromedia Director project", "Adobe Director Protected Cast", "Macromedia Director Protected Movie", "Director - Shockwave movie", "Generic RIFX container"];
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
		"dirOpener"

		// NOTE: If I encounter any instances where dirOpener fails to produce any file, I should add "macromediaDirector" here as a fallback
	];
}
