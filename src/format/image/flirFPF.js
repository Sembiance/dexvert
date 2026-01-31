import {Format} from "../../Format.js";

export class flirFPF extends Format
{
	name       = "FLIR Public Format";
	website    = "http://fileformats.archiveteam.org/wiki/FPF_(FLIR)";
	ext        = [".fpf"];
	magic      = ["FLIR Public Format bitmap"];
	converters = ["tkimgConvert"];
}
