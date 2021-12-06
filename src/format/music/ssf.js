import {Format} from "../../Format.js";

export class ssf extends Format
{
	name         = "Saturn Sound Format";
	website      = "http://fileformats.archiveteam.org/wiki/SSF";
	ext          = [".ssf", ".minissf", ".ssflib"];
	magic        = ["SSF Saturn Sound Format rip"];
	notes        = "Minissf files don't convert, not sure why yet.";
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
