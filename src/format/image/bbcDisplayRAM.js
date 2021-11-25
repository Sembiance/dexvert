import {Format} from "../../Format.js";

export class bbcDisplayRAM extends Format
{
	name        = "BBC Display RAM Dump";
	fileSize    = 1000;
	mimeType    = "image/x-bbc-micro-screendump";
	unsupported = true;
	notes       = "While supported by abydos, due to no extension and no magic, it's impossible to detect accurately.";
	converters  = [`abydosconvert[format:${this.mimeType}]`];
}
