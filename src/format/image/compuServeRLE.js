import {Format} from "../../Format.js";

export class compuServeRLE extends Format
{
	name       = "CompuServe RLE";
	website    = "http://fileformats.archiveteam.org/wiki/CompuServe_RLE";
	ext        = [".rle"];
	magic      = ["CompuServe RLE bitmap", /^fmt\/1538( |$)/];
	notes      = "RRCP1.RLE isn't able to be converted by recoil2png and cistopbm handles it better, but still a bit corrupted.";
	converters = ["recoil2png", "deark[module:cserve_rle]", "cistopbm"];
}
