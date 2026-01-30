import {Format} from "../../Format.js";

export class pbm extends Format
{
	name         = "Portable Bitmap";
	website      = "http://fileformats.archiveteam.org/wiki/Netpbm_formats";
	ext          = [".pbm", ".pnm"];
	mimeType     = "image/x-portable-bitmap";
	magic        = ["Portable BitMap", "Portable Bitmap Image", "image/x-portable-bitmap", "piped pbm sequence (pbm_pipe)", /^Netpbm image data,? .*bitmap/, /^fmt\/409( |$)/, /^x-fmt\/164( |$)/];
	metaProvider = ["image"];
	converters   = [
		"convert", "iio2png", "gimp", "wuimg[format:pnm]", "imconv[format:pbm][matchType:magic]",
		"paintDotNet[matchType:magic]", "hiJaakExpress[matchType:magic]", "canvas[matchType:magic]", "tomsViewer[matchType:magic]"
	];
}
