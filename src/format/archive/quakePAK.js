import {Format} from "../../Format.js";

export class quakePAK extends Format
{
	name       = "Quake PAK";
	website    = "http://fileformats.archiveteam.org/wiki/Quake_PAK";
	ext        = [".pak"];
	magic      = ["Quake archive", "Quake I or II world or extension"];
	converters = ["gameextractor"];
}
