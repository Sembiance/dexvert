import {Format} from "../../Format.js";

export class dcx extends Format
{
	name         = "Multi-Page PCX";
	website      = "http://fileformats.archiveteam.org/wiki/DCX";
	ext          = [".dcx"];
	mimeType     = "image/x-dcx";
	magic        = ["Multipage Zsoft Paintbrush Bitmap Graphics", "DCX multi-page", "Graphics Multipage PCX bitmap", "deark: dcx", "Zsoft Paintbrush :dcx:", /^x-fmt\/348( |$)/];
	metaProvider = ["image"];
	converters   = ["wuimg[matchType:magic]", "iio2png", "convert", "deark[module:dcx] -> dexvert[asFormat:image/pcx]", "nconvert[format:dcx]", `abydosconvert[format:${this.mimeType}]`, "canvas5", "hiJaakExpress", "pv[matchType:magic]"];
}
