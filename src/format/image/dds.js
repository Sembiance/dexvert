import {Format} from "../../Format.js";

export class dds extends Format
{
	name          = "DirectDraw Surface";
	website       = "http://fileformats.archiveteam.org/wiki/DDS";
	ext           = [".dds"];
	mimeType      = "image/x-direct-draw-surface";
	magic         = ["DirectX DirectDraw Surface", "Microsoft DirectDraw Surface", "DirectDraw Surface"];
	
	// Both convert and nconvert sometimes produce an invalid image, but convert usually does better overall
	converters    = ["convert", "nconvert"]
	metaProviders = ["image"];
}
