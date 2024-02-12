import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class ybm extends Format
{
	name           = "Bennet Yee's Face Format";
	website        = "http://fileformats.archiveteam.org/wiki/YBM";
	ext            = [".bm", ".ybm"];
	forbidExtMatch = [".bm"];
	magic          = ["Bennet Yee's face format bitmap"];
	forbiddenMagic = TEXT_MAGIC;
	converters     = ["ybmtopbm[strongMatch]", "deark[module:ybm][matchType:magic][strongMatch]"];
}
