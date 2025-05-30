import {Format} from "../../Format.js";

export class bigTIFF extends Format
{
	name           = "BigTIFF";
	website        = "http://fileformats.archiveteam.org/wiki/BigTIFF";
	ext            = [".tif", ".tiff", ".zif"];
	forbidExtMatch = true;
	magic          = ["ZoomifyImageFormat bitmap", "BigTIFF bitmap", "deark: tiff (BigTIFF)", /^Big TIFF image data/, /^fmt\/1917( |$)/];
	metaProvider   = ["image"];
	converters     = ["convert", "iio2png", "deark[module:BigTIFF]"];
}
