import {Format} from "../../Format.js";

export class nullBytes extends Format
{
	name      = "All Null Bytes";
	magic     = [/^All Null Bytes$/];	// WARNING: Do not add a magic match for 'null bytes' from trid, it only checks the first X bytes for zeroes. So NOT trustworthy
	untouched = true;
}
