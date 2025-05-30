import {Format} from "../../Format.js";

export class sgi extends Format
{
	name           = "Silicon Graphics Image";
	website        = "http://fileformats.archiveteam.org/wiki/SGI_(image_file_format)";
	ext            = [".sgi", ".bw", ".rgba", ".rgb"];
	mimeType       = "image/x-sgi";
	magic          = [/^Silicon Graphics.* bitmap/, "SGI image data", "piped sgi sequence (sgi_pipe)", "deark: sgiimage", /^x-fmt\/140( |$)/];
	forbiddenMagic = [/^SGI image data.*\d{5,6} x \d{5,6}/];
	idMeta         = ({macFileType}) => ["SGI ", ".SGI"].includes(macFileType);
	metaProvider   = ["image"];
	converters     = [
		"convert", "deark[module:sgiimage]", "nconvert", "iconvert", "iio2png", "gimp", "wuimg", `abydosconvert[format:${this.mimeType}]`, "ffmpeg[format:sgi_pipe][outType:png]", "imconv[format:rgb][matchType:magic]",
		"hiJaakExpress[strongMatch]", "canvas[strongMatch]", "tomsViewer[strongMatch]", "keyViewPro[strongMatch]"
	];
}
