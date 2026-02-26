import {Format} from "../../Format.js";

export class os2FTCOMP extends Format
{
	name       = "OS/2 FTCOMP Archive";
	website    = "http://fileformats.archiveteam.org/wiki/FTCOMP";
	magic      = ["FTCOMP compressed archive", "Archive: FTCOMP"];
	converters = ["unpack2_translated"];
	unsupported = true;	// todo WIP
}
