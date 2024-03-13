import {Format} from "../../Format.js";

export class gx2 extends Format
{
	name       = "GX2 Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/GX2";
	ext        = [".gx2"];
	mimeType   = "image/x-gx2";
	magic      = ["GX2 bitmap", /^fmt\/1789( |$)/];
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
