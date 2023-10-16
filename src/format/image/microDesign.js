import {Format} from "../../Format.js";

export class microDesign extends Format
{
	name       = "MicroDesign";
	website    = "http://fileformats.archiveteam.org/wiki/MDA";
	ext        = [".mda", ".mdp"];
	magic      = ["MicroDesign data", "MicroDesign Area bitmap"];
	converters = ["mdatopbm"];
}
