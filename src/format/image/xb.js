import {Format} from "../../Format.js";

export class xb extends Format
{
	name           = "Extended Binary";
	website        = "http://fileformats.archiveteam.org/wiki/XBIN";
	ext            = [".xb"];
	forbidExtMatch = true;
	mimeType       = "image/x-xbin";
	magic          = ["XBIN image", /^fmt\/1612( |$)/];
	metaProvider   = ["ansiArt"];
	converters     = ["ansilove[format:xb]", "deark[module:xbin]", `abydosconvert[format:${this.mimeType}]`];
}
