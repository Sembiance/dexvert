import {Format} from "../../Format.js";

export class dcx extends Format
{
	name         = "Multi-Page PCX";
	website      = "http://fileformats.archiveteam.org/wiki/DCX";
	ext          = [".dcx"];
	mimeType     = "image/x-dcx";
	magic        = ["Multipage Zsoft Paintbrush Bitmap Graphics", "DCX multi-page", "Graphics Multipage PCX bitmap", /^x-fmt\/348( |$)/];
	metaProvider = ["image"];
	converters   = ["convert", "deark[module:dcx] -> dexvert[asFormat:image/pcx]", "nconvert", `abydosconvert[format:${this.mimeType}]`, "hiJaakExpress", "pv[matchType:magic]"];
}
