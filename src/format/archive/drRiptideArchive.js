import {Format} from "../../Format.js";

export class drRiptideArchive extends Format
{
	name       = "Dr. Riptide Archive";
	website    = "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Dr._Riptide)";
	filename   = [/^riptide\.dat$/i];
	converters = ["gamearch"];
}
