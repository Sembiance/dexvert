import {Format} from "../../Format.js";

export class flf extends Format
{
	name       = "Turbo Rascal Syntax Error";
	website    = "http://fileformats.archiveteam.org/wiki/Turbo_Rascal_Syntax_Error";
	ext        = [".flf"];
	magic      = ["Turbo Rascal Syntax Error"];
	converters = ["recoil2png[format:FLF]"];
}
