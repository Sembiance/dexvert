import {xu} from "xu";
import {Program} from "../../Program.js";

export class inkscape extends Program
{
	website        = "https://inkscape.org/";
	package  = "media-gfx/inkscape";
	unsafe         = true;
	bin            = "inkscape";
	runOptions     = ({virtualX : true});

	// OLD: inkscape --actions="export-area-drawing; export-filename:/tmp/export.png; export-do;" inputFile
	args      = async r => ["--export-area-drawing", "--export-plain-svg", "--export-type=svg", "-o", await r.outFile("out.svg"), r.inFile()];
	renameOut = true;
	chain     = "deDynamicSVG";
}
