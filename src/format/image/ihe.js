import {Format} from "../../Format.js";

export class ihe extends Format
{
	name       = "Interlace Hires Editor";
	website    = "http://fileformats.archiveteam.org/wiki/Interlace_Hires_Editor";
	ext        = [".ihe"];
	converters = ["recoil2png[format:IHE]"];
}
