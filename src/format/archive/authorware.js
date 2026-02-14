import {Format} from "../../Format.js";

export class authorware extends Format
{
	name       = "Authorware Application/Package";
	website    = "http://fileformats.archiveteam.org/wiki/Authorware";
	ext        = [".app", ".apw", ".a4p", ".a5p"];
	magic      = ["Authorware Application", "Unpackaged Authorware 3 for Windows file", "Authorware Packaged file"];
	converters = ["unauthorware"];
}
