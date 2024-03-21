import {Format} from "../../Format.js";

export class tundra extends Format
{
	name           = "TUNDRA Text-Mode Graphic";
	website        = "http://fileformats.archiveteam.org/wiki/TUNDRA";
	ext            = [".tnd"];
	forbidExtMatch = true;
	mimeType       = "text/x-tundra";
	magic          = ["TUNDRA text-mode graphics", /^fmt\/1603( |$)/];
	metaProvider   = ["ansiloveInfo"];
	converters     = ["ansilove[format:tnd]", `abydosconvert[format:${this.mimeType}]`];
}
