import {Format} from "../../Format.js";

export class icdrawIcon extends Format
{
	name       = "ICDRAW Icon";
	website    = "http://fileformats.archiveteam.org/wiki/ICDRAW_icon";
	ext        = [".ib3", ".ibi"];
	magic      = ["ICDRAW group icon bitmap", "ICDRAW single icon bitmap"];
	converters = ["recoil2png"];
}
