import {Format} from "../../Format.js";

export class electronikaBKPIC extends Format
{
	name       = "Electronika BK PIC";
	ext        = [".pic"];
	fileSize   = 16384;
	converters = ["recoil2png[format:PIC]"];
}
