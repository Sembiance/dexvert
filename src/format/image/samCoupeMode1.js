import {Format} from "../../Format.js";

export class samCoupeMode1 extends Format
{
	name       = "SAM Coupe Mode 1";
	ext        = [".ss1"];
	fileSize   = [7461];
	converters = ["recoil2png[format:SS1]"];
}
