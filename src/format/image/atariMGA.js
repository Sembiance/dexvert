import {Format} from "../../Format.js";

export class atariMGA extends Format
{
	name       = "Atari MGA";
	ext        = [".mga"];
	converters = ["recoil2png[format:MGA]"];
}
