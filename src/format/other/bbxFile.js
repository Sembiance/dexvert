import {Format} from "../../Format.js";

export class bbxFile extends Format
{
	name       = "bbX File";
	magic      = ["BBx "];
	converters = ["strings"];
}
