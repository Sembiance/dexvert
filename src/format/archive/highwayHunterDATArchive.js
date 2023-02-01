import {Format} from "../../Format.js";

export class highwayHunterDATArchive extends Format
{
	name       = "Highway Hunter DAT Archive";
	website    = "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Highway_Hunter)";
	ext        = [".dat"];
	weakExt    = [".dat"];
	filename   = [/^123\.dat$/i];
	converters = ["gamearch"];
}
