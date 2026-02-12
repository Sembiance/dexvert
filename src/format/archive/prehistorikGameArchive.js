import {Format} from "../../Format.js";

export class prehistorikGameArchive extends Format
{
	name           = "Prehistorik Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/CUR_Format";
	filename       = [/^files[ab]\.(cur|vga)$/i];
	converters     = ["gamearch"];
}
