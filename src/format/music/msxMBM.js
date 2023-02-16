import {Format} from "../../Format.js";

export class msxMBM extends Format
{
	name       = "MSX Moon Blaster Music";
	ext        = [".mbm"];
	converters = ["kss2wav"];
}
