import {Format} from "../../Format.js";

export class bbcDisplayRAM extends Format
{
	name        = "BBC Display RAM Dump";
	fileSize    = 1000;
	mimeType    = "image/x-bbc-micro-screendump";
	unsupported = true;	// no extension, no magic, near impossibly to detect as it's just a 1,000 byte display RAM dump that happesn to be from a BBC
	converters  = [`abydosconvert[format:${this.mimeType}]`];
}
