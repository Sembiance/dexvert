import {Format} from "../../Format.js";

export class lifArchive extends Format
{
	name        = "LIF Archive";
	website     = "http://fileformats.archiveteam.org/wiki/LIF_(Knowledge_Dynamics)";
	ext         = [".lif"];
	magic       = ["LIF installer-archive format"];
	unsupported = true;
}
