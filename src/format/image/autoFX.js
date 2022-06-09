import {Format} from "../../Format.js";

export class autoFX extends Format
{
	name       = "Auto/FX Image";
	ext        = [".afx"];
	magic      = ["Auto/FX Image"];
	converters = ["nconvert"];
}
