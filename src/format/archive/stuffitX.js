import {Format} from "../../Format.js";

export class stuffitX extends Format
{
	name        = "Stuffit X Archive";
	website     = "http://fileformats.archiveteam.org/wiki/StuffIt_X";
	ext         = [".sitx"];
	magic       = ["StuffIt X compressed archive", /^StuffIt X$/];
	notes       = "Haven't found a linux or windows based tool that can extract these yet. Neither unar nor Stuffit Expander on windows can handle any of the sample .sitx files. Might need real stuffit expander on Mac";
	unsupported = true;
}
