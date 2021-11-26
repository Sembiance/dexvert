import {Format} from "../../Format.js";

export class din extends Format
{
	name       = "DIN";
	website    = "http://fileformats.archiveteam.org/wiki/DIN";
	ext        = [".din"];
	converters = ["recoil2png"]
}
