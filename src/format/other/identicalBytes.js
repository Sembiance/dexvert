import {Format} from "../../Format.js";

export class identicalBytes extends Format
{
	name            = "All Identical Bytes";
	magic           = [/^All Identical Bytes$/];
	untouched       = true;
	priority        = this.PRIORITY.LOW;
	transformUnsafe = true;	// Don't allow transformed files to be counted for this 'catch all' type format
}
