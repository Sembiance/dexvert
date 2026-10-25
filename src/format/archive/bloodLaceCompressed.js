import {Format} from "../../Format.js";

export class bloodLaceCompressed extends Format
{
	name       = "Blood & Lace Compressed";
	magic      = ["GMM Entertainment JFX1 compressed data", /^Blood & Lace Compressed$/, "deark: jfx1"];
	packed     = true;
	converters = ["deark[module:jfx1]", "bl_unpack"];
}
