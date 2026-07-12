import {xu} from "xu";
import {Format} from "../../Format.js";

export class realTimeFile extends Format
{
	name       = "CD-i Real Time File";
	ext        = [".rtf"];
	converters = ["vibeExtract"];
}
