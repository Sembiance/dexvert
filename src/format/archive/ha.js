import {Format} from "../../Format.js";

export class ha extends Format
{
	name       = "HA Archive";
	website    = "http://fileformats.archiveteam.org/wiki/HA";
	ext        = [".ha"];
	magic      = ["HA compressed archive", "HA archive data", "HA Archiv gefunden"];
	converters = ["ha"];
}
