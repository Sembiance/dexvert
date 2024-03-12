import {Format} from "../../Format.js";

export class ravenObjectFileFormat extends Format
{
	name        = "Raven Object File Format";
	website     = "http://fileformats.archiveteam.org/wiki/ROFF";
	ext         = [".rof"];
	magic       = ["ROFF 3D animation"];
	unsupported = true;
}
