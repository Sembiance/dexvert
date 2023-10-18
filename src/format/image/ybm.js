import {Format} from "../../Format.js";

export class ybm extends Format
{
	name       = "Bennet Yee's Face Format";
	website    = "http://fileformats.archiveteam.org/wiki/YBM";
	ext        = [".bm", ".ybm"];
	magic      = ["Bennet Yee's face format bitmap"];
	converters = ["ybmtopbm", "deark[module:ybm]"];
}
