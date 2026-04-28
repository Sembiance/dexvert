import {Format} from "../../Format.js";

export class pmDraw extends Format
{
	name           = "PMDraw";
	website        = "http://fileformats.archiveteam.org/wiki/PmDraw";
	ext            = [".pmd"];
	forbidExtMatch = true;
	magic          = ["PMDraw drawing/presentation"];
	converters     = ["vibe2svg[multiple]"];
}
