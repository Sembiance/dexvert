import {Format} from "../../Format.js";

export class packIt extends Format
{
	name       = "PackIt Archive";
	website    = "http://fileformats.archiveteam.org/wiki/PackIt";
	ext        = [".pit"];
	magic      = ["PackIt compressed archive", "PMWLite", /^PackIt$/];
	converters = ["unar", "macunpack"];
}
