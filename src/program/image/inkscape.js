import {xu} from "xu";
import {Program} from "../../Program.js";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";

export class inkscape extends Program
{
	website        = "https://inkscape.org/";
	gentooPackage  = "media-gfx/inkscape";
	gentooUseFlags = "cdr dbus dia exif graphicsmagick jpeg openmp postscript visio wpg";
	unsafe         = true;

	bin        = "inkscape"
	runOptions = ({virtualX : true});

	// OLD: inkscape --actions="export-area-drawing; export-filename:/tmp/export.png; export-do;" inputFile
	args = r => ["--export-area-drawing", "--export-plain-svg", "--export-type=svg", "-o", path.join(r.f.outDir.rel, "out.svg"), r.f.input.rel]
}
