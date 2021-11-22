import {Format} from "../../Format.js";

export class draw256 extends Format
{
	name        = "Draw 256 Image";
	website     = "http://fileformats.archiveteam.org/wiki/Draw256";
	ext         = [".vga"];
	priority    = this.PRIORITY.VERYLOW;
	mimeType    = "image/x-draw256-vga";
	unsupported = true;
	notes       = "Unsupported because .vga ext is too common, no known magic and converters can't be trusted to verify input file is correct before outputting garbage";
	converters = [`abydosconvert[format:${this.mimeType}]`, "draw256"];
}
