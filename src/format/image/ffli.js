import {Format} from "../../Format.js";

export class ffli extends Format
{
	name       = "Flickering Flexible Line Interpretation";
	website    = "http://fileformats.archiveteam.org/wiki/FFLI";
	ext        = [".ffli"];
	magic      = ["Flickering Flexible Line Interpratation bitmap"];
	converters = ["recoil2png"]
}
