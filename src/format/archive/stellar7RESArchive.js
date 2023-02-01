import {Format} from "../../Format.js";

export class stellar7RESArchive extends Format
{
	name           = "Stellar 7 RES Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/RES_Format_(Stellar_7)";
	ext            = [".res"];
	forbidExtMatch = true;
	filename       = [/^(stellar|cockpit|draxon|voice|stelart|scenex|level\d+)\.res$/i];
	converters     = ["gamearch"];
}
