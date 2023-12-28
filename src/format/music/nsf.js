import {Format} from "../../Format.js";

export class nsf extends Format
{
	name         = "NES Sound File";
	website      = "http://fileformats.archiveteam.org/wiki/NES_Sound_Format";
	ext          = [".nsf"];
	magic        = ["NES Sound File", "NES Sound Format rip"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123[largeQuota]"];
}
