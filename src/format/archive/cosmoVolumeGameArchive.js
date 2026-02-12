import {Format} from "../../Format.js";

export class cosmoVolumeGameArchive extends Format
{
	name           = "Cosmo Volume Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/CMP_Format";
	filename       = [/^nukem2\.cmp$/i, /^volume\d[ab]\.ms\d$/i];
	magic          = ["Build Engine RFF encrypted container", /^geArchive: CMP( |$)/];
	converters     = ["gameextractor[codes:CMP]", "gamearch"];
}
