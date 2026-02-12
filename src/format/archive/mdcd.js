import {Format} from "../../Format.js";

export class mdcd extends Format
{
	name       = "MDCD Archive";
	website    = "http://fileformats.archiveteam.org/wiki/MDCD";
	ext        = [".md", ".cd"];
	magic      = ["MDCD compressed archive", "MDCD archive data", "Archive: MDCD", "deark: mdcd", /^geArchive: CRS_MDMD( |$)/];
	converters = ["deark[module:mdcd]", "mdcd", "gameextractor[codes:CRS_MDMD]"];
}
