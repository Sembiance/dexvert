import {Format} from "../../Format.js";

export class dds extends Format
{
	name         = "DirectDraw Surface";
	website      = "http://fileformats.archiveteam.org/wiki/DirectDraw_Surface";
	ext          = [".dds"];
	mimeType     = "image/x-direct-draw-surface";
	magic        = ["DirectX DirectDraw Surface", "Microsoft DirectDraw Surface", "DirectDraw Surface", /^fmt\/1040( |$)/];
	metaProvider = ["image"];
	
	// Both convert and nconvert sometimes produce an invalid image, but convert usually does better overall and gets the abydos test image better than iconvert does
	converters = ["convert", "iconvert", "nconvert", "gimp"];
}
