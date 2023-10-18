import {Format} from "../../Format.js";

export class cpShrink extends Format
{
	name       = "CP Shrink";
	website    = "http://fileformats.archiveteam.org/wiki/CP_Shrink";
	ext        = [".cpz"];
	converters = ["deark[module:cpshrink]"];
}
