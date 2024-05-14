import {Format} from "../../Format.js";

export class sgi extends Format
{
	name         = "Silicon Graphics Image";
	website      = "http://fileformats.archiveteam.org/wiki/SGI_(image_file_format)";
	ext          = [".sgi", ".bw", ".rgba", ".rgb"];
	mimeType     = "image/x-sgi";
	magic        = [/^Silicon Graphics.* bitmap/, "SGI image data", /^x-fmt\/140( |$)/];
	idMeta       = ({macFileType}) => macFileType==="SGI ";
	metaProvider = ["image"];
	converters   = ["convert", "deark[module:sgiimage]", "nconvert", "iconvert", "iio2png", "gimp", `abydosconvert[format:${this.mimeType}]`, "ffmpeg[format:sgi_pipe][outType:png]", "hiJaakExpress", "canvas", "tomsViewer", "keyViewPro"];
}
