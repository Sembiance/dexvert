import {Format} from "../../Format.js";

export class slowScanTelevision extends Format
{
	name       = "Slow-Scan Teleivison HRZ";
	ext        = [".hrz"];
	magic      = ["Slow Scan Television :hrz:"];
	converters = ["gimp", "nconvert[format:hrz]"];
}
