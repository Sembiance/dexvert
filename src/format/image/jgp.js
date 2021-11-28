import {Format} from "../../Format.js";

export class jgp extends Format
{
	name       = "Jet Graphics Planner";
	website    = "http://fileformats.archiveteam.org/wiki/Jet_Graphics_Planner";
	ext        = [".jgp"];
	fileSize   = 2054;
	converters = ["recoil2png"];
}
