import {Format} from "../../Format.js";

export class gx1 extends Format
{
	name       = "GX1 Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/GX1";
	ext        = [".gx1"];
	mimeType   = "image/x-gx1";
	magic      = ["GX1 bitmap"];
	converters = [`abydosconvert[format:${this.mimeType}]`]
}
