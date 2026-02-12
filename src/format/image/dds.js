import {Format} from "../../Format.js";

export class dds extends Format
{
	name         = "DirectDraw Surface";
	website      = "http://fileformats.archiveteam.org/wiki/DirectDraw_Surface";
	ext          = [".dds"];
	mimeType     = "image/x-direct-draw-surface";
	magic        = ["DirectX DirectDraw Surface", "Microsoft DirectDraw Surface", "DirectDraw Surface", "image/x-dds", "piped dds sequence (dds_pipe)", /^geViewer: DDS_DDS( |$)/, /^fmt\/1040( |$)/];
	metaProvider = ["image"];
	
	
	converters = [
		
		"ffmpeg[format:dds_pipe][outType:png]",
		"gameextractor[renameOut][codes:DDS_DDS]",
		"paintDotNet",
		"noesis[type:image]",

		// convert and nconvert sometimes produce an invalid image, but convert usually does better overall than the rest and gets the abydos test image better than iconvert does
		"convert", "iconvert", "nconvert[format:dds]", "gimp"
	];
}
