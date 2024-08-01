import {Format} from "../../Format.js";

export class fizArchive extends Format
{
	name        = "FIZ Archive";
	ext         = [".fiz"];
	magic       = ["FIZ archive data", "Maximus installer archive format (old)"];
	unsupported = true;
	notes       = "Could not locate any info on this archive";
}
