import {Format} from "../../Format.js";

export class authorware extends Format
{
	name    = "Authorware Application/Package";
	website = "http://fileformats.archiveteam.org/wiki/Authorware";
	ext     = [
		".app", ".apr",
		".apw", ".asw", ".aas",
		".a3w", ".a3m",
		".a4p", ".a4r",
		".a5p", ".a5r",
		".a6p", ".a6r",
		".a7p", ".a7r"
	];
	magic      = ["Authorware Application", "Unpackaged Authorware 3 for Windows file", "Authorware Packaged file", "Authorware APR Archive", "Authorware Archive"];
	converters = ["unauthorware"];
}
