import {Format} from "../../Format.js";

export class topDrawShapes extends Format
{
	name           = "Top Draw Shapes Archive";
	website        = "http://fileformats.archiveteam.org/wiki/Top_Draw";
	ext            = [".tds", ".td"];
	forbidExtMatch = true;
	magic          = ["Top Draw Shapes"];
	weakMagic      = true;
	unsupported    = true;	// only 6 actual unique files on discmaster, and only really 3 different files, not worth it
	notes          = "No known extractor. I could probably use the original program and figure out a way to get them out, but meh.";
}
