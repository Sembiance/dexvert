import {Format} from "../../Format.js";

export class stargunnerGameArchive extends Format
{
	name           = "Stargunner Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/DLT_Format";
	filename       = [/^stargun\.dlt$/i];
	magic          = ["DLT game data archive", /^geArchive: TBD( |$)/];
	converters     = ["gamearch"];
}
