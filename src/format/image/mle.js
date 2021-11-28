import {Format} from "../../Format.js";

export class mle extends Format
{
	name       = "Multi-Lace Editor";
	website    = "http://fileformats.archiveteam.org/wiki/Multi-Lace_Editor";
	ext        = [".mle"];
	converters = ["recoil2png"];
}
