import {Format} from "../../Format.js";

export class draw256 extends Format
{
	name        = "Draw 256 Image";
	website     = "http://fileformats.archiveteam.org/wiki/Draw256";
	ext         = [".vga"];
	priority    = this.PRIORITY.VERYLOW;
	mimeType    = "image/x-draw256-vga";
	unsupported = true;	// extension only match, only 4 known sample files
	converters = [`abydosconvert[format:${this.mimeType}]`, "draw256"];
}
