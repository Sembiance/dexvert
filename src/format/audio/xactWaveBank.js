import {Format} from "../../Format.js";

export class xactWaveBank extends Format
{
	name       = "XACT Wave Bank";
	ext        = [".xwb"];
	magic      = ["XACT Wave Bank", "Format: Microsoft XACT Wave Bank", "XWB (Microsoft Wave Bank) (xwb)"];
	converters = ["zxtune123"];
}
