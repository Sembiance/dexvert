import {Format} from "../../Format.js";

export class fvl0 extends Format
{
	name       = "FVL0 Compressed";
	magic      = ["FVL0: ANC Cruncher"];
	packed     = true;
	converters = ["ancient"];
}
