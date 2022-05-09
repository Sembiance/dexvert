import {Format} from "../../Format.js";

export class redArchive extends Format
{
	name        = "RED Archive";
	website     = "http://fileformats.archiveteam.org/wiki/RED_(Knowledge_Dynamics)";
	ext         = [".red"];
	magic       = ["RED files library"];
	unsupported = true;
}
