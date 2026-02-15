import {Format} from "../../Format.js";

export class f80 extends Format
{
	name       = "The Last Word Font";
	ext        = [".f80"];
	converters = ["recoil2png[format:F80]"];
}
