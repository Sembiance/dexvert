import {Format} from "../../Format.js";

export class stuffitX extends Format
{
	name       = "Stuffit X Archive";
	website    = "http://fileformats.archiveteam.org/wiki/StuffIt_X";
	ext        = [".sitx"];
	magic      = ["StuffIt X compressed archive", /^StuffIt X$/];
	converters = ["vibeExtract"];
}
