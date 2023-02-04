import {Format} from "../../Format.js";

export class msxMBM extends Format
{
	name       = "MSX MBM Music";
	ext        = [".mbm"];
	converters = ["kss2wav"];
}
