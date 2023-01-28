import {Format} from "../../Format.js";

export class cosmoVolumeFile extends Format
{
	name       = "Cosmo Volume File";
	website    = "https://moddingwiki.shikadi.net/wiki/CMP_Format";
	filename   = [/^nukem2\.cmp$/i, /^volume\d[ab]\.ms\d$/i];
	converters = ["gamearch"];
}
