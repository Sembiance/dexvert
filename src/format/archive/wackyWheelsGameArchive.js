import {Format} from "../../Format.js";

export class wackyWheelsGameArchive extends Format
{
	name           = "Wacky Wheels Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Wacky_Wheels)";
	ext            = [".dat", ".lid"];
	forbidExtMatch = true;
	filename       = [/^wacky\.(dat|lid)$/i];
	magic          = [/^Wacky Wheels Archive$/, /^geArchive: DAT_3( |$)/];
	converters     = ["gameextractor[codes:DAT_3]", "gamearch"];
}
