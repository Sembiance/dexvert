import {Format} from "../../Format.js";

export class artist64 extends Format
{
	name       = "Wigmore Artist 64";
	website    = "http://fileformats.archiveteam.org/wiki/Wigmore_Artist_64";
	ext        = [".a64", ".wig"];
	mimeType   = "image/x-artist-64";
	converters = [`abydosconvert[format:${this.mimeType}]`, "view64"]
}
