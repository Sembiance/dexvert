import {Format} from "../../Format.js";

export class xb extends Format
{
	name           = "Extended Binary";
	website        = "http://fileformats.archiveteam.org/wiki/XBIN";
	ext            = [".xb"];
	forbidExtMatch = true;
	mimeType       = "image/x-xbin";
	magic          = ["XBIN image"];
	metaProvider   = ["ansiArt"];
	converters     = ["ansilove[format:xb]", "deark", `abydosconvert[format:${this.mimeType}]`];
}
