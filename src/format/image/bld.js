import {Format} from "../../Format.js";

export class bld extends Format
{
	name       = "MegaPaint BLD";
	website    = "http://fileformats.archiveteam.org/wiki/MegaPaint_BLD";
	ext        = [".bld"];
	converters = ["recoil2png"];
}
