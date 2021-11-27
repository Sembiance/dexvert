import {Format} from "../../Format.js";

export class him extends Format
{
	name       = "Hires Manager";
	website    = "http://fileformats.archiveteam.org/wiki/Hires_Manager";
	ext        = [".him"];
	byteCheck  = [{offset : 0, match : [0x00, 0x40]}];
	converters = ["recoil2png", "view64"];
}
