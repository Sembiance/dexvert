import {Format} from "../../Format.js";

export class os2Pointer extends Format
{
	name       = "OS/2 Pointer";
	website    = "http://fileformats.archiveteam.org/wiki/OS/2_Pointer";
	ext        = [".ptr"];
	magic      = ["OS/2 Pointer", /^OS\/2 [12].x color pointer/];
	converters = ["deark"];
}
