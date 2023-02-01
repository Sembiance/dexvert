import {Format} from "../../Format.js";

export class prehistorikCURArchive extends Format
{
	name       = "Prehistorik CUR Archive";
	website    = "https://moddingwiki.shikadi.net/wiki/CUR_Format";
	filename   = [/^files[ab]\.(cur|vga)$/i];
	converters = ["gamearch"];
}
