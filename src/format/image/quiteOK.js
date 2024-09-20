import {Format} from "../../Format.js";

export class quiteOK extends Format
{
	name         = "Quite OK Image Format";
	website      = "http://fileformats.archiveteam.org/wiki/Quite_OK_Image_Format";
	ext          = [".qoi"];
	magic        = ["Quite OK Image Format bitmap", "image/qoi", /^QOI image data/];
	metaProvider = ["image"];
	converters   = ["convert", "wuimg", "ffmpeg[format:qoi_pipe][outType:png]"];
}
