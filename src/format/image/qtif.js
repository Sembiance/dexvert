import {Format} from "../../Format.js";

export class qtif extends Format
{
	name       = "QuickTime Image Format";
	website    = "http://fileformats.archiveteam.org/wiki/QTIF";
	ext        = [".qtif", ".qif"];
	mimeType   = "image/qtif";
	magic      = ["QuickTime Image Format", "Apple QuickTime image", "image/x-quicktime"];
	notes      = "Not all QTIF sub formats are not supported.";
	converters = ["deark[module:qtif][mac]", "nconvert", `abydosconvert[format:${this.mimeType}]`, "ffmpeg[outType:png]"];
}
