import {Format} from "../../Format.js";

export class ldm extends Format
{
	name       = "Ludek Maker";
	website    = "http://fileformats.archiveteam.org/wiki/Ludek_Maker";
	ext        = [".ldm"];
	magic      = ["Ludek Maker bitmap"];
	converters = ["recoil2png"]
}
