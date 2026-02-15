import {Format} from "../../Format.js";

export class apl extends Format
{
	name       = "Atari Player Editor";
	ext        = [".apl"];
	converters = ["recoil2png[format:APL]"];
}
