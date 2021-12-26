import {Format} from "../../Format.js";

export class identicalBytes extends Format
{
	name      = "All Identical Bytes";
	magic     = [/^All Identical Bytes$/];
	idCheck   = inputFile => inputFile.size>8;	// Files 8 bytes or smaller are not worth matching
	untouched = true;
	priority  = this.PRIORITY.LOW;
}
