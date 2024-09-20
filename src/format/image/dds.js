import {Format} from "../../Format.js";

export class dds extends Format
{
	name         = "DirectDraw Surface";
	website      = "http://fileformats.archiveteam.org/wiki/DirectDraw_Surface";
	ext          = [".dds"];
	mimeType     = "image/x-direct-draw-surface";
	magic        = ["DirectX DirectDraw Surface", "Microsoft DirectDraw Surface", "DirectDraw Surface", "image/x-dds", /^fmt\/1040( |$)/];
	metaProvider = ["image"];
	
	// paintDotNet does the best with all samples I have. convert and nconvert sometimes produce an invalid image, but convert usually does better overall than the rest and gets the abydos test image better than iconvert does
	converters = ["paintDotNet", "convert", "iconvert", "nconvert", "gimp"];
}
