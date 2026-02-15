import {Format} from "../../Format.js";

export class cfliDesigner extends Format
{
	name       = "CFLI Designer";
	ext        = [".cfli"];
	fileSize   = 8170;
	converters = ["recoil2png[format:CFLI]"];
}
