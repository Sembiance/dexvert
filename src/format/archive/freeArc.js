import {Format} from "../../Format.js";

export class freeArc extends Format
{
	name        = "FreeArc Archive";
	website     = "http://fileformats.archiveteam.org/wiki/ARC_(FreeArc)";
	ext         = [".arc"];
	magic       = ["FreeArc archive", "FreeArc compressed archive", /^fmt\/1096( |$)/];
	unsupported = true;
	notes       = "I have the bz2 linux source code, but I don't trust it to be free of malware, so haven't compiled it. Pretty rare format I imagine and it didn't really exist until 2010, so not important to support at this time.";
}
