import {Format} from "../../Format.js";

export class msxOPX extends Format
{
	name       = "MSX OPX Music";
	ext        = [".opx"];
	magic      = ["MSX OPX Music file"];
	converters = ["kss2wav"];
}
