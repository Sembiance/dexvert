import {Format} from "../../Format.js";

export class sit extends Format
{
	name       = "Stuffit Archive";
	website    = "http://fileformats.archiveteam.org/wiki/StuffIt";
	ext        = [".sit"];
	magic      = ["StuffIt compressed archive", "Macintosh StuffIt 5 Archive", /^StuffIt$/, /StuffIt Archive/, /^fmt\/1459|1460( |$)/];
	converters = ["unar[mac]", "deark[module:stuffit][mac]", "macunpack"];
}
