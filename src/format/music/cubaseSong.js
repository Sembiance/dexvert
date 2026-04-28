import {Format} from "../../Format.js";

export class cubaseSong extends Format
{
	name        = "Cubase Song";
	website     = "http://fileformats.archiveteam.org/wiki/ALL";
	ext         = [".all"];
	magic       = ["Cubase song"];
	unsupported = true;	// only 248 unique files on discmaster, and might be a bit too difficult to convert
}
