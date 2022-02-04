import {Format} from "../../Format.js";

export class nullBytesAlternating extends Format
{
	name       = "Null Bytes Alternating";
	magic      = [/^Null Bytes Alternating$/];
	idCheck    = inputFile => inputFile.size>=16;	// Files 8 bytes or smaller are not worth matching
	priority   = this.PRIORITY.LOW;
	converters = ["stripGarbage[null]"];
}
