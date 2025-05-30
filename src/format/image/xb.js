import {Format} from "../../Format.js";

export class xb extends Format
{
	name           = "Extended Binary";
	website        = "http://fileformats.archiveteam.org/wiki/XBIN";
	ext            = [".xb"];
	forbidExtMatch = true;
	mimeType       = "image/x-xbin";
	magic          = ["XBIN image", "eXtended BINary text (XBIN) (xbin)", "deark: xbin", /^fmt\/1612( |$)/];
	metaProvider   = ["ansiloveInfo"];
	converters     = ["ansilove[format:xb]", "deark[module:xbin]", `abydosconvert[format:${this.mimeType}]`];
}
