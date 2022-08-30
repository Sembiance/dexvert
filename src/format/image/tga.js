import {Format} from "../../Format.js";

export class tga extends Format
{
	name         = "Truevision Targa Graphic";
	website      = "http://fileformats.archiveteam.org/wiki/TGA";
	ext          = [".tga", ".targa", ".tpic", ".icb", ".vda", ".vst"];
	mimeType     = "image/x-tga";
	magic        = ["Truevision TGA", "Targa image data", /^fmt\/402( |$)/, /^x-fmt\/367( |$)/];
	metaProvider = ["image"];
	
	// ImageMagick sometimes doesn't detect that a TGA image has been rotated. These other converters seem to do a better job at that
	// Only deark, corelDRAW & pv were able to correctly handle flag_b32.tga
	// picturePublisher also supports TGA but bad TGA's have a tendency to cause the program to freeze so bad that the AutoIt script freezes up too (see sandbox/samples/HangsPicturePublisher.tga)
	converters = ["deark", "corelDRAW", "pv[matchType:magic]", "nconvert", "recoil2png", `abydosconvert[format:${this.mimeType}]`, "gimp", "hiJaakExpress", "corelPhotoPaint", "canvas"];

	// Often files are confused as TGA and it results in just a single solid image. Since TGA's don't appear to have transparecy, require more than 1 color
	verify = ({meta}) => meta.colorCount>1;
}
