import {Format} from "../../Format.js";

export class stargunnerDLT extends Format
{
	name       = "Stargunner DLT Archive";
	website    = "https://moddingwiki.shikadi.net/wiki/DLT_Format";
	filename   = [/^stargun\.dlt$/i];
	magic      = ["DLT game data archive"];
	converters = ["gamearch"];
}
