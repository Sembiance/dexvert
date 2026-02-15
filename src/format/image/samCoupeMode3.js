import {Format} from "../../Format.js";

export class samCoupeMode3 extends Format
{
	name       = "SAM Coupe Mode 3";
	ext        = [".ss3"];
	fileSize   = [24633];
	converters = ["recoil2png[format:SS3]"];
}
