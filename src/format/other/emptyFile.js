import {Format} from "../../Format.js";

export class emptyFile extends Format
{
	name            = "Empty File";
	magic           = [/^empty$/];
	untouched       = true;
	transformUnsafe = true;	// Don't allow transformed files to be counted for this 'catch all' type format
}
