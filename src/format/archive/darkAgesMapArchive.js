import {Format} from "../../Format.js";

export class darkAgesMapArchive extends Format
{
	name       = "Dark Ages Map Archive";
	website    = "https://moddingwiki.shikadi.net/wiki/Dark_Ages_Map_Format";
	filename   = [/^file05\.da\d$/i];
	converters = ["gamearch"];
}
