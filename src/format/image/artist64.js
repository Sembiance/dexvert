import {Format} from "../../Format.js";

export class artist64 extends Format
{
	name       = "Wigmore Artist 64";
	website    = "http://fileformats.archiveteam.org/wiki/Wigmore_Artist_64";
	ext        = [".a64", ".wig"];
	magic      = ["Artist 64 :a64:"];
	mimeType   = "image/x-artist-64";
	converters = ["nconvert[format:a64]", `abydosconvert[format:${this.mimeType}]`];	// Too loose: view64		Not necessary: tomsViewer
}
