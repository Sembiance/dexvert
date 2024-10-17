import {Format} from "../../Format.js";

export class uhbc extends Format
{
	name       = "UHBC Compressed File";
	website    = "http://fileformats.archiveteam.org/wiki/UHBC";
	magic      = ["UHBC compressed", /^UHBC archive data/];
	converters = ["uhbc"];
}
