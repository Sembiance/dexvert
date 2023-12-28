import {Format} from "../../Format.js";

export class aseprite extends Format
{
	name       = "Asperite";
	website    = "http://fileformats.archiveteam.org/wiki/Aseprite";
	ext        = [".ase", ".aseprite"];
	mimeType   = "image/x-aseprite";
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
