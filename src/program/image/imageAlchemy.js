import {Program} from "../../Program.js";
import * as path from "https://deno.land/std@0.114.0/path/mod.ts";

export class imageAlchemy extends Program
{
	website = "http://fileformats.archiveteam.org/wiki/Image_Alchemy";
	loc = "dos";
	bin = "ALCHEMY.EXE";
	args = r => ["-t", r.inFile(), r.outFile("OUT.TIF")]
	chain = "convert"
}
