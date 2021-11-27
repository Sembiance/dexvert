import {Format} from "../../Format.js";

export class photoChrome extends Format
{
	name       = "PhotoChrome";
	website    = "http://fileformats.archiveteam.org/wiki/PhotoChrome";
	ext        = [".pcs"];
	mimeType   = "image/x-photochrome-screen";
	magic      = ["PhotoChrome bitmap"];
	converters = ["recoil2png", `abydosconvert[format:${this.mimeType}]`]
}
