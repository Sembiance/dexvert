import {Format} from "../../Format.js";

export class xwd extends Format
{
	name          = "X Window Dump";
	website       = "http://fileformats.archiveteam.org/wiki/XWD";
	ext           = [".xwd", ".dmp"];
	safeExt       = () => ".xwd";
	mimeType      = "image/x-xwindowdump";
	magic         = ["X-Windows Screen Dump", "XWD X Windows Dump image data"];

	// Neither nconvert nor convert properly handle all the files, but nconvert does a little bit better with color images
	converters    = ["nconvert", `abydosconvert[format:${this.mimeType}]`, "convert"]
	metaProvider = ["image"];
}
