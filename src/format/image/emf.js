import {Format} from "../../Format.js";

export class emf extends Format
{
	name         = "Microsoft Windows Enhanced Metafile";
	website      = "http://fileformats.archiveteam.org/wiki/Enhanced_Metafile";
	ext          = [".emf"];
	mimeType     = "image/emf";
	magic        = ["Windows Enhanced Metafile", "Microsoft Windows Enhanced Metafile", "image/emf", /^fmt\/(344|345)( |$)/, /^x-fmt\/153( |$)/];
	metaProvider = ["image"];
	converters   = [
		"deark[module:emf]", "convert[format:emf][matchType:magic]", `abydosconvert[format:${this.mimeType}]`,
		...["irfanView", "photoDraw", "hiJaakExpress", "canvas[nonRaster]"].map(v => `${v}[matchType:magic]`)
	];
}
