import {Format} from "../../Format.js";

export class icns extends Format
{
	name       = "MacOS Icon";
	website    = "http://fileformats.archiveteam.org/wiki/ICNS";
	ext        = [".icns"];
	mimeType   = "image/x-icns";
	magic      = ["Mac OS X icon", "Apple Icon Image Format", /^fmt\/1185( |$)/];
	converters = ["deark", `abydosconvert[format:${this.mimeType}]`];
}
