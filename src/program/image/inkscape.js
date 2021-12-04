import {xu} from "xu";
import {Program} from "../../Program.js";

export class inkscape extends Program
{
	website        = "https://inkscape.org/";
	gentooPackage  = "media-gfx/inkscape";
	gentooUseFlags = "cdr dbus dia exif graphicsmagick jpeg openmp postscript visio wpg";
	unsafe         = true;
	bin            = "inkscape";
	runOptions     = ({virtualX : true});

	// OLD: inkscape --actions="export-area-drawing; export-filename:/tmp/export.png; export-do;" inputFile
	args = async r => ["--export-area-drawing", "--export-plain-svg", "--export-type=svg", "-o", await r.outFile("out.svg"), r.inFile()];

	chain = "deDynamicSVG";
}
