import {Format} from "../../Format.js";

export class emf extends Format
{
	name         = "Microsoft Windows Enhanced Metafile";
	website      = "http://fileformats.archiveteam.org/wiki/Enhanced_Metafile";
	ext          = [".emf"];
	mimeType     = "image/emf";
	magic        = ["Windows Enhanced Metafile", "Microsoft Windows Enhanced Metafile", /^fmt\/(344|345)( |$)/, /^x-fmt\/153( |$)/];
	metaProvider = ["image"];
	converters   = ["deark[module:emf]", "convert", `abydosconvert[format:${this.mimeType}]`, "irfanView", "photoDraw", "hiJaakExpress", "canvas[matchType:magic][nonRaster]"];
}
