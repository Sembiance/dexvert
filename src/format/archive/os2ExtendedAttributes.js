import {Format} from "../../Format.js";

export class os2ExtendedAttributes extends Format
{
	name       = "OS/2 Extended Attributes";
	website    = "http://fileformats.archiveteam.org/wiki/OS/2_extended_attributes";
	magic      = ["OS/2 EA Extended file Attributes", "deark: ea_data (OS/2 extended attributes data)"];
	converters = ["deark[module:ea_data]"];
}
