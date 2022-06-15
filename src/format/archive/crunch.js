import {Format} from "../../Format.js";

export class crunch extends Format
{
	name       = "Crunch Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Crunch";
	magic      = ["Crunch compressed archive", "crunched data"];
	converters = ["unar", "lbrate"];
}
