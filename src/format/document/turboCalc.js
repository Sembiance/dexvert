import {Format} from "../../Format.js";

export class turboCalc extends Format
{
	name           = "TurboCalc Document";
	website        = "http://fileformats.archiveteam.org/wiki/TurboCalc";
	ext            = [".tcd"];
	forbidExtMatch = true;
	magic          = ["TurboCalc Document", /^fmt\/1585( |$)/];
	converters     = ["vibe2rtf"];
}
