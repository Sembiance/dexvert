import {Format} from "../../Format.js";

export class aseprite extends Format
{
	name       = "Asperite";
	website    = "http://fileformats.archiveteam.org/wiki/Aseprite";
	ext        = [".ase", ".aseprite"];
	mimeType   = "image/x-aseprite";
	magic      = ["Aseprite Animated sprite", /^Aseprite asset file/];
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
