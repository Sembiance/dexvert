import {Format} from "../../Format.js";

export class texFont extends Format
{
	name       = "TexFont Texture Mapped Font";
	website    = "http://fileformats.archiveteam.org/wiki/TexFont";
	ext        = [".txf"];
	magic      = ["TexFont"];
	notes      = "Using sandbox/app/glut-master/progs/texfont/showtxf.c I can render it to a cube. Could write C code to render the whole test alphabet letters and then save that to an image, but MEH.";
	converters = ["wuimg"];
}
