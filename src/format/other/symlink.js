import {Format} from "../../Format.js";

export class symlink extends Format
{
	name        = "symlink";
	unsupported = true;
	notes       = "This format is a hardcoded match at the beginning of identify.js";
}
