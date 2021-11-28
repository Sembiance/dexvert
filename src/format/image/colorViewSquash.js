import {Format} from "../../Format.js";

export class colorViewSquash extends Format
{
	name       = "ColorViewSquash";
	website    = "http://fileformats.archiveteam.org/wiki/ColorViewSquash";
	ext        = [".rgb"];
	magic      = ["ColorViewSquash bitmap"];
	converters = ["recoil2png"];
}
