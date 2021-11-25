import {Format} from "../../Format.js";

export class aseprite extends Format
{
	name       = "Asperite";
	website    = "https://www.aseprite.org/";
	ext        = [".ase", ".aseprite"];
	mimeType   = "image/x-aseprite";
	converters = [`abydosconvert[format:${this.mimeType}]`]
}
