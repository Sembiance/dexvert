import {Format} from "../../Format.js";

export class stellar7GameArchive extends Format
{
	name           = "Stellar 7 Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/RES_Format_(Stellar_7)";
	ext            = [".res"];
	forbidExtMatch = true;
	filename       = [/^(stellar|cockpit|draxon|voice|stelart|scenex|level\d+)\.res$/i];
	converters     = ["gamearch"];
}
