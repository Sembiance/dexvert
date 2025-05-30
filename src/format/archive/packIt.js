import {Format} from "../../Format.js";

export class packIt extends Format
{
	name       = "PackIt Archive";
	website    = "http://fileformats.archiveteam.org/wiki/PackIt";
	ext        = [".pit"];
	magic      = ["PackIt compressed archive", "PMWLite", /^PackIt$/, "deark: packit"];
	idMeta     = ({macFileType}) => macFileType==="PIT ";
	converters = ["unar", "macunpack", "deark[module:packit]"];
}
