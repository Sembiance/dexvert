import {Format} from "../../Format.js";

export class sit extends Format
{
	name       = "Stuffit Archive";
	website    = "http://fileformats.archiveteam.org/wiki/SIT";
	ext        = [".sit"];
	magic      = ["StuffIt compressed archive", /StuffIt Archive/, /^fmt\/1459|1460( |$)/];
	converters = ["unar[mac]", "UniExtract"];
}
