import {Format} from "../../Format.js";

export class emf extends Format
{
	name         = "Microsoft Windows Enhanced Metafile";
	website      = "http://fileformats.archiveteam.org/wiki/EMF";
	ext          = [".emf"];
	mimeType     = "image/emf";
	magic        = ["Windows Enhanced Metafile", "Microsoft Windows Enhanced Metafile"];
	metaProvider = ["image"];
	converters   = ["deark", "convert", `abydosconvert[format:${this.mimeType}]`, "irfanView", "hiJaakExpress", "canvas[matchType:magic][nonRaster]"];
}
