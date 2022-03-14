import {Format} from "../../Format.js";

export class nullBytesAlternating extends Format
{
	name       = "Null Bytes Alternating";
	magic      = [/^Null Bytes Alternating$/];
	idCheck    = inputFile => inputFile.size>=16;	// Files less than 16 bytes are not worth matching
	priority   = this.PRIORITY.LOW;
	converters = ["stripGarbage[null]"];
}
