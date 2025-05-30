import {Format} from "../../Format.js";

export class grafx2 extends Format
{
	name       = "GrafX2";
	website    = "http://fileformats.archiveteam.org/wiki/PKM";
	ext        = [".pkm"];
	magic      = ["GrafX2 bitmap", "deark: pkm"];
	mimeType   = "image/x-pkm";
	converters = ["deark[module:pkm]", `abydosconvert[format:${this.mimeType}]`];
	verify     = ({meta}) => meta.colorCount>1;
}
