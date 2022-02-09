import {xu} from "xu";
import {Format} from "../../Format.js";

export class iffFantavision extends Format
{
	name       = "IFF Fantavision";
	magic      = ["IFF data, Fantavision animation", "Fantavision animation"];
	notes      = "Don't have support to convert this to a movie yet, so classify it as an archive and just extract what we can from it.";
	converters = ["iff_convert[keepAll]"];
}

