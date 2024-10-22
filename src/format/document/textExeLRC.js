import {Format} from "../../Format.js";

export class textExeLRC extends Format
{
	name           = "TextExe (LRC Computing)";
	website        = "http://fileformats.archiveteam.org/wiki/TextExe_(LRC_Computing)";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["TextExe generated doc viewer"];
	unsupported    = true;
}
