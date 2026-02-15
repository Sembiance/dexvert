import {Format} from "../../Format.js";

export class hiresEditor extends Format
{
	name       = "Hires-Editor";
	ext        = [".het"];
	converters = ["recoil2png[format:HET]"];
}
