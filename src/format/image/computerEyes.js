import {Format} from "../../Format.js";

export class computerEyes extends Format
{
	name       = "ComputerEyes";
	website    = "http://fileformats.archiveteam.org/wiki/ComputerEyes";
	ext        = [".ce1", ".ce2", ".ce3"];
	magic      = ["ComputerEyes Raw Data Format bitmap"];
	converters = ["recoil2png"];
}
