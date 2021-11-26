import {Format} from "../../Format.js";

export class dcx extends Format
{
	name          = "Multi-Page PCX";
	website       = "http://fileformats.archiveteam.org/wiki/DCX";
	ext           = [".dcx"];
	mimeType      = "image/x-dcx";
	magic         = ["Multipage Zsoft Paintbrush Bitmap Graphics", "DCX multi-page PCX image data", "Graphics Multipage PCX bitmap"];
	converters    = ["convert", "nconvert", `abydosconvert[format:${this.mimeType}]`]
	metaProviders = ["image"];
}
