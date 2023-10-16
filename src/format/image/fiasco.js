import {Format} from "../../Format.js";

export class fiasco extends Format
{
	name       = "Fractal Image and Sequence Codec";
	website    = "http://fileformats.archiveteam.org/wiki/FIASCO";
	ext        = [".fco"];
	magic      = ["FIASCO image/video"];
	converters = ["fiascotopnm"];
}
