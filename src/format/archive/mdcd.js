import {Format} from "../../Format.js";

export class mdcd extends Format
{
	name       = "MDCD Archive";
	website    = "http://fileformats.archiveteam.org/wiki/MDCD";
	ext        = [".md", ".cd"];
	magic      = ["MDCD compressed archive", "MDCD archive data"];
	converters = ["deark[module:mdcd]", "mdcd"];
}
