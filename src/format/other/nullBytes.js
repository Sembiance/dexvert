import {Format} from "../../Format.js";

const _NULL_BYTES_MAGIC = [/^All Null Bytes$/];	// WARNING: Do not add a magic match for 'null bytes' from trid, it only checks the first X bytes for zeroes. So NOT trustworthy
export {_NULL_BYTES_MAGIC};

export class nullBytes extends Format
{
	name      = "All Null Bytes";
	magic     = _NULL_BYTES_MAGIC;
	untouched = true;
}
