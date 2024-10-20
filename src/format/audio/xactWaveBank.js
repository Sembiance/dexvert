import {Format} from "../../Format.js";

export class xactWaveBank extends Format
{
	name       = "XACT Wave Bank";
	ext        = [".xwb"];
	magic      = ["XACT Wave Bank"];
	converters = ["zxtune123"];
}
