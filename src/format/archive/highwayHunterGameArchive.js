import {Format} from "../../Format.js";

export class highwayHunterGameArchive extends Format
{
	name           = "Highway Hunter Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Highway_Hunter)";
	ext            = [".dat"];
	forbidExtMatch = true;
	filename       = [/^123\.dat$/i];
	converters     = ["gamearch"];
}
