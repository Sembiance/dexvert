import {Format} from "../../Format.js";

export class gem extends Format
{
	name     = "GEM Raster Bitmap";
	website  = "http://fileformats.archiveteam.org/wiki/GEM_Raster";
	ext      = [".img", ".ximg", ".timg"];
	mimeType = "image/x-gem";
	magic    = [
		"GEM bitmap", "GEM HYPERPAINT Image data", "GEM Image data", "Extended GEM bitmap", "Digital Research GEM VDI bitmap", "piped gem sequence (gem_pipe)", /^GEM .{4} Image data/, "deark: gemraster", "GEM Paint :gem:",
		/^fmt\/1657( |$)/, /^x-fmt\/159( |$)/
	];
	converters = [
		// ffmpeg handles everything the best, like teststtt.img and COLUMNS4.IMG
		"ffmpeg[format:gem_pipe][outType:png]",

		// Recoil does second bes
		"recoil2png[matchType:magic]", "deark[module:gemras]"
		
		// Abydos and nconvert handle the color in flag_b24 and tru256 (nconvert messes up some other images colorspaces (as usual for nconvert))
		//`abydosconvert[format:${this.mimeType}]`, "nconvert[format:gem]",
		//"canvas5[strongMatch][matchType:magic][hasExtMatch]", "hiJaakExpress[strongMatch]", "pv[strongMatch]", "corelPhotoPaint[strongMatch]"
	];
}
