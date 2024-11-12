import {Format} from "../../Format.js";

export class bigTIFF extends Format
{
	name           = "BigTIFF";
	website        = "http://fileformats.archiveteam.org/wiki/BigTIFF";
	ext            = [".tif", ".tiff"];
	forbidExtMatch = true;
	magic          = [/^Big TIFF image data/, /^fmt\/1917( |$)/];
	metaProvider   = ["image"];
	converters     = ["convert", "iio2png", "deark[module:BigTIFF]"];
}
