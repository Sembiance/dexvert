import {Format} from "../../Format.js";

export class x3f extends Format
{
	name         = "Sigma/Foveon X3F";
	website      = "http://fileformats.archiveteam.org/wiki/X3F";
	ext          = [".x3f"];
	magic        = ["Sigma RAW Image", "Foveon X3F raw image data", "Sigma - Foveon X3 raw picture", "image/x-sigma-x3f", /^fmt\/661( |$)/];
	mimeType     = "image/x-sigma-x3f";
	metaProvider = ["image"];
	converters   = ["dcraw", "convert", `abydosconvert[format:${this.mimeType}]`];
}
